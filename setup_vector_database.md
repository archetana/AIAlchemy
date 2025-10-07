# Vector Database Setup Guide

## 🎯 **Solution Summary: Vector Database for Document Extraction**

### **Why Vector Database is Better for Your Use Case**

✅ **Semantic Search**: Find documents by meaning, not just keywords  
✅ **AI-Powered Queries**: Ask natural language questions about documents  
✅ **Similarity Matching**: Find similar companies, compare documents  
✅ **RAG Integration**: Perfect for AI analysis and investment insights  
✅ **Scalability**: Handle growing document volumes efficiently  
✅ **Cost-Effective**: Using Supabase + pgvector = $0 additional cost  

## 💰 **Cost Comparison & Recommendation**

### **Document AI Services:**
| Service | Cost | Best For | Recommendation |
|---------|------|----------|---------------|
| **Landing AI** | $0.03/page | Complex extraction, low volume | ✅ **Start here** (1000 free pages) |
| **Google Doc AI** | $0.0015/page (OCR) to $0.03/page (extraction) | High volume, enterprise | Switch when >5K pages/month |

### **Storage Solution:**
| Option | Cost | Pros | Cons |
|--------|------|------|------|
| **Supabase + pgvector** | **$0** | Existing setup, SQL queries, hybrid search | Limited vector operations |
| **Pinecone** | $70+/month | Full-featured, fast | Expensive, vendor lock-in |
| **ChromaDB** | $0 (self-hosted) | Free, simple | Not managed, scaling issues |

**🏆 Winner**: **Supabase + pgvector** (already included in your plan)

## 🚀 **Implementation Steps**

### **Step 1: Enable Vector Extension in Supabase**

1. Go to your Supabase Dashboard → SQL Editor
2. Run this command:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### **Step 2: Set Up Vector Schema**

Execute the schema file in Supabase SQL Editor:
```bash
# File: backend/vector_document_schema.sql
# Copy contents and paste in Supabase SQL Editor
```

### **Step 3: Configure Environment Variables**

Add to your GitHub Secrets:
```bash
OPENAI_API_KEY=your_openai_key_here  # For embeddings
LANDING_AI_API_KEY=your_landing_ai_key  # Optional
GOOGLE_CLOUD_PROJECT=your_project_id    # For Document AI
```

### **Step 4: Deploy Updated Backend**

Your backend now includes:
- ✅ Vector document service (`backend/app/services/vector_document_service.py`)
- ✅ Vector API endpoints (`backend/app/api/v1/vector_documents.py`)
- ✅ Document AI integration (`backend/integrate_document_ai.py`)
- ✅ Main app updated to include vector routes

## 🔧 **API Endpoints Available**

### **Document Upload & Processing:**
```bash
POST /vector-documents/upload
# Upload document, extract with AI, store in vector DB
```

### **Semantic Search:**
```bash
POST /vector-documents/search
{
  "query": "companies with AI technology in healthcare",
  "search_type": "hybrid",
  "similarity_threshold": 0.7,
  "max_results": 10
}
```

### **Find Similar Companies:**
```bash
GET /vector-documents/search/similar-companies?startup_id=123
# Find companies with similar pitch decks/documents
```

### **Document Management:**
```bash
GET /vector-documents/startup/{startup_id}    # Get all docs for startup
DELETE /vector-documents/{document_id}        # Archive document
GET /vector-documents/stats                   # Usage statistics
```

## 📊 **Usage Examples**

### **Example 1: Upload and Process Document**
```python
import requests

# Upload a pitch deck
files = {'file': open('pitch_deck.pdf', 'rb')}
data = {
    'startup_id': 123,
    'document_type': 'pitch_deck',
    'extraction_service': 'landing_ai'
}

response = requests.post(
    'https://your-app.run.app/vector-documents/upload',
    files=files,
    data=data,
    headers={'Authorization': 'Bearer YOUR_JWT_TOKEN'}
)
```

### **Example 2: Semantic Search**
```python
# Find documents about AI in healthcare
search_query = {
    "query": "artificial intelligence healthcare medical diagnosis",
    "search_type": "hybrid",
    "similarity_threshold": 0.7,
    "max_results": 5
}

response = requests.post(
    'https://your-app.run.app/vector-documents/search',
    json=search_query,
    headers={'Authorization': 'Bearer YOUR_JWT_TOKEN'}
)

# Results include similarity scores, snippets, structured data
for result in response.json():
    print(f"Company: {result['filename']}")
    print(f"Similarity: {result['similarity_score']:.2f}")
    print(f"Snippet: {result['text_snippet'][:200]}...")
```

### **Example 3: Find Similar Companies**
```python
# Find companies similar to startup ID 123
response = requests.get(
    'https://your-app.run.app/vector-documents/search/similar-companies',
    params={
        'startup_id': 123,
        'document_type': 'pitch_deck',
        'similarity_threshold': 0.8,
        'max_results': 5
    },
    headers={'Authorization': 'Bearer YOUR_JWT_TOKEN'}
)

# Use for competitive analysis, market research
similar_companies = response.json()['similar_companies']
```

## 🎯 **Business Value**

### **For Investment Analysis:**
- **Smart Search**: "Find SaaS companies with $1M+ ARR in fintech"
- **Competitive Analysis**: Automatically find similar companies
- **Due Diligence**: Compare financial metrics across similar startups
- **Market Research**: Identify trends and patterns in documents

### **For Document Processing:**
- **Automatic Extraction**: Pull key metrics from pitch decks
- **Standardization**: Convert varied formats to structured data  
- **Quality Control**: Confidence scores for AI extractions
- **Audit Trail**: Track processing costs and performance

### **For User Experience:**
- **Natural Language Queries**: Ask questions in plain English
- **Instant Insights**: Get answers from document corpus
- **Visual Similarity**: Find companies with similar profiles
- **Smart Recommendations**: Suggest relevant documents/companies

## 🔍 **Next Steps**

### **Immediate (Deploy Now):**
1. ✅ Fixed Supabase deployment (removed SQLite override)
2. ✅ Vector database schema ready
3. ✅ API endpoints implemented
4. 🔄 **Deploy to production** - your app will now use Supabase + vectors

### **Testing Phase (After Deploy):**
1. Enable pgvector extension in Supabase
2. Run vector schema setup
3. Upload a sample document
4. Test semantic search
5. Verify similar company matching

### **Production Optimization:**
1. Add OpenAI API key for better embeddings
2. Configure Landing AI for advanced extraction
3. Set up batch processing for large volumes
4. Implement usage analytics and cost tracking

## 💡 **Why This Solution is Perfect for You**

1. **Zero Additional Cost**: Uses existing Supabase plan
2. **Incremental Adoption**: Start simple, add AI services as needed
3. **Proven Technology**: PostgreSQL + vectors is battle-tested
4. **Future-Proof**: Scales with your business growth
5. **Hybrid Approach**: Best of both RDBMS and vector search

Your startup evaluation platform now has **enterprise-grade document intelligence** at **startup costs**! 🚀