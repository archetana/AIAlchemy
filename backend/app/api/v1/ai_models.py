"""
AI Models Management API
Endpoints for managing AI models, providers, and cost optimization
"""

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.services.model_agnostic_service import model_service, EmbeddingModel, ModelProvider
from app.api.auth import get_current_user
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-models", tags=["ai-models"])

# =====================================================
# PYDANTIC MODELS
# =====================================================

class ModelInfo(BaseModel):
    model_name: str
    provider: str
    available: bool
    cost_estimate: str
    dimensions: int
    description: Optional[str] = None

class CostSummary(BaseModel):
    total_cost_usd: float
    by_provider: Dict[str, float]
    by_day: Dict[str, float]
    period_days: int

class EmbeddingRequest(BaseModel):
    text: str = Field(..., description="Text to generate embedding for")
    model: Optional[str] = Field(None, description="Specific model to use (optional)")
    dimensions: Optional[int] = Field(None, description="Embedding dimensions (if supported)")

class EmbeddingResponse(BaseModel):
    embedding: List[float]
    metadata: Dict[str, Any]
    available_models: List[str]

class ModelConfig(BaseModel):
    preferred_models: List[str] = Field(default=[], description="Preferred models in order")
    cost_limits: Dict[str, float] = Field(default={}, description="Cost limits by provider")
    enable_fallback: bool = Field(default=True, description="Enable fallback models")

# =====================================================
# MODEL INFORMATION ENDPOINTS
# =====================================================

@router.get("/available", response_model=List[ModelInfo])
async def get_available_models(
    current_user: Dict = Depends(get_current_user)
):
    """Get list of all available AI models"""
    
    try:
        models_info = model_service.get_available_models_info()
        
        result = []
        for model_name, info in models_info.items():
            result.append(ModelInfo(
                model_name=model_name,
                provider=info["provider"],
                available=info["available"],
                cost_estimate=info["cost_estimate"],
                dimensions=info["dimensions"],
                description=f"{info['provider']} embedding model with {info['dimensions']} dimensions"
            ))
        
        # Sort by availability, cost, and prioritize NVIDIA NIM
        result.sort(key=lambda x: (
            not x.available, 
            x.cost_estimate == "Paid", 
            not x.model_name.startswith("nvidia/"),  # NVIDIA models first
            x.model_name
        ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")

@router.get("/providers")
async def get_providers_status(
    current_user: Dict = Depends(get_current_user)
):
    """Get status of all AI providers"""
    
    try:
        providers_status = {}
        
        for provider in ModelProvider:
            if provider == ModelProvider.FALLBACK:
                continue
                
            provider_config = model_service.config["providers"].get(provider, {})
            
            status_info = {
                "name": provider.value,
                "enabled": provider_config.get("enabled", False),
                "has_credentials": bool(provider_config.get("api_key") or provider_config.get("enabled")),
                "description": _get_provider_description(provider)
            }
            
            # Add special info for NVIDIA NIM
            if provider == ModelProvider.NVIDIA_NIM:
                status_info["credits_remaining"] = provider_config.get("credits_remaining", 0)
                status_info["free_tier"] = True
                status_info["setup_url"] = "https://build.nvidia.com/"
            
            providers_status[provider.value] = status_info
        
        return {
            "providers": providers_status,
            "total_providers": len(providers_status),
            "enabled_providers": sum(1 for p in providers_status.values() if p["enabled"])
        }
        
    except Exception as e:
        logger.error(f"Error getting provider status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get provider status: {str(e)}")

@router.get("/nvidia-nim/status")
async def get_nvidia_nim_status(
    current_user: Dict = Depends(get_current_user)
):
    """Get detailed NVIDIA NIM status and credit information"""
    
    try:
        nvidia_config = model_service.config["providers"][ModelProvider.NVIDIA_NIM]
        
        # Check available models
        nvidia_models = [
            model for model in EmbeddingModel 
            if model.value.startswith("nvidia/")
        ]
        
        available_models = []
        for model in nvidia_models:
            is_available = model_service._is_model_available(model)
            available_models.append({
                "model": model.value,
                "available": is_available,
                "dimensions": model_service._get_model_dimensions(model),
                "description": {
                    EmbeddingModel.NVIDIA_NV_EMBED_V2: "Latest generalist embedding model (RECOMMENDED)",
                    EmbeddingModel.NVIDIA_EMBED_QA_MISTRAL_7B_V2: "QA-optimized model (DEPRECATED 12/19/2025)",
                    EmbeddingModel.NVIDIA_EMBED_CODE: "Code retrieval and search model"
                }.get(model, "NVIDIA embedding model")
            })
        
        return {
            "enabled": nvidia_config.get("enabled", False),
            "has_api_key": bool(nvidia_config.get("api_key")),
            "credits_remaining": nvidia_config.get("credits_remaining", 0),
            "base_url": nvidia_config.get("base_url"),
            "available_models": available_models,
            "setup_instructions": {
                "step_1": "Visit https://build.nvidia.com/ to sign up",
                "step_2": "Get your free API key (starts with 'nvapi-')",
                "step_3": "Set NVIDIA_NIM_API_KEY environment variable",
                "step_4": "Set NVIDIA_NIM_CREDITS=1000 (your initial credits)"
            },
            "benefits": {
                "free_credits": "1,000-5,000 free API calls",
                "high_quality": "4096-dimensional embeddings",
                "openai_compatible": "Drop-in replacement for OpenAI API",
                "cost_savings": "100% savings during free tier"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting NVIDIA NIM status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get NVIDIA NIM status: {str(e)}")

def _get_provider_description(provider: ModelProvider) -> str:
    """Get human-readable description for provider"""
    descriptions = {
        ModelProvider.NVIDIA_NIM: "🚀 NVIDIA NIM - FREE CREDITS! High-quality AI models",
        ModelProvider.OPENAI: "OpenAI GPT and embedding models",
        ModelProvider.AZURE_OPENAI: "Azure OpenAI Service",
        ModelProvider.ANTHROPIC: "Anthropic Claude models",
        ModelProvider.COHERE: "Cohere embedding and generation models",
        ModelProvider.GEMINI: "Google Gemini models",
        ModelProvider.HUGGINGFACE: "HuggingFace Transformers models",
        ModelProvider.OLLAMA: "Local Ollama models",
        ModelProvider.LOCAL: "Local sentence-transformers models"
    }
    return descriptions.get(provider, "Unknown provider")

# =====================================================
# COST TRACKING ENDPOINTS
# =====================================================

@router.get("/costs", response_model=CostSummary)
async def get_cost_summary(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    current_user: Dict = Depends(get_current_user)
):
    """Get AI service cost summary"""
    
    try:
        cost_summary = model_service.get_cost_summary(days)
        
        return CostSummary(**cost_summary)
        
    except Exception as e:
        logger.error(f"Error getting cost summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cost summary: {str(e)}")

@router.get("/costs/detailed")
async def get_detailed_costs(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: Dict = Depends(get_current_user)
):
    """Get detailed cost breakdown with usage statistics"""
    
    try:
        cost_summary = model_service.get_cost_summary(days)
        
        # Add additional metrics
        detailed_costs = {
            **cost_summary,
            "cost_per_day": cost_summary["total_cost_usd"] / days if days > 0 else 0,
            "estimated_monthly_cost": cost_summary["total_cost_usd"] * (30 / days) if days > 0 else 0,
            "cost_limits": model_service.config["cost_thresholds"],
            "cache_stats": {
                "cached_embeddings": len(model_service.embedding_cache),
                "cache_hit_rate": "N/A"  # Would need to track this separately
            }
        }
        
        return detailed_costs
        
    except Exception as e:
        logger.error(f"Error getting detailed costs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get detailed costs: {str(e)}")

# =====================================================
# EMBEDDING GENERATION ENDPOINTS
# =====================================================

@router.post("/embeddings", response_model=EmbeddingResponse)
async def generate_embedding(
    request: EmbeddingRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Generate embedding using the best available model"""
    
    try:
        # Convert model name to enum if provided
        model_enum = None
        if request.model:
            try:
                model_enum = EmbeddingModel(request.model)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Unknown model: {request.model}")
        
        # Generate embedding
        embedding, metadata = await model_service.generate_embedding(
            text=request.text,
            model=model_enum,
            dimensions=request.dimensions
        )
        
        # Get list of available models for reference
        available_models = [
            model.value for model in model_service._get_available_models()
        ]
        
        return EmbeddingResponse(
            embedding=embedding,
            metadata=metadata,
            available_models=available_models
        )
        
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {str(e)}")

@router.post("/embeddings/batch")
async def generate_embeddings_batch(
    texts: List[str] = Body(..., description="List of texts to generate embeddings for"),
    model: Optional[str] = Body(None, description="Model to use for all embeddings"),
    dimensions: Optional[int] = Body(None, description="Embedding dimensions"),
    current_user: Dict = Depends(get_current_user)
):
    """Generate embeddings for multiple texts"""
    
    if len(texts) > 100:  # Limit batch size
        raise HTTPException(status_code=400, detail="Maximum batch size is 100 texts")
    
    try:
        # Convert model name to enum if provided
        model_enum = None
        if model:
            try:
                model_enum = EmbeddingModel(model)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Unknown model: {model}")
        
        results = []
        total_cost = 0.0
        
        for i, text in enumerate(texts):
            try:
                embedding, metadata = await model_service.generate_embedding(
                    text=text,
                    model=model_enum,
                    dimensions=dimensions
                )
                
                results.append({
                    "index": i,
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "embedding": embedding,
                    "metadata": metadata,
                    "success": True
                })
                
                total_cost += metadata.get("cost_usd", 0)
                
            except Exception as e:
                results.append({
                    "index": i,
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "embedding": None,
                    "metadata": {"error": str(e)},
                    "success": False
                })
        
        return {
            "results": results,
            "summary": {
                "total_texts": len(texts),
                "successful": sum(1 for r in results if r["success"]),
                "failed": sum(1 for r in results if not r["success"]),
                "total_cost_usd": total_cost
            }
        }
        
    except Exception as e:
        logger.error(f"Error in batch embedding generation: {e}")
        raise HTTPException(status_code=500, detail=f"Batch embedding failed: {str(e)}")

# =====================================================
# CONFIGURATION ENDPOINTS
# =====================================================

@router.get("/config")
async def get_model_config(
    current_user: Dict = Depends(get_current_user)
):
    """Get current AI model configuration"""
    
    try:
        config = {
            "embedding_models": [model.value for model in model_service.config["embedding_models"]],
            "cost_thresholds": model_service.config["cost_thresholds"],
            "cache_ttl_hours": model_service.config["cache_ttl_hours"],
            "max_retries": model_service.config["max_retries"],
            "timeout_seconds": model_service.config["timeout_seconds"]
        }
        
        return config
        
    except Exception as e:
        logger.error(f"Error getting model config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get config: {str(e)}")

@router.post("/config/test")
async def test_model_configuration(
    current_user: Dict = Depends(get_current_user)
):
    """Test current model configuration"""
    
    try:
        test_text = "This is a test text to verify AI model configuration"
        
        # Test each available model
        test_results = []
        
        available_models = model_service._get_available_models()
        
        for model in available_models[:5]:  # Test first 5 models
            try:
                start_time = time.time()
                embedding, metadata = await model_service.generate_embedding(
                    text=test_text,
                    model=model
                )
                test_time = time.time() - start_time
                
                test_results.append({
                    "model": model.value,
                    "success": True,
                    "dimensions": len(embedding),
                    "test_time_seconds": round(test_time, 3),
                    "cost_usd": metadata.get("cost_usd", 0),
                    "provider": metadata.get("provider", "unknown")
                })
                
            except Exception as e:
                test_results.append({
                    "model": model.value,
                    "success": False,
                    "error": str(e),
                    "test_time_seconds": 0,
                    "cost_usd": 0,
                    "provider": "unknown"
                })
        
        successful_tests = sum(1 for r in test_results if r["success"])
        
        return {
            "test_results": test_results,
            "summary": {
                "total_models_tested": len(test_results),
                "successful_models": successful_tests,
                "configuration_status": "healthy" if successful_tests > 0 else "degraded",
                "recommended_action": (
                    "Configuration is working properly" if successful_tests > 0
                    else "Check API keys and model availability"
                )
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing model configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration test failed: {str(e)}")

# =====================================================
# UTILITY ENDPOINTS
# =====================================================

@router.post("/cache/clear")
async def clear_embedding_cache(
    current_user: Dict = Depends(get_current_user)
):
    """Clear embedding cache"""
    
    # TODO: Add admin role check
    # if not current_user.get('is_superuser'):
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        cache_size_before = len(model_service.embedding_cache)
        model_service.embedding_cache.clear()
        
        return {
            "success": True,
            "message": "Embedding cache cleared",
            "cached_embeddings_removed": cache_size_before
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.get("/health")
async def ai_models_health():
    """Health check for AI models service"""
    
    try:
        # Basic health checks
        health_status = {
            "service": "ai-models",
            "status": "healthy",
            "timestamp": "2024-10-07T09:30:00Z",
            "checks": {
                "model_service_initialized": model_service is not None,
                "config_loaded": bool(model_service.config),
                "cache_functional": isinstance(model_service.embedding_cache, dict),
                "available_models": len(model_service._get_available_models())
            }
        }
        
        # Determine overall health
        all_checks_passed = all(health_status["checks"].values())
        health_status["status"] = "healthy" if all_checks_passed else "degraded"
        
        return health_status
        
    except Exception as e:
        return {
            "service": "ai-models",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-10-07T09:30:00Z"
        }