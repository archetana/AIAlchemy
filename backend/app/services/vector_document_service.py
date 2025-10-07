"""
Vector Document Service
Handles document extraction, embedding generation, and semantic search
Uses Supabase + pgvector for vector operations
"""

import os
import hashlib
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.supabase_client import get_supabase_client
from app.core.config import get_settings
from app.services.model_agnostic_service import model_service, EmbeddingModel
import logging

logger = logging.getLogger(__name__)

class VectorDocumentService:
    """Service for managing document vectors and semantic search"""
    
    def __init__(self):
        self.settings = get_settings()
        self.supabase = get_supabase_client()
        self.model_service = model_service
    
    async def generate_embedding(
        self, 
        text: str, 
        model: Optional[EmbeddingModel] = None,
        dimensions: Optional[int] = None
    ) -> Tuple[List[float], Dict[str, Any]]:
        """Generate embeddings using model-agnostic service"""
        try:
            embedding, metadata = await self.model_service.generate_embedding(
                text=text,
                model=model,
                dimensions=dimensions
            )
            return embedding, metadata
                
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Fallback to simple embedding
            fallback_embedding = self._generate_fallback_embedding(text, dimensions or 1536)
            fallback_metadata = {
                "model": "fallback",
                "provider": "local",
                "dimensions": len(fallback_embedding),
                "cost_usd": 0.0,
                "processing_time_seconds": 0.0,
                "text_length": len(text),
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
            return fallback_embedding, fallback_metadata
    
    def _generate_fallback_embedding(self, text: str, dimensions: int = 1536) -> List[float]:
        """Generate a deterministic fallback embedding for development"""
        # Use the model service's fallback method
        return self.model_service._generate_fallback_embedding(text, dimensions)
    
    def _clean_text_for_embedding(self, raw_text: str) -> str:
        """Clean and prepare text for embedding generation"""
        # Remove excessive whitespace
        cleaned = ' '.join(raw_text.split())
        
        # Remove special characters but keep important punctuation
        import re
        cleaned = re.sub(r'[^\w\s\.\,\!\?\-]', '', cleaned)
        
        # Truncate to reasonable length (avoid token limits)
        max_length = 8000  # Roughly 2000 tokens
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
        
        return cleaned.lower().strip()
    
    async def store_document_vector(
        self,
        startup_id: int,
        document_type: str,
        filename: str,
        raw_text: str,
        structured_data: Dict[str, Any],
        extraction_service: str,
        extraction_confidence: Optional[float] = None,
        file_url: Optional[str] = None,
        content_categories: Optional[List[str]] = None,
        key_entities: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store document with vector embedding"""
        
        # Clean text for embedding
        cleaned_text = self._clean_text_for_embedding(raw_text)
        
        # Generate embedding using model-agnostic service
        embedding, embedding_metadata = await self.generate_embedding(cleaned_text)
        
        # Prepare data for insertion
        document_data = {
            "startup_application_id": startup_id,
            "document_type": document_type,
            "original_filename": filename,
            "file_url": file_url,
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "text_embedding": embedding,
            "structured_data": structured_data,
            "extraction_service": extraction_service,
            "extraction_confidence": extraction_confidence,
            "content_categories": content_categories or [],
            "key_entities": key_entities or {},
            "token_count": len(cleaned_text.split()),
            "embedding_model": embedding_metadata.get("model", "unknown"),
            "processing_cost_cents": int(embedding_metadata.get("cost_usd", 0) * 100)  # Store cost in cents
        }
        
        try:
            # Insert into Supabase
            result = self.supabase.table('document_vectors').insert(document_data).execute()
            
            if result.data:
                document_id = result.data[0]['id']
                logger.info(f"Stored document vector {document_id} for startup {startup_id}")
                return document_id
            else:
                raise Exception("Failed to insert document vector")
                
        except Exception as e:
            logger.error(f"Error storing document vector: {e}")
            raise
    
    async def chunk_and_store_large_document(
        self,
        document_id: str,
        startup_id: int,
        raw_text: str,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> List[str]:
        """Split large documents into chunks and store separately"""
        
        chunks = self._split_text_into_chunks(raw_text, chunk_size, overlap)
        chunk_ids = []
        
        for i, chunk_text in enumerate(chunks):
            # Generate embedding for chunk
            cleaned_chunk = self._clean_text_for_embedding(chunk_text)
            chunk_embedding, chunk_metadata = await self.generate_embedding(cleaned_chunk)
            
            # Determine chunk content type based on keywords
            content_type = self._classify_chunk_content(chunk_text)
            importance_score = self._calculate_chunk_importance(chunk_text, content_type)
            
            chunk_data = {
                "document_vector_id": document_id,
                "startup_application_id": startup_id,
                "chunk_text": chunk_text,
                "chunk_embedding": chunk_embedding,
                "chunk_index": i,
                "chunk_size": len(chunk_text),
                "content_type": content_type,
                "importance_score": importance_score
            }
            
            try:
                result = self.supabase.table('document_chunks').insert(chunk_data).execute()
                if result.data:
                    chunk_ids.append(result.data[0]['id'])
            except Exception as e:
                logger.error(f"Error storing chunk {i}: {e}")
        
        return chunk_ids
    
    def _split_text_into_chunks(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
            
            # Stop if we've processed all words
            if i + chunk_size >= len(words):
                break
        
        return chunks
    
    def _classify_chunk_content(self, chunk_text: str) -> str:
        """Classify chunk content type based on keywords"""
        text_lower = chunk_text.lower()
        
        # Define keyword patterns for different content types
        patterns = {
            'executive_summary': ['executive summary', 'overview', 'mission', 'vision'],
            'problem_solution': ['problem', 'solution', 'pain point', 'address'],
            'market_analysis': ['market', 'tam', 'addressable market', 'competition'],
            'product_info': ['product', 'technology', 'platform', 'feature'],
            'business_model': ['revenue', 'business model', 'monetization', 'pricing'],
            'financials': ['financial', 'revenue', 'profit', 'funding', 'valuation', '$'],
            'team_info': ['team', 'founder', 'ceo', 'experience', 'background'],
            'traction': ['traction', 'growth', 'users', 'customers', 'metrics'],
            'funding': ['funding', 'investment', 'round', 'raise', 'capital']
        }
        
        # Score each content type
        scores = {}
        for content_type, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[content_type] = score
        
        # Return highest scoring type or 'general' if no strong match
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'general'
    
    def _calculate_chunk_importance(self, chunk_text: str, content_type: str) -> float:
        """Calculate importance score for a chunk (0.0 to 1.0)"""
        base_scores = {
            'executive_summary': 0.9,
            'problem_solution': 0.8,
            'financials': 0.8,
            'traction': 0.7,
            'market_analysis': 0.6,
            'business_model': 0.6,
            'product_info': 0.5,
            'team_info': 0.5,
            'funding': 0.8,
            'general': 0.3
        }
        
        base_score = base_scores.get(content_type, 0.5)
        
        # Adjust based on chunk length and content quality
        text_length = len(chunk_text)
        if text_length < 100:
            base_score *= 0.7  # Penalize very short chunks
        elif text_length > 2000:
            base_score *= 1.1  # Reward comprehensive chunks
        
        # Look for important keywords
        important_keywords = [
            'revenue', 'growth', 'users', 'funding', 'investment',
            'technology', 'innovative', 'competitive advantage',
            'market size', 'opportunity'
        ]
        
        keyword_count = sum(1 for keyword in important_keywords 
                          if keyword.lower() in chunk_text.lower())
        
        # Boost score based on keyword presence
        keyword_boost = min(keyword_count * 0.1, 0.3)
        
        return min(base_score + keyword_boost, 1.0)
    
    async def semantic_search(
        self,
        query_text: str,
        startup_id: Optional[int] = None,
        document_types: Optional[List[str]] = None,
        similarity_threshold: float = 0.7,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform semantic search across documents"""
        
        # Generate embedding for query
        query_embedding, query_metadata = await self.generate_embedding(query_text)
        
        try:
            # Call the stored function for semantic search
            result = self.supabase.rpc('search_documents_by_similarity', {
                'query_embedding': query_embedding,
                'similarity_threshold': similarity_threshold,
                'max_results': max_results,
                'startup_id': startup_id,
                'document_types': document_types
            }).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    async def hybrid_search(
        self,
        query_text: str,
        startup_id: Optional[int] = None,
        similarity_threshold: float = 0.7,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search (semantic + keyword)"""
        
        # Check cache first
        cache_result = await self._get_cached_search(query_text, startup_id)
        if cache_result:
            return cache_result
        
        # Generate embedding for query
        query_embedding, query_metadata = await self.generate_embedding(query_text)
        
        try:
            start_time = datetime.now()
            
            # Call the stored function for hybrid search
            result = self.supabase.rpc('hybrid_document_search', {
                'query_text': query_text,
                'query_embedding': query_embedding,
                'similarity_threshold': similarity_threshold,
                'max_results': max_results,
                'startup_id': startup_id
            }).execute()
            
            search_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Cache the results
            await self._cache_search_results(
                query_text, query_embedding, result.data or [], 
                search_time_ms, startup_id
            )
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    async def find_similar_companies(
        self,
        startup_id: int,
        document_type: str = 'pitch_deck',
        similarity_threshold: float = 0.8,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Find companies with similar documents"""
        
        try:
            # First get the document vectors for the given startup
            startup_docs = self.supabase.table('document_vectors') \
                .select('text_embedding') \
                .eq('startup_application_id', startup_id) \
                .eq('document_type', document_type) \
                .eq('status', 'active') \
                .execute()
            
            if not startup_docs.data:
                return []
            
            # Use the first document's embedding as reference
            reference_embedding = startup_docs.data[0]['text_embedding']
            
            # Find similar documents from other companies
            similar_docs = self.supabase.rpc('search_documents_by_similarity', {
                'query_embedding': reference_embedding,
                'similarity_threshold': similarity_threshold,
                'max_results': max_results * 2,  # Get more to filter out same company
                'startup_id': None,  # Search across all companies
                'document_types': [document_type]
            }).execute()
            
            # Filter out the same company and limit results
            results = []
            for doc in similar_docs.data or []:
                if doc['startup_application_id'] != startup_id:
                    results.append(doc)
                if len(results) >= max_results:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar companies: {e}")
            return []
    
    async def _get_cached_search(
        self, 
        query_text: str, 
        startup_id: Optional[int]
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results if available"""
        
        # Create cache key
        cache_key = self._create_cache_key(query_text, startup_id)
        
        try:
            result = self.supabase.table('search_cache') \
                .select('result_document_ids, result_scores') \
                .eq('query_hash', cache_key) \
                .gt('expires_at', datetime.utcnow().isoformat()) \
                .execute()
            
            if result.data:
                # Increment cache hit counter
                cache_id = result.data[0]['id']
                self.supabase.table('search_cache') \
                    .update({'cache_hits': self.supabase.table('search_cache').select('cache_hits').eq('id', cache_id).single().execute().data['cache_hits'] + 1}) \
                    .eq('id', cache_id) \
                    .execute()
                
                # Reconstruct results from cached IDs
                # This is a simplified version - in practice you'd fetch full document details
                return result.data
            
        except Exception as e:
            logger.error(f"Error retrieving cached search: {e}")
        
        return None
    
    async def _cache_search_results(
        self,
        query_text: str,
        query_embedding: List[float],
        results: List[Dict[str, Any]],
        search_time_ms: int,
        startup_id: Optional[int]
    ):
        """Cache search results for future queries"""
        
        cache_key = self._create_cache_key(query_text, startup_id)
        
        # Extract document IDs and scores from results
        result_ids = [r.get('document_id') for r in results if r.get('document_id')]
        result_scores = [r.get('similarity_score', 0) for r in results]
        
        cache_data = {
            'query_text': query_text,
            'query_embedding': query_embedding,
            'query_hash': cache_key,
            'result_document_ids': result_ids,
            'result_scores': result_scores,
            'total_results': len(results),
            'search_time_ms': search_time_ms,
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        try:
            self.supabase.table('search_cache').insert(cache_data).execute()
        except Exception as e:
            logger.error(f"Error caching search results: {e}")
    
    def _create_cache_key(self, query_text: str, startup_id: Optional[int]) -> str:
        """Create a unique cache key for the query"""
        key_data = f"{query_text.lower().strip()}_{startup_id or 'all'}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_document_stats(self, startup_id: Optional[int] = None) -> Dict[str, Any]:
        """Get statistics about stored documents"""
        
        try:
            if startup_id:
                result = self.supabase.table('document_vector_stats') \
                    .select('*') \
                    .eq('startup_application_id', startup_id) \
                    .execute()
            else:
                result = self.supabase.table('document_vector_stats') \
                    .select('*') \
                    .execute()
            
            return {
                'success': True,
                'data': result.data,
                'total_startups': len(result.data) if result.data else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting document stats: {e}")
            return {'success': False, 'error': str(e)}
    
    async def cleanup_old_data(self) -> Dict[str, int]:
        """Clean up old cache entries and optionally archive old documents"""
        
        cleanup_results = {}
        
        try:
            # Clean up expired cache
            cache_result = self.supabase.rpc('cleanup_expired_cache').execute()
            cleanup_results['expired_cache_cleaned'] = cache_result.data or 0
            
            # Optionally archive old documents (uncomment if needed)
            # archive_result = self.supabase.rpc('archive_old_documents', {'days_old': 365}).execute()
            # cleanup_results['documents_archived'] = archive_result.data or 0
            
            logger.info(f"Cleanup completed: {cleanup_results}")
            return cleanup_results
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return {'error': str(e)}

# Global service instance
vector_document_service = VectorDocumentService()