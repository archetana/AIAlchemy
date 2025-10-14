# Document AI Solutions Comparison: Google Document AI vs Landing AI

## Executive Summary

| Aspect | Google Document AI | Landing AI Agentic Document Extraction |
|--------|-------------------|----------------------------------------|
| **Best For** | High-volume processing, enterprise features | Intelligent extraction, agentic workflows |
| **Starting Cost** | $0.0015/page (OCR only) | $0.01/page (full parsing) |
| **Free Tier** | No free tier | 1,000 free credits |
| **Cheapest Option** | ✅ Google Document AI | Landing AI ADE |

## Detailed Pricing Breakdown

### **Google Document AI Pricing**

#### OCR (Text Digitization)
- **1-5M pages/month**: $1.50/1,000 pages = **$0.0015/page**
- **5M+ pages/month**: $0.60/1,000 pages = **$0.0006/page**

#### Structured Extraction 
- **Custom Extractor**: $30/1,000 pages = **$0.03/page** (1-1M pages)
- **Form Parser**: $30/1,000 pages = **$0.03/page** (1-1M pages)
- **Layout Parser**: $10/1,000 pages = **$0.01/page**

#### Specialized Processors
- **Invoice Parser**: $0.10 per document (up to 10 pages)
- **Receipt Parser**: $0.10 per document (up to 10 pages)
- **Bank Statement**: $0.75 per document
- **Custom Processor Hosting**: $0.05/hour = **$438/year per processor**

### **Landing AI ADE Pricing**

#### Credit System
- **Explore Plan**: $1 = 100 credits ($0.01/credit) + 1,000 free credits
- **Team Plan**: $1 = 110 credits ($250/month minimum)
- **Visionary Plan**: $1 = 130 credits ($2,000/month minimum)

#### Processing Costs
- **Parse API**: 3 credits/page = **$0.03/page** (Explore)
- **Extract API**: 1 credit/5,000 input chars + 1 credit/1,000 output chars
- **Zero Data Retention**: +1 credit/page (HIPAA compliance)

## Cost Scenarios Analysis

### **Scenario 1: Small Startup (100 pages/month)**

| Solution | Monthly Cost | Annual Cost | Notes |
|----------|--------------|-------------|--------|
| Google OCR only | $0.15 | $1.80 | Text extraction only |
| Google Form Parser | $3.00 | $36.00 | Structured extraction |
| Landing AI (free tier) | $0.00 | $0.00 | First 10 months free |
| Landing AI (paid) | $3.00 | $36.00 | After free credits |

**Winner**: Landing AI (free tier covers 10 months)

### **Scenario 2: Growing Company (1,000 pages/month)**

| Solution | Monthly Cost | Annual Cost | Notes |
|----------|--------------|-------------|--------|
| Google OCR | $1.50 | $18.00 | Basic OCR |
| Google Form Parser | $30.00 | $360.00 | Structured data |
| Landing AI Explore | $30.00 | $360.00 | Pay-as-you-go |
| Landing AI Team | $250.00 | $3,000.00 | Minimum commitment |

**Winner**: Google Document AI (OCR) or Landing AI Explore (structured)

### **Scenario 3: Enterprise (10,000 pages/month)**

| Solution | Monthly Cost | Annual Cost | Notes |
|----------|--------------|-------------|--------|
| Google Form Parser | $300.00 | $3,600.00 | Structured extraction |
| Google OCR + Custom | $351.50 | $4,218.00 | Including hosting fee |
| Landing AI Team | $300.00 | $3,600.00 | 27,273 credits/month |
| Landing AI Visionary | $2,000.00 | $24,000.00 | 260,000 credits/month |

**Winner**: Tie between Google and Landing AI Team plan

## Storage Solutions for Extraction Results

### **Option 1: Supabase PostgreSQL (Recommended for You) 💰**

```sql
-- Add document extraction table to your existing schema
CREATE TABLE document_extractions (
    id SERIAL PRIMARY KEY,
    startup_application_id INTEGER REFERENCES startup_applications(id),
    original_filename VARCHAR(255) NOT NULL,
    file_url VARCHAR(500),
    extraction_service VARCHAR(50) NOT NULL, -- 'google_document_ai' or 'landing_ai'
    extraction_type VARCHAR(100) NOT NULL,  -- 'form_parser', 'invoice', 'pitch_deck', etc.
    
    -- Raw extraction results
    raw_response JSONB NOT NULL,           -- Full API response
    structured_data JSONB,                 -- Cleaned/processed data
    extracted_text TEXT,                   -- Plain text content
    
    -- Metadata
    page_count INTEGER,
    processing_cost_cents INTEGER,        -- Cost in cents for tracking
    processing_time_ms INTEGER,           -- Performance tracking
    confidence_score DECIMAL(5,2),        -- AI confidence (0-100)
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'processing', -- processing, completed, failed
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for queries
CREATE INDEX idx_document_extractions_startup ON document_extractions(startup_application_id);
CREATE INDEX idx_document_extractions_status ON document_extractions(status);
CREATE INDEX idx_document_extractions_type ON document_extractions(extraction_type);
```

**Cost**: ~$0 (included in existing Supabase plan)

### **Option 2: Google Cloud Storage + Firestore**

```python
# Store large documents in GCS, metadata in Firestore
{
    "document_id": "doc_123",
    "startup_id": "startup_456", 
    "gcs_path": "gs://bucket/extractions/doc_123.json",
    "extraction_summary": {"fields": 15, "confidence": 0.92},
    "cost_cents": 300,
    "created_at": "2024-10-07T09:30:00Z"
}
```

**Cost**: $0.026/GB/month (GCS) + $0.18/100K reads (Firestore)

### **Option 3: Local File System + SQLite (Development Only)**

```python
# For development/testing
extraction_results/
├── startup_123/
│   ├── pitch_deck_extraction.json
│   ├── financial_docs_extraction.json
│   └── metadata.db
```

**Cost**: $0 (local storage only)

## **Recommendation: Hybrid Approach**

### **For Your Startup Application:**

1. **Start with Landing AI** for 1,000 free pages to test functionality
2. **Switch to Google Document AI** when volume increases (cheaper at scale)
3. **Store results in Supabase** (your existing database)

### **Implementation Strategy:**

```python
# backend/app/services/document_extraction_service.py
class DocumentExtractionService:
    def __init__(self):
        self.monthly_pages = self.get_monthly_usage()
        
    def choose_provider(self, document_type: str):
        """Smart provider selection based on cost and document type"""
        if self.monthly_pages < 5000:
            return "landing_ai"  # Better for low volume
        else:
            return "google_document_ai"  # Better for high volume
            
    async def extract_document(self, file_path: str, document_type: str):
        provider = self.choose_provider(document_type)
        
        if provider == "landing_ai":
            return await self.extract_with_landing_ai(file_path)
        else:
            return await self.extract_with_google_ai(file_path, document_type)
```

### **Cost Optimization Tips:**

1. **Use Google OCR** for simple text extraction ($0.0015/page)
2. **Use Landing AI** for complex document understanding
3. **Implement caching** to avoid re-processing
4. **Batch process** documents to reduce API calls
5. **Monitor usage** to switch providers at optimal thresholds

## **Next Steps:**

1. ✅ Start with Landing AI free tier (1,000 pages)
2. 🔄 Implement Supabase storage schema  
3. 📊 Track usage and costs
4. 🔀 Switch to Google Document AI when cost-effective
5. 🎯 Optimize based on actual usage patterns

**Bottom Line**: Landing AI for testing/low volume, Google Document AI for production scale, Supabase for storage = **Most cost-effective solution**