# API Keys Configuration for Document AI

## 🔑 **Required API Keys for Full Functionality**

### **1. OpenAI API Key (Recommended)**
- **Purpose**: High-quality embeddings for semantic search
- **Cost**: ~$0.0001 per 1000 tokens for embeddings
- **Get Key**: https://platform.openai.com/api-keys
- **Add to GitHub Secrets**: `OPENAI_API_KEY`

### **2. Landing AI API Key (Recommended for start)**
- **Purpose**: Document extraction with 1000 free credits
- **Cost**: $0.03/page after free tier
- **Get Key**: https://landing.ai/
- **Add to GitHub Secrets**: `LANDING_AI_API_KEY`

### **3. Google Cloud Project (For Document AI)**
- **Purpose**: High-volume document processing
- **Cost**: $0.0015-$0.03/page depending on service
- **Setup**: Already configured in your project
- **Keys**: `GOOGLE_CLOUD_PROJECT`, `DOCUMENT_AI_PROCESSOR_ID`

## 📝 **How to Add Keys to GitHub Secrets**

1. **Go to your GitHub repository**: https://github.com/archetana/AIAlchemy
2. **Navigate to**: Settings → Secrets and variables → Actions
3. **Click**: "New repository secret"
4. **Add each key**:

```bash
Name: OPENAI_API_KEY
Value: sk-your-openai-api-key-here

Name: LANDING_AI_API_KEY  
Value: your-landing-ai-key-here

Name: DOCUMENT_AI_PROCESSOR_ID
Value: your-processor-id-here
```

## 🚀 **Without API Keys (Current Setup)**

Your vector database will work with:
- ✅ **Fallback embeddings**: Deterministic hash-based embeddings
- ✅ **Semantic search**: Basic similarity matching
- ✅ **Document storage**: Full vector database functionality
- ✅ **Manual extraction**: Upload pre-extracted text

## 💰 **Cost Comparison**

| Service | Free Tier | Cost After Free | Best For |
|---------|-----------|----------------|----------|
| **Landing AI** | 1000 pages ($30 value) | $0.03/page | Starting out, complex docs |
| **OpenAI Embeddings** | None | $0.0001/1K tokens | High-quality search |
| **Google Document AI** | None | $0.0015-$0.03/page | High volume |

## 🎯 **Recommendation**

1. **Start Free**: Use the system without API keys first
2. **Add OpenAI**: For better semantic search ($5-10/month typical usage)
3. **Add Landing AI**: When you need document extraction (free tier first)
4. **Add Google AI**: When processing >5K pages/month

Your vector database is fully functional without any API keys!