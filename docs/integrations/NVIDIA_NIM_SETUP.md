# NVIDIA NIM Integration Setup Guide

## 🚀 Quick Start - Get FREE AI Credits!

NVIDIA NIM offers **1,000-5,000 FREE API credits** for embedding and AI model access. This guide will help you integrate NVIDIA NIM with your existing model-agnostic service to leverage these free credits.

## 📋 Prerequisites

1. **NVIDIA Developer Program Membership** (Free - 5M+ members)
2. **NVIDIA API Catalog Account** (Free signup at build.nvidia.com)
3. **Python dependencies**: `httpx` for async HTTP requests

## 🔧 Step 1: Get Your NVIDIA NIM API Key

### 1.1 Sign Up for NVIDIA Developer Program
```bash
# Visit: https://developer.nvidia.com/developer-program
# Sign up for free (if not already a member)
```

### 1.2 Access NVIDIA API Catalog
```bash
# Visit: https://build.nvidia.com/
# Sign in with your NVIDIA Developer account
# You'll receive 1,000 FREE credits immediately
```

### 1.3 Generate API Key
1. Go to https://build.nvidia.com/
2. Click on any model (e.g., "nvidia/nv-embed-v2")
3. Click "Get API Key" button
4. Copy your API key (starts with "nvapi-")

## 🔐 Step 2: Configure Environment Variables

Add these environment variables to your `.env` file:

```bash
# NVIDIA NIM Configuration
NVIDIA_NIM_API_KEY=nvapi-your-api-key-here
NVIDIA_NIM_BASE_URL=https://api.nvcf.nvidia.com/v2/nvcf
NVIDIA_NIM_CREDITS=1000  # Track your remaining credits

# Optional: Disable other providers to force NIM usage
# OPENAI_API_KEY=  # Leave empty to use NIM first
```

## 🔄 Step 3: Install Additional Dependencies

```bash
cd /home/agenticai/webapp/backend
pip install httpx  # For async HTTP requests to NVIDIA NIM API
```

## 🎯 Step 4: Test NVIDIA NIM Integration

Create a test script to verify the integration:

```python
# test_nvidia_nim.py
import asyncio
import os
from app.services.model_agnostic_service import model_service, EmbeddingModel

async def test_nvidia_nim():
    try:
        # Test NVIDIA NIM embedding
        text = "NVIDIA NIM provides free AI model access through developer credits"
        
        embedding, metadata = await model_service.generate_embedding(
            text=text,
            model=EmbeddingModel.NVIDIA_NV_EMBED_V2
        )
        
        print(f"✅ NVIDIA NIM Integration Successful!")
        print(f"📊 Embedding dimensions: {len(embedding)}")
        print(f"💰 Cost: ${metadata['cost_usd']:.6f} (FREE with credits!)")
        print(f"🚀 Model: {metadata['model']}")
        print(f"⚡ Processing time: {metadata['processing_time_seconds']:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ NVIDIA NIM test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_nvidia_nim())
```

Run the test:
```bash
cd /home/agenticai/webapp
python test_nvidia_nim.py
```

## 📊 Available NVIDIA Models

| Model | Dimensions | Use Case | Status |
|-------|------------|----------|--------|
| **nvidia/nv-embed-v2** | 4096 | **Generalist embedding (RECOMMENDED)** | ✅ Active |
| nvidia/nv-embedqa-mistral-7b-v2 | 4096 | Question-answering, RAG | ⚠️ Deprecated 12/19/2025 |
| nvidia/nv-embedcode | 4096 | Code retrieval and search | ✅ Active |

## 💡 Model Priority Configuration

The ModelAgnosticService now prioritizes models in this order:

1. **🥇 NVIDIA NIM models** (FREE with credits)
2. **🥈 Local models** (Free, always available)  
3. **🥉 OpenAI/Cohere** (Paid fallback)

This ensures you maximize your free credit usage!

## 🔍 Monitoring Credit Usage

Track your NVIDIA NIM credit usage:

```python
# Check remaining credits
nvidia_config = model_service.config["providers"]["nvidia_nim"]
credits_remaining = nvidia_config.get("credits_remaining", 0)
print(f"NVIDIA NIM credits remaining: {credits_remaining}")

# Get cost summary (NVIDIA will show $0.00)
cost_summary = model_service.get_cost_summary(days=7)
print(f"Weekly AI costs: ${cost_summary['total_cost_usd']:.2f}")
```

## ⚠️ Important Notes

### Credit Limits
- **Initial credits**: 1,000 upon signup
- **Maximum free credits**: 5,000 total per account
- **No automatic renewal**: Credits don't replenish automatically

### Model Deprecation
- `nv-embedqa-mistral-7b-v2` is **deprecated** as of 12/19/2025
- Use `nvidia/nv-embed-v2` as the primary model
- The system will automatically fall back to other models if credits are exhausted

### Performance Benefits
- **High-quality embeddings**: 4096 dimensions vs 1536 for OpenAI
- **Fast processing**: Optimized with TensorRT
- **OpenAI compatibility**: Drop-in replacement for OpenAI API calls

## 🚨 Troubleshooting

### Common Issues

1. **"No NVIDIA NIM credits remaining"**
   ```bash
   # Solution: System will automatically fall back to local models or other providers
   # Check credit status in logs
   ```

2. **"NVIDIA NIM embedding failed"**
   ```bash
   # Check API key configuration
   echo $NVIDIA_NIM_API_KEY
   
   # Verify network connectivity
   curl -H "Authorization: Bearer $NVIDIA_NIM_API_KEY" \
        https://api.nvcf.nvidia.com/v2/nvcf/functions
   ```

3. **"Model not available"**
   ```bash
   # Check if model is still active (some models get deprecated)
   # System will automatically try next available model
   ```

### Debug Logging

Enable debug logging to see NVIDIA NIM credit usage:

```python
import logging
logging.getLogger("app.services.model_agnostic_service").setLevel(logging.DEBUG)
```

## 🎉 Next Steps

1. **Deploy to production**: Set `NVIDIA_NIM_CREDITS=5000` in production environment
2. **Monitor usage**: Set up alerts when credits drop below 100
3. **Optimize costs**: Use NVIDIA NIM for high-quality embeddings, local models for bulk processing
4. **Scale up**: Apply for NVIDIA AI Enterprise license for production workloads

## 💰 Cost Savings Summary

With NVIDIA NIM integration, you can achieve:
- **100% cost reduction** for embedding generation (during free credit period)
- **Higher quality embeddings** (4096 vs 1536 dimensions)  
- **Automatic fallback** to local/paid models when credits exhausted
- **Production-ready performance** with TensorRT optimization

**Estimated savings**: $10-50/month depending on usage volume!

---

✅ **Your NVIDIA NIM integration is now complete!** 

The system will automatically use NVIDIA NIM models first, maximizing your free credits while maintaining high performance and automatic fallbacks.