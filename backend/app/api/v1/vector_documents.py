"""
Vector Documents API
Endpoints for document embedding, semantic search, and document analysis
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.vector_document_service import vector_document_service
from app.services.database_service import db_service

import logging

from app.api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vector-documents", tags=["vector-documents"])

# =====================================================
# PYDANTIC MODELS
# =====================================================

class DocumentUploadRequest(BaseModel):
    startup_id: int = Field(..., description="Startup application ID")
    document_type: str = Field(..., description="Type of document (pitch_deck, financial_statement, etc.)")
    extraction_service: str = Field(default="landing_ai", description="AI service to use for extraction")
    chunk_large_documents: bool = Field(default=True, description="Whether to chunk large documents")
    
class DocumentVector(BaseModel):
    id: str
    startup_application_id: int
    document_type: str
    original_filename: str
    file_url: Optional[str]
    extraction_confidence: Optional[float]
    content_categories: List[str]
    token_count: int
    created_at: str
    
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query text")
    startup_id: Optional[int] = Field(None, description="Limit search to specific startup")
    document_types: Optional[List[str]] = Field(None, description="Filter by document types")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Minimum similarity score")
    max_results: int = Field(10, ge=1, le=100, description="Maximum number of results")
    search_type: str = Field("hybrid", description="Search type: semantic, hybrid, or keyword")

class SearchResult(BaseModel):
    document_id: str
    startup_application_id: int
    document_type: str
    filename: str
    similarity_score: float
    text_snippet: str
    structured_data: Dict[str, Any]
    
class SimilarCompaniesRequest(BaseModel):
    startup_id: int = Field(..., description="Reference startup ID")
    document_type: str = Field(default="pitch_deck", description="Document type to compare")
    similarity_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Minimum similarity score")
    max_results: int = Field(5, ge=1, le=20, description="Maximum number of results")

# =====================================================
# DOCUMENT UPLOAD AND PROCESSING
# =====================================================

@router.post("/upload", response_model=Dict[str, Any])
async def upload_and_process_document(
    file: UploadFile = File(...),
    startup_id: int = Form(...),
    document_type: str = Form(...),
    extraction_service: str = Form(default="landing_ai"),
    chunk_large_documents: bool = Form(default=True),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a document and process it for vector storage
    
    This endpoint:
    1. Receives the uploaded file
    2. Extracts text using the specified AI service
    3. Generates embeddings
    4. Stores in vector database
    5. Optionally chunks large documents
    """
    
    try:
        # Validate startup exists
        startup = await db_service.get_startup(startup_id, db)
        if not startup:
            raise HTTPException(status_code=404, detail="Startup not found")
        
        # Save uploaded file (you'll need to implement file storage)
        file_content = await file.read()
        file_url = f"gs://your-bucket/{startup_id}/{file.filename}"  # Placeholder
        
        # Here you would:
        # 1. Save file to Google Cloud Storage
        # 2. Extract text using Document AI or Landing AI
        # 3. Process extracted data
        
        # For now, simulating extracted data
        extracted_data = {
            "raw_text": "Sample extracted text from the document...",
            "structured_data": {
                "company_name": "Example Company",
                "funding_stage": "Series A",
                "industry": "AI/ML"
            },
            "confidence": 89.5
        }
        
        # Store in vector database
        document_id = await vector_document_service.store_document_vector(
            startup_id=startup_id,
            document_type=document_type,
            filename=file.filename,
            raw_text=extracted_data["raw_text"],
            structured_data=extracted_data["structured_data"],
            extraction_service=extraction_service,
            extraction_confidence=extracted_data["confidence"],
            file_url=file_url,
            content_categories=["business", "financial"],  # Would be determined by AI
            key_entities={"companies": ["Example Company"], "people": []}
        )
        
        # Optionally chunk large documents
        chunk_ids = []
        if chunk_large_documents and len(extracted_data["raw_text"]) > 2000:
            chunk_ids = await vector_document_service.chunk_and_store_large_document(
                document_id=document_id,
                startup_id=startup_id,
                raw_text=extracted_data["raw_text"]
            )
        
        return {
            "success": True,
            "message": "Document processed and stored successfully",
            "data": {
                "document_id": document_id,
                "filename": file.filename,
                "chunks_created": len(chunk_ids),
                "extraction_service": extraction_service,
                "confidence": extracted_data["confidence"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing document upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

# =====================================================
# SEMANTIC SEARCH ENDPOINTS
# =====================================================

@router.post("/search", response_model=List[SearchResult])
async def search_documents(
    request: SearchRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Perform semantic search across document vectors
    
    Supports multiple search types:
    - semantic: Pure vector similarity search
    - hybrid: Combines semantic similarity with keyword matching
    - keyword: Traditional text search (if needed)
    """
    
    try:
        if request.search_type == "semantic":
            results = await vector_document_service.semantic_search(
                query_text=request.query,
                startup_id=request.startup_id,
                document_types=request.document_types,
                similarity_threshold=request.similarity_threshold,
                max_results=request.max_results
            )
        elif request.search_type == "hybrid":
            results = await vector_document_service.hybrid_search(
                query_text=request.query,
                startup_id=request.startup_id,
                similarity_threshold=request.similarity_threshold,
                max_results=request.max_results
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid search type")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in document search: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/search/similar-companies")
async def find_similar_companies(
    startup_id: int = Query(..., description="Reference startup ID"),
    document_type: str = Query(default="pitch_deck", description="Document type to compare"),
    similarity_threshold: float = Query(0.8, ge=0.0, le=1.0, description="Minimum similarity score"),
    max_results: int = Query(5, ge=1, le=20, description="Maximum results"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Find companies with similar documents based on vector similarity
    
    This is useful for:
    - Competitive analysis
    - Market research
    - Investment pattern analysis
    - Due diligence comparisons
    """
    
    try:
        similar_companies = await vector_document_service.find_similar_companies(
            startup_id=startup_id,
            document_type=document_type,
            similarity_threshold=similarity_threshold,
            max_results=max_results
        )
        
        return {
            "success": True,
            "reference_startup_id": startup_id,
            "document_type": document_type,
            "similar_companies": similar_companies,
            "total_found": len(similar_companies)
        }
        
    except Exception as e:
        logger.error(f"Error finding similar companies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find similar companies: {str(e)}")

# =====================================================
# DOCUMENT MANAGEMENT
# =====================================================

@router.get("/startup/{startup_id}", response_model=List[DocumentVector])
async def get_startup_documents(
    startup_id: int,
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all documents for a specific startup"""
    
    try:
        # Validate startup exists
        startup = await db_service.get_startup(startup_id, db)
        if not startup:
            raise HTTPException(status_code=404, detail="Startup not found")
        
        # Query documents from Supabase
        query = vector_document_service.supabase.table('document_vectors') \
            .select('*') \
            .eq('startup_application_id', startup_id) \
            .eq('status', 'active')
        
        if document_type:
            query = query.eq('document_type', document_type)
        
        result = query.execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error retrieving startup documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Soft delete a document (mark as archived)"""
    
    try:
        # Update document status to archived
        result = vector_document_service.supabase.table('document_vectors') \
            .update({'status': 'archived'}) \
            .eq('id', document_id) \
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "success": True,
            "message": "Document archived successfully",
            "document_id": document_id
        }
        
    except Exception as e:
        logger.error(f"Error archiving document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to archive document: {str(e)}")

# =====================================================
# ANALYTICS AND STATISTICS
# =====================================================

@router.get("/stats")
async def get_document_statistics(
    startup_id: Optional[int] = Query(None, description="Filter by startup ID"),
    current_user: Dict = Depends(get_current_user)
):
    """Get document storage and processing statistics"""
    
    try:
        stats = await vector_document_service.get_document_stats(startup_id)
        return stats
        
    except Exception as e:
        logger.error(f"Error retrieving document statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")

@router.get("/stats/search-performance")
async def get_search_performance(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: Dict = Depends(get_current_user)
):
    """Get search performance analytics"""
    
    try:
        result = vector_document_service.supabase.table('search_performance') \
            .select('*') \
            .limit(days) \
            .execute()
        
        return {
            "success": True,
            "data": result.data or [],
            "period_days": days
        }
        
    except Exception as e:
        logger.error(f"Error retrieving search performance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve search performance: {str(e)}")

# =====================================================
# ADMIN ENDPOINTS
# =====================================================

@router.post("/admin/cleanup")
async def cleanup_old_data(
    current_user: Dict = Depends(get_current_user)
):
    """Clean up expired cache and old data (admin only)"""
    
    # TODO: Add admin role check
    # if not current_user.get('is_superuser'):
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        cleanup_results = await vector_document_service.cleanup_old_data()
        return {
            "success": True,
            "message": "Cleanup completed",
            "results": cleanup_results
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@router.post("/admin/reindex")
async def reindex_documents(
    startup_id: Optional[int] = Query(None, description="Reindex specific startup only"),
    current_user: Dict = Depends(get_current_user)
):
    """Regenerate embeddings for existing documents (admin only)"""
    
    # TODO: Add admin role check
    # if not current_user.get('is_superuser'):
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get documents to reindex
        query = vector_document_service.supabase.table('document_vectors') \
            .select('id, cleaned_text') \
            .eq('status', 'active')
        
        if startup_id:
            query = query.eq('startup_application_id', startup_id)
        
        result = query.execute()
        documents = result.data or []
        
        reindexed_count = 0
        for doc in documents:
            try:
                # Regenerate embedding
                new_embedding = await vector_document_service.generate_embedding(doc['cleaned_text'])
                
                # Update document
                vector_document_service.supabase.table('document_vectors') \
                    .update({'text_embedding': new_embedding, 'updated_at': 'NOW()'}) \
                    .eq('id', doc['id']) \
                    .execute()
                
                reindexed_count += 1
                
            except Exception as e:
                logger.error(f"Error reindexing document {doc['id']}: {e}")
        
        return {
            "success": True,
            "message": f"Reindexed {reindexed_count} documents",
            "reindexed_count": reindexed_count,
            "total_documents": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error during reindexing: {e}")
        raise HTTPException(status_code=500, detail=f"Reindexing failed: {str(e)}")

# =====================================================
# UTILITY ENDPOINTS
# =====================================================

@router.get("/health")
async def vector_db_health_check():
    """Health check for vector database operations"""
    
    try:
        # Test basic connection
        test_result = vector_document_service.supabase.table('document_vectors') \
            .select('count') \
            .execute()
        
        # Test embedding generation
        test_embedding = await vector_document_service.generate_embedding("test query")
        
        return {
            "status": "healthy",
            "vector_db_connected": True,
            "embedding_service": "available" if len(test_embedding) > 0 else "unavailable",
            "embedding_dimensions": len(test_embedding),
            "timestamp": "2024-10-07T09:30:00Z"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-10-07T09:30:00Z"
        }