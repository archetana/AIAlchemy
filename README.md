# AIAlchemy - AI Analyst for Startup Evaluation

[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://python.org/)
[![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org/)

> **AI-powered startup evaluation platform that automates due diligence, conducts AI interviews, and generates investment-ready memos in under 4 minutes.**

## 🚀 Quick Start

### Production Deployment (Recommended)

**Step 1: Set up Google Cloud Storage**
```bash
# Clone the repository
git clone https://github.com/archetana/AIAlchemy.git
cd AIAlchemy

# Validate GCS setup (creates instructions if needed)
python3 setup-gcs-complete.py
```

**Step 2: Deploy to Google Cloud Platform**
```bash
# Authenticate with Google Cloud
gcloud auth login && gcloud auth application-default login

# Deploy with nginx gateway (no domain required)
./deploy-nginx-gateway.sh
```

**What you get**: Backend API + Frontend Dashboard + Nginx Gateway + GCS Storage = Single URL (~$25/month)

### Local Development

```bash
# Backend setup
cd backend && pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# Frontend setup (new terminal)
cd frontend && npm install && npm start

# Visit http://localhost:3000
```

## ✨ Key Features

### 🔄 Multi-Format Processing
- **Pitch Deck Analysis** (PDF/PPT) with financial extraction
- **Video Pitch Processing** with AI transcription
- **Voice Memo Analysis** with sentiment detection
- **Smart Forms** with auto-completion

### 🤖 AI-Powered Evaluation
- **Automated Due Diligence** with risk assessment
- **AI Founder Interviews** with dynamic questioning
- **Market Intelligence** with competitor analysis
- **Investment Memo Generation** in minutes

### 📊 Analytics Dashboard
- **Deal Flow Management** with Kanban pipeline
- **Performance Metrics** and success tracking
- **Sector Analysis** with benchmarking
- **Team Collaboration** with comments and notes

## 🏗️ Architecture

### System Components
```
Frontend (React/TypeScript) → Nginx Gateway → Backend (FastAPI/Python)
                                    ↓
                            Database (SQLite/PostgreSQL)
                                    ↓
                        Google Cloud AI Services (Vertex AI, Gemini)
```

### Multi-Agent AI System
- **Data Ingestion Agent**: Document and media processing
- **Market Intelligence Agent**: Competitor and market research
- **Interview Agent**: AI-powered founder interviews
- **Risk Assessment Agent**: ML-based risk evaluation
- **Memo Generator Agent**: Investment memo creation

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI + Python 3.11+ | High-performance API |
| **Frontend** | React 18+ + TypeScript | Modern web interface |
| **Database** | SQLite/PostgreSQL | Data persistence |
| **AI/ML** | Google Cloud Vertex AI | AI capabilities |
| **Deployment** | Google Cloud Run | Serverless containers |
| **CI/CD** | GitHub Actions | Automated deployment |

## 📁 Project Structure

```
AIAlchemy/
├── README.md                    # This file
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py             # Application entry point
│   │   ├── agents/             # Multi-agent AI system
│   │   ├── api/                # REST API endpoints
│   │   ├── core/               # Core business logic
│   │   ├── models/             # Database models
│   │   └── services/           # Business services
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile             # Backend container
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API services
│   │   └── store/              # Redux store
│   ├── package.json           # Node dependencies
│   └── Dockerfile             # Frontend container
├── nginx-gateway/             # Nginx reverse proxy
├── docs/                      # Documentation
└── .github/workflows/         # CI/CD pipelines
```

## 📚 Documentation

**Complete documentation available in [`docs/`](./docs/) directory:**

### 🎯 Quick Navigation
- **[📋 Documentation Index](./docs/README.md)** - Complete documentation guide
- **[🌐 Deployment Guide](./docs/deployment.md)** - Production deployment on GCP
- **[📖 API Reference](./docs/API-ENDPOINTS.md)** - Complete REST API documentation
- **[🏗️ Architecture Details](./docs/agents.md)** - Multi-agent system architecture
- **[🔄 CI/CD Setup](./docs/GITHUB-ACTIONS.md)** - GitHub Actions configuration

### 👨‍💻 For Developers
- **[Development Roadmap](./docs/DEVELOPMENT-ROADMAP.md)** - Project timeline and milestones
- **[Development Tasks](./docs/DEVELOPMENT-BACKLOG.md)** - Current development backlog
- **[Database Design](./docs/DATABASE-API-SUMMARY.md)** - Database schema and API summary
- **[Contributing Guide](./CONTRIBUTING.md)** - How to contribute

### 🚀 For DevOps
- **[GCP Integration](./docs/GCP-DEPLOYMENT.md)** - Google Cloud Platform setup
- **[Gateway Configuration](./docs/GATEWAY-SETUP.md)** - Load balancer and routing
- **[Project Overview](./docs/PROJECT-SUMMARY.md)** - System architecture overview

## 🚀 Deployment Options

### 1. Nginx Gateway (Recommended)
- **Cost**: ~$25/month
- **Domain**: Not required
- **Features**: Single URL, automatic SSL
- **Command**: `./deploy-nginx-gateway.sh`

### 2. Cloud Load Balancer (Enterprise)
- **Cost**: ~$45/month
- **Domain**: Required
- **Features**: Global CDN, advanced routing
- **Command**: `DOMAIN_NAME=yourdomain.com ./deploy-gcp.sh`

### 3. GitHub Actions (CI/CD)
```bash
# Set repository secrets:
# - GCP_PROJECT_ID
# - GCP_SA_KEY
# - DOMAIN_NAME (optional)

# Manual workflow trigger or push to main branch
```

## ⚙️ Configuration

### Google Cloud Storage Setup (Required)

AIAlchemy requires Google Cloud Storage for document uploads and processing:

**1. Automatic Setup Validation**
```bash
# Check configuration status and get setup instructions
python3 setup-gcs-complete.py
```

**2. Manual GCS Setup (if needed)**
```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"

# Create service account and generate key
gcloud iam service-accounts create aialchemy-storage \
    --display-name="AIAlchemy Storage Service Account"

gcloud iam service-accounts keys create ./gcs-service-account-key.json \
    --iam-account=aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com

# Move key to backend directory
mv ./gcs-service-account-key.json backend/

# Grant storage permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Create storage bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://aialchemy-uploads
```

**3. GitHub Secrets (for CI/CD)**
Add these secrets to your GitHub repository for automated deployment:
- `GCS_SERVICE_ACCOUNT_KEY` - Entire JSON content from service account key
- `GOOGLE_CLOUD_PROJECT` - Your GCP project ID  
- `GCS_BUCKET_NAME` - Your GCS bucket name (e.g., aialchemy-uploads)
- `SECRET_KEY` - Generate with `openssl rand -hex 32`
- `JWT_SECRET_KEY` - Generate with `openssl rand -hex 32`

### Backend Configuration
```bash
# Required environment variables
DATABASE_URL=sqlite:///./aialchemy.db
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_STORAGE_BUCKET=aialchemy-uploads
USE_GOOGLE_CLOUD_STORAGE=true
GOOGLE_APPLICATION_CREDENTIALS=./gcs-service-account-key.json

# Optional external APIs  
GEMINI_API_KEY=your-gemini-key
CRUNCHBASE_API_KEY=your-crunchbase-key
LINKEDIN_API_KEY=your-linkedin-key
```

### Frontend Configuration
```bash
# API configuration
REACT_APP_API_URL=/api                    # For nginx gateway
# REACT_APP_API_URL=http://localhost:8000  # For local development

# Google services
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
```

## 🧪 Development

### Local Setup
```bash
# Install dependencies
cd backend && pip install -r requirements.txt -r requirements-dev.txt
cd ../frontend && npm install

# Run tests
cd backend && pytest tests/ -v --cov=app
cd frontend && npm test

# Code formatting
cd backend && black app/ && isort app/
cd frontend && npm run format
```

### Adding New Features
1. **Backend**: Create new agents in `backend/app/agents/`
2. **Frontend**: Add components in `frontend/src/components/`
3. **API**: Define endpoints in `backend/app/api/`
4. **Database**: Add models in `backend/app/models/`

## 🔍 Health Checks

```bash
# Check service status
curl https://your-gateway-url/health
# Response: {"status": "healthy", "database": "connected", "tables_initialized": true}

# Check API documentation
curl https://your-gateway-url/docs
# Opens interactive API documentation
```

## 🤝 Contributing

We welcome contributions! Please see our **[Contributing Guide](./CONTRIBUTING.md)** for details.

### Quick Contribution Steps
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Follow our [code style guidelines](./CONTRIBUTING.md#code-style-guidelines)
4. Add tests for new functionality
5. Submit pull request using our [PR template](./CONTRIBUTING.md#pull-request-guidelines)

## 🆘 Support

### Getting Help
- **[📋 Documentation](./docs/README.md)** - Complete documentation index
- **[🐛 Issues](https://github.com/archetana/AIAlchemy/issues)** - Bug reports and feature requests
- **[💬 Discussions](https://github.com/archetana/AIAlchemy/discussions)** - Community discussions

### Troubleshooting

**Common Issues:**

🔧 **Frontend Health Check Timeout**
```bash
# Fixed in latest version - port mismatch resolved
# Ensure GitHub workflow uses port 8080 (not 3000)
```

🔧 **GCS Permission Errors**
```bash
# Verify service account has correct permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --filter="bindings.members:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com"
```

🔧 **Missing Dependencies**
```bash
# Backend missing dependencies
cd backend && pip install -r requirements.txt

# Frontend build issues  
cd frontend && npm install --production=false
```

**Additional Resources:**
- **[Deployment Issues](./docs/deployment.md#-troubleshooting)** - Common deployment problems
- **[Database Problems](./docs/deployment.md#database-configuration)** - Database initialization issues  
- **[API Errors](./docs/API-ENDPOINTS.md)** - API endpoint troubleshooting

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the Google Cloud GenAI Exchange Hackathon 2025**

**🔗 Links**: [Repository](https://github.com/archetana/AIAlchemy) | [Documentation](./docs/README.md) | [Issues](https://github.com/archetana/AIAlchemy/issues) | [Contributing](./CONTRIBUTING.md)

**AIAlchemy - Where AI Meets Investment Intelligence**