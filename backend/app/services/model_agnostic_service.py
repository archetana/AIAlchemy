"""
Model-Agnostic AI Service
Supports multiple AI providers through LiteLLM for embeddings and text generation
Provides cost optimization, fallback mechanisms, and local model support
"""

import os
import asyncio
import hashlib
import json
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

try:
    import litellm
    from litellm import embedding, aembedding, completion, acompletion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logger.warning("LiteLLM not available. Install with: pip install litellm")

try:
    from sentence_transformers import SentenceTransformer
    import torch
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.info("sentence-transformers not available for local models")

class ModelProvider(Enum):
    """Supported model providers"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    LOCAL = "local"
    GEMINI = "gemini"
    NVIDIA_NIM = "nvidia_nim"
    FALLBACK = "fallback"

class EmbeddingModel(Enum):
    """Supported embedding models"""
    # NVIDIA NIM (Priority - FREE CREDITS!)
    NVIDIA_NV_EMBED_V2 = "nvidia/nv-embed-v2"
    NVIDIA_EMBED_QA_MISTRAL_7B_V2 = "nvidia/nv-embedqa-mistral-7b-v2"  # Deprecated but may still work
    NVIDIA_EMBED_CODE = "nvidia/nv-embedcode"
    
    # OpenAI
    OPENAI_ADA_002 = "text-embedding-ada-002"
    OPENAI_3_SMALL = "text-embedding-3-small"
    OPENAI_3_LARGE = "text-embedding-3-large"
    
    # Azure OpenAI
    AZURE_ADA_002 = "azure/text-embedding-ada-002"
    
    # Cohere
    COHERE_ENGLISH = "embed-english-v3.0"
    COHERE_MULTILINGUAL = "embed-multilingual-v3.0"
    
    # HuggingFace (via API)
    HF_SENTENCE_T5 = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Local models
    LOCAL_MINILM = "all-MiniLM-L6-v2"
    LOCAL_MPNET = "all-mpnet-base-v2"
    LOCAL_DISTILBERT = "distilbert-base-nli-mean-tokens"
    
    # Ollama
    OLLAMA_NOMIC = "ollama/nomic-embed-text"
    
    # Fallback
    FALLBACK_HASH = "fallback"

class ModelAgnosticService:
    """
    Model-agnostic AI service for embeddings and text generation
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.embedding_cache = {}
        self.cost_tracker = {}
        self.local_models = {}
        
        # Initialize LiteLLM
        if LITELLM_AVAILABLE:
            litellm.set_verbose = False  # Disable verbose logging
            self._setup_litellm()
        
        # Load local models if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._load_local_models()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        return {
            # Model preferences (in order of preference)
            "embedding_models": [
                EmbeddingModel.NVIDIA_NV_EMBED_V2,       # PRIORITY: FREE CREDITS! 
                EmbeddingModel.NVIDIA_EMBED_QA_MISTRAL_7B_V2,  # Backup NVIDIA model
                EmbeddingModel.LOCAL_MINILM,             # Fast local model (free)
                EmbeddingModel.OPENAI_3_SMALL,           # Most cost-effective OpenAI
                EmbeddingModel.COHERE_ENGLISH,           # Good alternative
                EmbeddingModel.FALLBACK_HASH             # Always available
            ],
            
            # Provider configurations
            "providers": {
                ModelProvider.NVIDIA_NIM: {
                    "api_key": os.getenv("NVIDIA_NIM_API_KEY"),
                    "base_url": os.getenv("NVIDIA_NIM_BASE_URL", "https://api.nvcf.nvidia.com/v2/nvcf"),
                    "enabled": bool(os.getenv("NVIDIA_NIM_API_KEY")),
                    "credits_remaining": int(os.getenv("NVIDIA_NIM_CREDITS", "0"))  # Track remaining credits
                },
                ModelProvider.OPENAI: {
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "enabled": bool(os.getenv("OPENAI_API_KEY"))
                },
                ModelProvider.AZURE_OPENAI: {
                    "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
                    "api_base": os.getenv("AZURE_OPENAI_ENDPOINT"),
                    "api_version": os.getenv("AZURE_OPENAI_VERSION", "2023-12-01-preview"),
                    "enabled": bool(os.getenv("AZURE_OPENAI_API_KEY"))
                },
                ModelProvider.ANTHROPIC: {
                    "api_key": os.getenv("ANTHROPIC_API_KEY"),
                    "enabled": bool(os.getenv("ANTHROPIC_API_KEY"))
                },
                ModelProvider.COHERE: {
                    "api_key": os.getenv("COHERE_API_KEY"),
                    "enabled": bool(os.getenv("COHERE_API_KEY"))
                },
                ModelProvider.GEMINI: {
                    "api_key": os.getenv("GEMINI_API_KEY"),
                    "enabled": bool(os.getenv("GEMINI_API_KEY"))
                },
                ModelProvider.HUGGINGFACE: {
                    "api_key": os.getenv("HUGGINGFACE_API_KEY"),
                    "enabled": bool(os.getenv("HUGGINGFACE_API_KEY"))
                },
                ModelProvider.OLLAMA: {
                    "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                    "enabled": os.getenv("OLLAMA_ENABLED", "false").lower() == "true"
                },
                ModelProvider.LOCAL: {
                    "enabled": SENTENCE_TRANSFORMERS_AVAILABLE,
                    "cache_dir": os.getenv("LOCAL_MODEL_CACHE_DIR", "./models")
                }
            },
            
            # Cost optimization
            "cost_thresholds": {
                "daily_limit_usd": float(os.getenv("DAILY_AI_COST_LIMIT", "10.0")),
                "monthly_limit_usd": float(os.getenv("MONTHLY_AI_COST_LIMIT", "100.0"))
            },
            
            # Performance settings
            "cache_ttl_hours": int(os.getenv("EMBEDDING_CACHE_TTL_HOURS", "24")),
            "max_retries": int(os.getenv("AI_MAX_RETRIES", "3")),
            "timeout_seconds": int(os.getenv("AI_TIMEOUT_SECONDS", "30"))
        }
    
    def _setup_litellm(self):
        """Setup LiteLLM with available providers"""
        # Set API keys for available providers
        if self.config["providers"][ModelProvider.NVIDIA_NIM]["enabled"]:
            # NVIDIA NIM uses OpenAI-compatible format
            nvidia_config = self.config["providers"][ModelProvider.NVIDIA_NIM]
            litellm.api_base = nvidia_config["base_url"]
            os.environ["NVIDIA_NIM_API_KEY"] = nvidia_config["api_key"]
        
        if self.config["providers"][ModelProvider.OPENAI]["enabled"]:
            os.environ["OPENAI_API_KEY"] = self.config["providers"][ModelProvider.OPENAI]["api_key"]
        
        if self.config["providers"][ModelProvider.COHERE]["enabled"]:
            os.environ["COHERE_API_KEY"] = self.config["providers"][ModelProvider.COHERE]["api_key"]
        
        if self.config["providers"][ModelProvider.ANTHROPIC]["enabled"]:
            os.environ["ANTHROPIC_API_KEY"] = self.config["providers"][ModelProvider.ANTHROPIC]["api_key"]
    
    def _load_local_models(self):
        """Load local embedding models"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return
        
        try:
            # Load commonly used local models
            cache_dir = self.config["providers"][ModelProvider.LOCAL]["cache_dir"]
            
            # Start with the fastest, smallest model
            model_name = "all-MiniLM-L6-v2"
            logger.info(f"Loading local embedding model: {model_name}")
            
            self.local_models[EmbeddingModel.LOCAL_MINILM] = SentenceTransformer(
                model_name, 
                cache_folder=cache_dir
            )
            
            logger.info(f"Local model {model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load local models: {e}")
            self.config["providers"][ModelProvider.LOCAL]["enabled"] = False
    
    async def generate_embedding(
        self, 
        text: str, 
        model: Optional[EmbeddingModel] = None,
        dimensions: Optional[int] = None
    ) -> Tuple[List[float], Dict[str, Any]]:
        """
        Generate embeddings using the best available model
        
        Returns:
            Tuple of (embedding_vector, metadata)
        """
        
        # Check cache first
        cache_key = self._create_cache_key(text, model, dimensions)
        if cache_key in self.embedding_cache:
            cached_result = self.embedding_cache[cache_key]
            if self._is_cache_valid(cached_result["timestamp"]):
                return cached_result["embedding"], cached_result["metadata"]
        
        # Determine which models to try
        models_to_try = self._get_available_models(model)
        
        for model_enum in models_to_try:
            try:
                start_time = time.time()
                
                embedding, cost = await self._generate_with_model(text, model_enum, dimensions)
                
                processing_time = time.time() - start_time
                
                # Create metadata
                metadata = {
                    "model": model_enum.value,
                    "provider": self._get_model_provider(model_enum),
                    "dimensions": len(embedding),
                    "cost_usd": cost,
                    "processing_time_seconds": processing_time,
                    "text_length": len(text),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Cache the result
                self.embedding_cache[cache_key] = {
                    "embedding": embedding,
                    "metadata": metadata,
                    "timestamp": datetime.utcnow()
                }
                
                # Track costs
                self._track_cost(metadata["provider"], cost)
                
                logger.info(f"Generated embedding using {model_enum.value}: {len(embedding)} dimensions, ${cost:.6f}")
                
                return embedding, metadata
                
            except Exception as e:
                logger.warning(f"Failed to generate embedding with {model_enum.value}: {e}")
                continue
        
        # If all models failed, raise exception
        raise Exception("All embedding models failed")
    
    async def _generate_with_model(
        self, 
        text: str, 
        model: EmbeddingModel,
        dimensions: Optional[int] = None
    ) -> Tuple[List[float], float]:
        """Generate embedding with specific model"""
        
        if model == EmbeddingModel.FALLBACK_HASH:
            return self._generate_fallback_embedding(text, dimensions or 1536), 0.0
        
        # NVIDIA NIM models (special handling for OpenAI-compatible API)
        if model in [EmbeddingModel.NVIDIA_NV_EMBED_V2, EmbeddingModel.NVIDIA_EMBED_QA_MISTRAL_7B_V2, EmbeddingModel.NVIDIA_EMBED_CODE]:
            return await self._generate_nvidia_nim_embedding(text, model, dimensions)
        
        # Local models
        if model in [EmbeddingModel.LOCAL_MINILM, EmbeddingModel.LOCAL_MPNET, EmbeddingModel.LOCAL_DISTILBERT]:
            return await self._generate_local_embedding(text, model), 0.0
        
        # API-based models via LiteLLM
        if LITELLM_AVAILABLE:
            return await self._generate_api_embedding(text, model, dimensions)
        
        # Fallback if LiteLLM not available
        return self._generate_fallback_embedding(text, dimensions or 1536), 0.0
    
    async def _generate_api_embedding(
        self, 
        text: str, 
        model: EmbeddingModel,
        dimensions: Optional[int] = None
    ) -> Tuple[List[float], float]:
        """Generate embedding using LiteLLM API"""
        
        try:
            # Prepare request
            kwargs = {"input": text, "model": model.value}
            
            # Add dimensions if specified and supported
            if dimensions and model in [EmbeddingModel.OPENAI_3_SMALL, EmbeddingModel.OPENAI_3_LARGE]:
                kwargs["dimensions"] = dimensions
            
            # Make async request
            response = await aembedding(**kwargs)
            
            embedding = response.data[0]["embedding"]
            
            # Calculate cost (rough estimate)
            cost = self._estimate_embedding_cost(model, len(text))
            
            return embedding, cost
            
        except Exception as e:
            logger.error(f"API embedding failed for {model.value}: {e}")
            raise
    
    async def _generate_nvidia_nim_embedding(
        self, 
        text: str, 
        model: EmbeddingModel,
        dimensions: Optional[int] = None
    ) -> Tuple[List[float], float]:
        """Generate embedding using NVIDIA NIM API (OpenAI-compatible)"""
        
        try:
            import httpx
            
            nvidia_config = self.config["providers"][ModelProvider.NVIDIA_NIM]
            api_key = nvidia_config["api_key"]
            base_url = nvidia_config["base_url"]
            
            # Check if we have credits remaining
            credits_remaining = nvidia_config.get("credits_remaining", 0)
            if credits_remaining <= 0:
                logger.warning("No NVIDIA NIM credits remaining, failing to fallback")
                raise Exception("No NVIDIA NIM credits remaining")
            
            # Prepare OpenAI-compatible request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # NVIDIA NIM uses OpenAI-compatible /v1/embeddings endpoint
            url = f"{base_url}/v1/embeddings"
            
            payload = {
                "input": text,
                "model": model.value,
                "encoding_format": "float"
            }
            
            # Add dimensions if supported
            if dimensions and model == EmbeddingModel.NVIDIA_NV_EMBED_V2:
                payload["dimensions"] = dimensions
            
            async with httpx.AsyncClient(timeout=self.config["timeout_seconds"]) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                data = response.json()
                embedding = data["data"][0]["embedding"]
                
                # NVIDIA NIM is FREE with credits - track usage but no cost
                self._track_nvidia_credit_usage()
                
                logger.info(f"NVIDIA NIM embedding generated: {len(embedding)} dimensions, FREE with credits")
                
                return embedding, 0.0  # FREE!
                
        except Exception as e:
            logger.error(f"NVIDIA NIM embedding failed for {model.value}: {e}")
            raise
    
    def _track_nvidia_credit_usage(self):
        """Track NVIDIA NIM credit usage"""
        nvidia_config = self.config["providers"][ModelProvider.NVIDIA_NIM]
        current_credits = nvidia_config.get("credits_remaining", 0)
        
        if current_credits > 0:
            nvidia_config["credits_remaining"] = current_credits - 1
            logger.debug(f"NVIDIA NIM credits remaining: {nvidia_config['credits_remaining']}")
        
        # Log when approaching credit limit
        if nvidia_config["credits_remaining"] <= 100:  # Warning at 100 credits
            logger.warning(f"NVIDIA NIM credits running low: {nvidia_config['credits_remaining']} remaining")
    
    async def _generate_local_embedding(self, text: str, model: EmbeddingModel) -> List[float]:
        """Generate embedding using local model"""
        
        if model not in self.local_models:
            raise Exception(f"Local model {model.value} not loaded")
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None, 
            self.local_models[model].encode, 
            text
        )
        
        return embedding.tolist()
    
    def _generate_fallback_embedding(self, text: str, dimensions: int = 1536) -> List[float]:
        """Generate deterministic fallback embedding"""
        # Create multiple hashes to get enough data
        text_bytes = text.encode('utf-8')
        
        embedding = []
        for i in range(0, dimensions, 32):  # MD5 gives us 32 hex chars = 16 bytes
            hash_input = f"{text}_{i}".encode('utf-8')
            hash_hex = hashlib.md5(hash_input).hexdigest()
            
            # Convert hex to normalized floats
            for j in range(0, len(hash_hex), 2):
                if len(embedding) >= dimensions:
                    break
                hex_pair = hash_hex[j:j+2]
                value = int(hex_pair, 16) / 255.0  # Normalize to 0-1
                embedding.append(value - 0.5)  # Center around 0
        
        # Ensure exact dimensions
        while len(embedding) < dimensions:
            embedding.append(0.0)
        
        # Normalize vector
        import math
        magnitude = math.sqrt(sum(x * x for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding[:dimensions]
    
    def _get_available_models(self, preferred_model: Optional[EmbeddingModel] = None) -> List[EmbeddingModel]:
        """Get list of available models in order of preference"""
        
        available_models = []
        
        # Add preferred model first if specified and available
        if preferred_model and self._is_model_available(preferred_model):
            available_models.append(preferred_model)
        
        # Add other available models from config
        for model in self.config["embedding_models"]:
            if model not in available_models and self._is_model_available(model):
                available_models.append(model)
        
        # Always add fallback
        if EmbeddingModel.FALLBACK_HASH not in available_models:
            available_models.append(EmbeddingModel.FALLBACK_HASH)
        
        return available_models
    
    def _is_model_available(self, model: EmbeddingModel) -> bool:
        """Check if a model is available"""
        
        if model == EmbeddingModel.FALLBACK_HASH:
            return True
        
        # NVIDIA NIM models
        if model in [EmbeddingModel.NVIDIA_NV_EMBED_V2, EmbeddingModel.NVIDIA_EMBED_QA_MISTRAL_7B_V2, EmbeddingModel.NVIDIA_EMBED_CODE]:
            nvidia_config = self.config["providers"][ModelProvider.NVIDIA_NIM]
            return (
                nvidia_config["enabled"] and
                nvidia_config.get("credits_remaining", 0) > 0  # Must have credits
            )
        
        # Local models
        if model in [EmbeddingModel.LOCAL_MINILM, EmbeddingModel.LOCAL_MPNET, EmbeddingModel.LOCAL_DISTILBERT]:
            return (
                self.config["providers"][ModelProvider.LOCAL]["enabled"] and
                model in self.local_models
            )
        
        # API models - check if LiteLLM and provider are available
        if not LITELLM_AVAILABLE:
            return False
        
        provider = self._get_model_provider(model)
        return self.config["providers"][provider]["enabled"]
    
    def _get_model_provider(self, model: EmbeddingModel) -> ModelProvider:
        """Get provider for a model"""
        
        if model.value.startswith("nvidia/"):
            return ModelProvider.NVIDIA_NIM
        elif model.value.startswith("text-embedding-"):
            return ModelProvider.OPENAI
        elif model.value.startswith("azure/"):
            return ModelProvider.AZURE_OPENAI
        elif model.value.startswith("embed-"):
            return ModelProvider.COHERE
        elif model.value.startswith("sentence-transformers/"):
            return ModelProvider.HUGGINGFACE
        elif model.value.startswith("ollama/"):
            return ModelProvider.OLLAMA
        elif model in [EmbeddingModel.LOCAL_MINILM, EmbeddingModel.LOCAL_MPNET, EmbeddingModel.LOCAL_DISTILBERT]:
            return ModelProvider.LOCAL
        else:
            return ModelProvider.FALLBACK
    
    def _estimate_embedding_cost(self, model: EmbeddingModel, text_length: int) -> float:
        """Estimate cost for embedding generation"""
        
        # Rough token estimate (1 token ≈ 4 characters)
        estimated_tokens = text_length / 4
        
        # Cost per 1K tokens (approximate)
        costs_per_1k_tokens = {
            # NVIDIA NIM models are FREE with credits!
            EmbeddingModel.NVIDIA_NV_EMBED_V2: 0.0,
            EmbeddingModel.NVIDIA_EMBED_QA_MISTRAL_7B_V2: 0.0,
            EmbeddingModel.NVIDIA_EMBED_CODE: 0.0,
            # OpenAI models
            EmbeddingModel.OPENAI_ADA_002: 0.0001,
            EmbeddingModel.OPENAI_3_SMALL: 0.00002,
            EmbeddingModel.OPENAI_3_LARGE: 0.00013,
            EmbeddingModel.COHERE_ENGLISH: 0.0001,
            EmbeddingModel.COHERE_MULTILINGUAL: 0.0001,
        }
        
        cost_per_1k = costs_per_1k_tokens.get(model, 0.0001)  # Default estimate
        
        return (estimated_tokens / 1000) * cost_per_1k
    
    def _create_cache_key(self, text: str, model: Optional[EmbeddingModel], dimensions: Optional[int]) -> str:
        """Create cache key for embedding"""
        key_data = f"{text}_{model.value if model else 'auto'}_{dimensions or 'default'}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Check if cache entry is still valid"""
        ttl = timedelta(hours=self.config["cache_ttl_hours"])
        return datetime.utcnow() - timestamp < ttl
    
    def _track_cost(self, provider: ModelProvider, cost: float):
        """Track AI service costs"""
        today = datetime.utcnow().date().isoformat()
        
        if provider.value not in self.cost_tracker:
            self.cost_tracker[provider.value] = {}
        
        if today not in self.cost_tracker[provider.value]:
            self.cost_tracker[provider.value][today] = 0.0
        
        self.cost_tracker[provider.value][today] += cost
        
        # Log if approaching limits
        daily_total = sum(
            day_costs for day_costs in self.cost_tracker[provider.value].values()
            if day_costs
        )
        
        daily_limit = self.config["cost_thresholds"]["daily_limit_usd"]
        if daily_total > daily_limit * 0.8:  # 80% of limit
            logger.warning(f"Approaching daily cost limit: ${daily_total:.2f} / ${daily_limit:.2f}")
    
    def get_cost_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get cost summary for recent days"""
        
        summary = {
            "total_cost_usd": 0.0,
            "by_provider": {},
            "by_day": {},
            "period_days": days
        }
        
        cutoff_date = (datetime.utcnow().date() - timedelta(days=days)).isoformat()
        
        for provider, daily_costs in self.cost_tracker.items():
            provider_total = 0.0
            
            for date, cost in daily_costs.items():
                if date >= cutoff_date:
                    provider_total += cost
                    
                    if date not in summary["by_day"]:
                        summary["by_day"][date] = 0.0
                    summary["by_day"][date] += cost
            
            if provider_total > 0:
                summary["by_provider"][provider] = provider_total
                summary["total_cost_usd"] += provider_total
        
        return summary
    
    def get_available_models_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        
        models_info = {}
        
        for model in EmbeddingModel:
            provider = self._get_model_provider(model)
            is_available = self._is_model_available(model)
            
            models_info[model.value] = {
                "provider": provider.value,
                "available": is_available,
                "cost_estimate": "Free" if provider in [ModelProvider.LOCAL, ModelProvider.FALLBACK, ModelProvider.NVIDIA_NIM] else "Paid",
                "dimensions": self._get_model_dimensions(model)
            }
        
        return models_info
    
    def _get_model_dimensions(self, model: EmbeddingModel) -> int:
        """Get embedding dimensions for model"""
        
        dimensions_map = {
            # NVIDIA NIM models - high quality embeddings!
            EmbeddingModel.NVIDIA_NV_EMBED_V2: 4096,      # Latest generalist model
            EmbeddingModel.NVIDIA_EMBED_QA_MISTRAL_7B_V2: 4096,  # QA-optimized
            EmbeddingModel.NVIDIA_EMBED_CODE: 4096,       # Code-optimized
            # OpenAI models
            EmbeddingModel.OPENAI_ADA_002: 1536,
            EmbeddingModel.OPENAI_3_SMALL: 1536,
            EmbeddingModel.OPENAI_3_LARGE: 3072,
            # Local models
            EmbeddingModel.LOCAL_MINILM: 384,
            EmbeddingModel.LOCAL_MPNET: 768,
            EmbeddingModel.LOCAL_DISTILBERT: 768,
            # Cohere models
            EmbeddingModel.COHERE_ENGLISH: 1024,
            EmbeddingModel.COHERE_MULTILINGUAL: 1024,
            EmbeddingModel.FALLBACK_HASH: 1536
        }
        
        return dimensions_map.get(model, 1536)

# Global service instance
model_service = ModelAgnosticService()