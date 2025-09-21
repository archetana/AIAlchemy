# AIAlchemy REST API Endpoints

## 🔗 Base URL
```
http://localhost:8000
```

## 📚 API Documentation
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 🏠 System Endpoints

### Health & Status
```bash
# Health Check
curl http://localhost:8000/health

# API Status
curl http://localhost:8000/api/status

# Service Info
curl http://localhost:8000/
```

---

## 📊 Dashboard API (`/api/dashboard/`)

### Dashboard Stats
```bash
# Complete dashboard metrics
curl http://localhost:8000/api/dashboard/stats

# Fast overview (key metrics only)
curl http://localhost:8000/api/dashboard/overview
```

**Response includes:**
- Total applications count
- Applications in AI processing
- Completed evaluations
- Average AI score
- Recent applications
- Pipeline metrics

---

## 🚀 Startups API (`/api/startups/`)

### List Startups (Paginated with Filtering)
```bash
# Basic list (first page, 20 items)
curl "http://localhost:8000/api/startups/"

# Paginated with custom page size
curl "http://localhost:8000/api/startups/?page=1&page_size=5"

# Filter by status
curl "http://localhost:8000/api/startups/?status=ai_analysis"

# Filter by industry
curl "http://localhost:8000/api/startups/?industry_id=1"

# Filter by AI score range
curl "http://localhost:8000/api/startups/?min_ai_score=80&max_ai_score=95"

# Search by company name/email
curl "http://localhost:8000/api/startups/?search=TechFlow"

# Combined filters with sorting
curl "http://localhost:8000/api/startups/?status=completed&sort_by=ai_score&sort_order=desc&page_size=10"
```

### Startup Details
```bash
# Get specific startup
curl http://localhost:8000/api/startups/1

# Get startup with all related data
curl http://localhost:8000/api/startups/2
```

### Create Startup
```bash
# Create new startup application
curl -X POST http://localhost:8000/api/startups/ \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "New Startup Co",
    "contact_email": "founder@newstartup.com",
    "contact_name": "John Doe", 
    "website": "https://newstartup.com",
    "industry_id": 1,
    "funding_stage": "seed",
    "funding_amount_requested": 5000000
  }'
```

### Update Startup
```bash
# Update startup status
curl -X PUT http://localhost:8000/api/startups/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "ai_analysis",
    "ai_score": 85.5
  }'
```

### Quick Stats
```bash
# Count startups by status
curl http://localhost:8000/api/startups/status/new/count

# Search suggestions (autocomplete)
curl "http://localhost:8000/api/startups/search/suggestions?query=Tech&limit=5"
```

---

## 🏭 Pipeline API (`/api/pipeline/`)

### Pipeline Analytics
```bash
# Complete pipeline statistics
curl http://localhost:8000/api/pipeline/stats

# Kanban board data (applications by stage)
curl http://localhost:8000/api/pipeline/stages

# Bottleneck analysis
curl http://localhost:8000/api/pipeline/bottlenecks

# Throughput metrics (default 30 days)
curl http://localhost:8000/api/pipeline/throughput

# Throughput for specific period
curl "http://localhost:8000/api/pipeline/throughput?days=7"
```

### Status Management
```bash
# Update application status
curl -X PUT http://localhost:8000/api/pipeline/applications/1/status \
  -H "Content-Type: application/json" \
  -d '"manual_review"'

# Update status with notes
curl -X PUT "http://localhost:8000/api/pipeline/applications/1/status?notes=Moving to manual review after AI analysis" \
  -H "Content-Type: application/json" \
  -d '"manual_review"'
```

---

## 📝 Investment Memos API (`/api/memos/`)

### Memo Management
```bash
# Get memo for specific startup
curl http://localhost:8000/api/memos/startup/1

# List all memos (paginated)
curl "http://localhost:8000/api/memos/?page=1&page_size=10"

# Filter memos by status
curl "http://localhost:8000/api/memos/?is_draft=false&approved=true"

# Get specific memo by ID
curl http://localhost:8000/api/memos/1
```

### Create Investment Memo
```bash
# Create new memo
curl -X POST "http://localhost:8000/api/memos/?author_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "startup_application_id": 2,
    "executive_summary": "Promising AI startup with strong technical team...",
    "investment_highlights": "• Strong product-market fit\n• Experienced team",
    "market_analysis": "Large addressable market in AI space...",
    "recommendation": "Strong Invest",
    "recommended_investment": 3000000,
    "proposed_valuation": 15000000
  }'
```

### Update Memo
```bash
# Update memo content
curl -X PUT http://localhost:8000/api/memos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "executive_summary": "Updated executive summary...",
    "is_draft": false
  }'
```

### Memo Workflow
```bash
# Approve memo
curl -X POST http://localhost:8000/api/memos/1/approve

# Schedule partner review
curl -X POST "http://localhost:8000/api/memos/1/schedule-review?review_date=2024-02-15"

# Get memo statistics
curl http://localhost:8000/api/memos/stats/summary
```

---

## 📁 File Uploads API (`/api/uploads/`)

### File Management
```bash
# Upload files for startup (multipart form)
curl -X POST http://localhost:8000/api/uploads/startup/1/files \
  -F "file_type=pitch_deck" \
  -F "files=@pitch_deck.pdf" \
  -F "files=@financial_model.xlsx"

# Get all files for startup
curl http://localhost:8000/api/uploads/startup/1/files

# Filter files by type
curl "http://localhost:8000/api/uploads/startup/1/files?file_type=pitch_deck"

# Download specific file
curl -O http://localhost:8000/api/uploads/files/1

# Get file processing status
curl http://localhost:8000/api/uploads/files/1/processing-status
```

### File Processing
```bash
# Trigger data extraction
curl -X POST http://localhost:8000/api/uploads/files/1/extract-data

# Delete file
curl -X DELETE http://localhost:8000/api/uploads/files/1

# Upload statistics
curl http://localhost:8000/api/uploads/stats/summary
```

---

## ⚙️ Settings API (`/api/settings/`)

### User Management
```bash
# Get current user profile
curl http://localhost:8000/api/settings/users/me

# Update user profile
curl -X PUT http://localhost:8000/api/settings/users/me \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Smith Updated",
    "title": "Senior Investment Analyst",
    "phone": "+1-555-0199"
  }'

# Get all users (admin)
curl http://localhost:8000/api/settings/users
```

### System Configuration
```bash
# Get investment weights
curl http://localhost:8000/api/settings/investment-weights

# Update investment weights
curl -X PUT http://localhost:8000/api/settings/investment-weights \
  -H "Content-Type: application/json" \
  -d '{
    "market_size_weight": 30.0,
    "team_experience_weight": 25.0,
    "business_model_weight": 20.0,
    "traction_weight": 15.0,
    "financial_health_weight": 10.0
  }'

# Get industries list
curl http://localhost:8000/api/settings/industries

# Get system information
curl http://localhost:8000/api/settings/system/info
```

### Account Preferences
```bash
# Get account preferences
curl http://localhost:8000/api/settings/account/preferences

# Update preferences
curl -X PUT http://localhost:8000/api/settings/account/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "notifications": {
      "email_notifications": true,
      "desktop_notifications": false
    },
    "display": {
      "theme": "dark"
    }
  }'
```

---

## 🧪 Testing the APIs

### Start the Server
```bash
cd /home/user/webapp/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Run Comprehensive Tests
```bash
cd /home/user/webapp/backend
python test_api.py
```

### Quick Health Check
```bash
# Test all basic endpoints
curl http://localhost:8000/health && echo ""
curl http://localhost:8000/api/dashboard/overview && echo ""
curl "http://localhost:8000/api/startups/?page_size=2" && echo ""
curl http://localhost:8000/api/pipeline/stats && echo ""
curl http://localhost:8000/api/settings/investment-weights && echo ""
```

---

## 📊 Sample Responses

### Dashboard Overview
```json
{
  "success": true,
  "data": {
    "total_applications": 8,
    "ai_processing": 3,
    "completed_analysis": 2,
    "average_score": 81.8
  }
}
```

### Startups List
```json
{
  "items": [
    {
      "id": 1,
      "company_name": "TechFlow AI",
      "status": "ai_analysis", 
      "ai_score": 83.07,
      "funding_stage": "series_a",
      "created_at": "2024-12-01T10:30:00"
    }
  ],
  "total": 8,
  "page": 1,
  "page_size": 20,
  "pages": 1,
  "has_next": false,
  "has_prev": false
}
```

### Pipeline Stats
```json
{
  "success": true,
  "data": {
    "stages": {
      "new": 2,
      "ai_analysis": 3,
      "manual_review": 2,
      "completed": 1
    },
    "conversion_rates": {
      "ai_analysis": 85.7,
      "manual_review": 73.2
    },
    "avg_days_per_stage": {
      "ai_analysis": 3.8,
      "manual_review": 7.5
    },
    "weekly_throughput": 2
  }
}
```

---

## 🔍 Key Features for Testing

1. **Pagination** - All list endpoints support page/page_size parameters
2. **Filtering** - Multiple filter combinations on startups
3. **Search** - Text search across company names and contacts  
4. **Sorting** - Configurable sort fields and order
5. **Status Management** - Update pipeline status with history tracking
6. **File Uploads** - Multi-file upload with progress tracking
7. **Analytics** - Pre-calculated metrics for fast dashboard loading
8. **Validation** - Comprehensive request validation and error handling

The API is fully functional and ready for frontend integration! 🚀