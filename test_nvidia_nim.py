#!/usr/bin/env python3
"""
NVIDIA NIM Integration Test Script

This script tests the NVIDIA NIM integration with the ModelAgnosticService
to ensure free credits are working and embeddings are generated correctly.
"""

import asyncio
import os
import sys
import logging
from typing import Dict, Any

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.model_agnostic_service import model_service, EmbeddingModel, ModelProvider

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_nvidia_nim_embedding() -> Dict[str, Any]:
    """Test NVIDIA NIM embedding generation"""
    
    print("🚀 Testing NVIDIA NIM Integration...")
    print("=" * 50)
    
    results = {
        "success": False,
        "error": None,
        "embedding_info": {},
        "cost_info": {},
        "performance_info": {}
    }
    
    try:
        # Test text
        test_text = "NVIDIA NIM provides free AI model access through developer credits for building intelligent applications"
        
        print(f"📝 Test text: {test_text[:60]}...")
        print(f"📏 Text length: {len(test_text)} characters")
        
        # Try NVIDIA NIM models in order of preference
        nvidia_models = [
            EmbeddingModel.NVIDIA_NV_EMBED_V2,
            EmbeddingModel.NVIDIA_EMBED_QA_MISTRAL_7B_V2,
            EmbeddingModel.NVIDIA_EMBED_CODE
        ]
        
        for model in nvidia_models:
            try:
                print(f"\n🔄 Testing model: {model.value}")
                
                # Check if model is available
                if not model_service._is_model_available(model):
                    print(f"❌ Model {model.value} not available")
                    continue
                
                # Generate embedding
                import time
                start_time = time.time()
                
                embedding, metadata = await model_service.generate_embedding(
                    text=test_text,
                    model=model
                )
                
                end_time = time.time()
                
                # Success!
                results["success"] = True
                results["embedding_info"] = {
                    "model": metadata['model'],
                    "provider": metadata['provider'],
                    "dimensions": len(embedding),
                    "first_10_values": embedding[:10]
                }
                results["cost_info"] = {
                    "cost_usd": metadata['cost_usd'],
                    "is_free": metadata['cost_usd'] == 0.0
                }
                results["performance_info"] = {
                    "processing_time_seconds": end_time - start_time,
                    "text_length": len(test_text),
                    "tokens_estimated": len(test_text) / 4
                }
                
                print(f"✅ SUCCESS! NVIDIA NIM Integration Working!")
                print(f"📊 Model: {metadata['model']}")
                print(f"🏭 Provider: {metadata['provider']}")
                print(f"📐 Dimensions: {len(embedding)}")
                print(f"💰 Cost: ${metadata['cost_usd']:.6f} {'(FREE with credits!)' if metadata['cost_usd'] == 0 else ''}")
                print(f"⚡ Processing time: {end_time - start_time:.3f}s")
                print(f"🎯 First 5 embedding values: {embedding[:5]}")
                
                break
                
            except Exception as model_error:
                print(f"❌ Model {model.value} failed: {model_error}")
                continue
        
        if not results["success"]:
            results["error"] = "All NVIDIA NIM models failed"
            
    except Exception as e:
        results["error"] = str(e)
        print(f"❌ NVIDIA NIM test failed: {e}")
    
    return results

async def test_model_priority() -> Dict[str, Any]:
    """Test that NVIDIA NIM models are prioritized correctly"""
    
    print("\n🎯 Testing Model Priority...")
    print("=" * 30)
    
    try:
        # Get available models in priority order
        available_models = model_service._get_available_models()
        
        print("📋 Available models in priority order:")
        for i, model in enumerate(available_models, 1):
            provider = model_service._get_model_provider(model)
            is_free = provider in [ModelProvider.NVIDIA_NIM, ModelProvider.LOCAL, ModelProvider.FALLBACK]
            cost_indicator = "💰 FREE" if is_free else "💳 PAID"
            print(f"  {i}. {model.value} ({provider.value}) {cost_indicator}")
        
        # Check if NVIDIA models come first
        nvidia_first = any(
            model.value.startswith("nvidia/") 
            for model in available_models[:3]  # Check top 3
        )
        
        if nvidia_first:
            print("✅ NVIDIA NIM models are properly prioritized!")
        else:
            print("⚠️ NVIDIA NIM models may not be available (no credits or API key?)")
        
        return {
            "nvidia_prioritized": nvidia_first,
            "available_models": [m.value for m in available_models],
            "total_available": len(available_models)
        }
        
    except Exception as e:
        print(f"❌ Priority test failed: {e}")
        return {"error": str(e)}

async def check_nvidia_configuration() -> Dict[str, Any]:
    """Check NVIDIA NIM configuration"""
    
    print("\n🔧 Checking NVIDIA NIM Configuration...")
    print("=" * 40)
    
    config_status = {
        "api_key_set": False,
        "base_url_set": False,
        "credits_configured": False,
        "provider_enabled": False,
        "recommendations": []
    }
    
    try:
        # Check environment variables
        api_key = os.getenv("NVIDIA_NIM_API_KEY")
        base_url = os.getenv("NVIDIA_NIM_BASE_URL")
        credits = os.getenv("NVIDIA_NIM_CREDITS")
        
        config_status["api_key_set"] = bool(api_key)
        config_status["base_url_set"] = bool(base_url)
        config_status["credits_configured"] = bool(credits)
        
        print(f"🔑 NVIDIA_NIM_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
        print(f"🌐 NVIDIA_NIM_BASE_URL: {'✅ Set' if base_url else '❌ Using default'}")
        print(f"💳 NVIDIA_NIM_CREDITS: {'✅ Set' if credits else '❌ Not configured'}")
        
        if api_key:
            print(f"🔍 API Key preview: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else ''}")
        
        # Check provider configuration
        nvidia_config = model_service.config["providers"][ModelProvider.NVIDIA_NIM]
        config_status["provider_enabled"] = nvidia_config["enabled"]
        
        print(f"⚙️ Provider enabled: {'✅ Yes' if nvidia_config['enabled'] else '❌ No'}")
        
        if nvidia_config["enabled"]:
            credits_remaining = nvidia_config.get("credits_remaining", 0)
            print(f"💰 Credits remaining: {credits_remaining}")
            
            if credits_remaining <= 0:
                config_status["recommendations"].append("Set NVIDIA_NIM_CREDITS=1000 (or your actual credit balance)")
        
        # Generate recommendations
        if not api_key:
            config_status["recommendations"].append("Get API key from https://build.nvidia.com/")
        if not credits:
            config_status["recommendations"].append("Set NVIDIA_NIM_CREDITS environment variable")
        
        if config_status["recommendations"]:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(config_status["recommendations"], 1):
                print(f"  {i}. {rec}")
        
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
        config_status["error"] = str(e)
    
    return config_status

async def run_comprehensive_test():
    """Run all NVIDIA NIM tests"""
    
    print("🧪 NVIDIA NIM Comprehensive Test Suite")
    print("=" * 50)
    
    # Test 1: Configuration Check
    config_results = await check_nvidia_configuration()
    
    # Test 2: Model Priority
    priority_results = await test_model_priority() 
    
    # Test 3: Embedding Generation (only if configured)
    embedding_results = None
    if config_results.get("provider_enabled"):
        embedding_results = await test_nvidia_nim_embedding()
    else:
        print("\n⚠️ Skipping embedding test - NVIDIA NIM not configured")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    print(f"🔧 Configuration: {'✅ OK' if config_results.get('api_key_set') else '❌ Needs setup'}")
    print(f"🎯 Model Priority: {'✅ OK' if priority_results.get('nvidia_prioritized') else '⚠️ Check config'}")
    
    if embedding_results:
        print(f"🚀 Embedding Test: {'✅ SUCCESS' if embedding_results.get('success') else '❌ FAILED'}")
        if embedding_results.get("success"):
            dims = embedding_results["embedding_info"]["dimensions"]
            cost = embedding_results["cost_info"]["cost_usd"]
            print(f"   📐 Dimensions: {dims}")
            print(f"   💰 Cost: ${cost:.6f}")
    else:
        print("🚀 Embedding Test: ⏭️ Skipped")
    
    # Next steps
    if not config_results.get("api_key_set"):
        print("\n🎯 NEXT STEPS:")
        print("1. Visit https://build.nvidia.com/ to get your free API key")
        print("2. Set NVIDIA_NIM_API_KEY environment variable")
        print("3. Set NVIDIA_NIM_CREDITS=1000 (your initial credit balance)")
        print("4. Run this test again!")
    elif embedding_results and embedding_results.get("success"):
        print("\n🎉 SUCCESS! NVIDIA NIM is working perfectly!")
        print("💡 Your application will now use FREE NVIDIA NIM credits first!")
    else:
        print("\n🔧 Some issues detected - check the logs above for details")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())