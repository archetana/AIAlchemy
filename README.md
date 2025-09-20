# AIAlchemy - AI Analyst for Startup Evaluation

[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://python.org/)
[![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org/)

> **AI-powered startup evaluation platform that automates due diligence, conducts AI interviews, and generates investment-ready memos in under 4 minutes.**

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/archetana/AIAlchemy.git
cd AIAlchemy

# Setup backend
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload

# Setup frontend (new terminal)
cd ../frontend
npm install
npm start

# Visit http://localhost:3000
```

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Google Cloud Integration](#-google-cloud-integration)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Development](#-development)
- [Deployment](#-deployment)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Core Platform Features

#### 🔄 Multi-Format Input Processing
- **Pitch Deck Analysis**: PDF/PPT extraction with financial modeling
- **Video Pitch Processing**: Auto-transcription + sentiment analysis
- **Voice Memo Analysis**: Real-time speech-to-text with emotion detection
- **Structured Forms**: Smart questionnaires with auto-completion

#### 🤖 AI-Powered Founder Interviews
- **Automated Scheduling**: Calendar integration with Calendly/Google Calendar
- **Dynamic Questioning**: Context-aware follow-ups based on pitch analysis
- **Real-time Analysis**: Live sentiment scoring and consistency checking
- **Interview Insights**: Post-call assessment with confidence metrics

#### 🛡️ Comprehensive Risk Assessment
- **Financial Validation**: Cross-reference metrics for inconsistency detection
- **Market Size Verification**: Real-time TAM/SAM validation
- **Team Capability Scoring**: LinkedIn analysis + experience verification
- **Red Flag Detection**: ML pattern recognition for common startup failures

#### 📊 Investment Memo Generation
- **Automated Reports**: Professional investor-ready documents
- **Customizable Scoring**: Investor-specific weightage preferences
- **Benchmarking**: Comparison with 900+ successful startups
- **Risk Matrix**: Visual risk assessment with mitigation strategies

#### 📈 Analytics Dashboard
- **Deal Flow Management**: Kanban-style pipeline with automated progression
- **Performance Metrics**: Platform efficiency and accuracy tracking
- **Sector Analysis**: Investment success rates by industry
- **Team Collaboration**: Comments, annotations, decision tracking

### Advanced Features

#### 🔍 Market Intelligence
- **Competitor Analysis**: Real-time competitive landscape mapping
- **Patent Research**: IP portfolio analysis and validation
- **News Sentiment**: Market perception and media coverage analysis
- **Funding Trends**: Historical and predictive funding pattern analysis

#### 🎯 Investor Preferences
- **Custom Weightings**: Personalized scoring criteria
- **Sector Focus**: Industry-specific evaluation parameters  
- **Risk Appetite**: Conservative vs aggressive analysis modes
- **Portfolio Integration**: Existing investment thesis alignment

#### 🌐 Enterprise Features
- **Multi-tenant Architecture**: White-label solutions for VC firms
- **API Ecosystem**: Third-party integrations (CRM, calendar, communication)
- **Compliance Suite**: SOC 2, GDPR, regional regulatory adherence
- **Audit Trails**: Complete decision tracking for regulatory compliance

## 🏗️ Architecture

### Multi-Agent System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React Dashboard]
        MOB[Mobile App]
    end
    
    subgraph "API Gateway"
        GATEWAY[FastAPI Gateway]
        AUTH[Authentication Service]
    end
    
    subgraph "Multi-Agent System"
        subgraph "Agent 1: Data Ingestion"
            DI[Data Ingestion Agent]
            DOC[Document Processor]
            MEDIA[Media Processor]
        end
        
        subgraph "Agent 2: Market Intelligence"
            MI[Market Intelligence Agent]
            COMP[Competitor Analyzer]
            NEWS[News Scraper]
        end
        
        subgraph "Agent 3: AI Interviewer"
            INT[Interview Agent]
            QUEST[Question Generator]
            CONV[Conversation Manager]
        end
        
        subgraph "Agent 4: Risk Assessment"
            RISK[Risk Assessment Agent]
            ML[ML Risk Models]
            PATTERN[Pattern Recognition]
        end
        
        subgraph "Agent 5: Memo Generator"
            MEMO[Memo Generator Agent]
            TEMPLATE[Template Engine]
            INSIGHT[Insight Generator]
        end
    end
    
    subgraph "Google Cloud AI Services"
        VERTEX[Vertex AI]
        GEMINI[Gemini Pro]
        DOC_AI[Document AI]
        SPEECH[Speech-to-Text]
        DIALOG[Dialogflow CX]
        VISION[Cloud Vision]
    end
    
    subgraph "Data Layer"
        BIGQUERY[(BigQuery)]
        FIRESTORE[(Firestore)]
        CLOUDSQL[(Cloud SQL)]
        STORAGE[(Cloud Storage)]
    end
    
    subgraph "External APIs"
        CRUNCHBASE[Crunchbase API]
        LINKEDIN[LinkedIn API]
        NEWS_API[News APIs]
    end
    
    UI --> GATEWAY
    GATEWAY --> AUTH
    GATEWAY --> DI
    GATEWAY --> MI
    GATEWAY --> INT
    GATEWAY --> RISK
    GATEWAY --> MEMO
    
    DI --> DOC_AI
    DI --> SPEECH
    DI --> VISION
    
    MI --> VERTEX
    MI --> CRUNCHBASE
    MI --> NEWS_API
    
    INT --> DIALOG
    INT --> GEMINI
    
    RISK --> VERTEX
    MEMO --> GEMINI
    
    DI --> STORAGE
    MI --> BIGQUERY
    INT --> FIRESTORE
    RISK --> CLOUDSQL
```

### Data Flow Architecture

```mermaid
sequenceDiagram
    participant F as Founder
    participant UI as Frontend
    participant API as API Gateway
    participant DI as Data Ingestion
    participant MI as Market Intelligence
    participant IA as Interview Agent
    participant RA as Risk Assessment
    participant MG as Memo Generator
    
    F->>UI: Upload pitch materials
    UI->>API: Submit evaluation request
    
    par Data Processing
        API->>DI: Process documents
        API->>MI: Gather market data
    end
    
    DI-->>API: Extracted data
    MI-->>API: Market intelligence
    
    API->>RA: Initial risk assessment
    RA-->>API: Risk score & flags
    
    alt High potential startup
        API->>IA: Schedule AI interview
        IA->>F: Conduct interview
        IA-->>API: Interview insights
        API->>RA: Enhanced assessment
    end
    
    API->>MG: Generate memo
    MG-->>UI: Investment memo ready
```

## 🛠️ Tech Stack

### Backend Technologies

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| **Framework** | FastAPI | 0.104+ | High-performance API development |
| **Language** | Python | 3.11+ | Core backend logic |
| **Database** | PostgreSQL | 15+ | Transactional data storage |
| **Cache** | Redis | 7.0+ | Session management & caching |
| **Task Queue** | Celery | 5.3+ | Asynchronous job processing |
| **Message Broker** | Redis | 7.0+ | Task queue backend |
| **ORM** | SQLAlchemy | 2.0+ | Database abstraction |
| **Migration** | Alembic | 1.12+ | Database schema management |
| **Testing** | Pytest | 7.4+ | Unit and integration testing |
| **Documentation** | Swagger/OpenAPI | 3.0+ | API documentation |

### Frontend Technologies

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| **Framework** | React | 18.2+ | User interface development |
| **Language** | TypeScript | 5.0+ | Type-safe JavaScript |
| **State Management** | Redux Toolkit | 1.9+ | Application state management |
| **UI Library** | Material-UI (MUI) | 5.14+ | Component library |
| **Styling** | Emotion | 11.11+ | CSS-in-JS styling |
| **Data Fetching** | React Query | 4.32+ | Server state management |
| **Routing** | React Router | 6.15+ | Client-side routing |
| **Forms** | React Hook Form | 7.45+ | Form management |
| **Charts** | Recharts | 2.8+ | Data visualization |
| **Testing** | Jest + RTL | Latest | Unit and integration testing |

### DevOps & Infrastructure

| Category | Technology | Purpose |
|----------|------------|---------|
| **Cloud Platform** | Google Cloud Platform | Primary cloud infrastructure |
| **Containerization** | Docker + Docker Compose | Development and deployment |
| **Orchestration** | Google Cloud Run | Serverless container deployment |
| **CI/CD** | GitHub Actions | Automated testing and deployment |
| **Monitoring** | Google Cloud Monitoring | Performance and error tracking |
| **Logging** | Google Cloud Logging | Centralized log management |
| **Security** | Google Cloud IAM | Identity and access management |

## ☁️ Google Cloud Integration

### AI/ML Services

#### Vertex AI Platform
```python
# Example: Custom risk assessment model
from google.cloud import aiplatform

# Initialize Vertex AI
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# Deploy risk assessment model
model = aiplatform.Model.upload(
    display_name="startup-risk-assessment-v1",
    artifact_uri="gs://your-bucket/model-artifacts",
    serving_container_image_uri="gcr.io/vertex-ai/prediction/sklearn-cpu.0-24:latest"
)

endpoint = model.deploy(machine_type="n1-standard-2")
```

#### Document AI Integration
```python
# Example: Pitch deck processing
from google.cloud import documentai

def process_pitch_deck(file_content: bytes) -> dict:
    client = documentai.DocumentProcessorServiceClient()
    
    request = documentai.ProcessRequest(
        name=PROCESSOR_NAME,
        raw_document=documentai.RawDocument(
            content=file_content,
            mime_type="application/pdf"
        )
    )
    
    result = client.process_document(request=request)
    return extract_financial_data(result.document)
```

#### Gemini Pro Integration
```python
# Example: Investment memo generation
import google.generativeai as genai

def generate_investment_memo(analysis_data: dict) -> str:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    Generate a professional investment memo for:
    Company: {analysis_data['company_name']}
    Sector: {analysis_data['sector']}
    Traction: {analysis_data['traction_metrics']}
    Risk Score: {analysis_data['risk_score']}
    
    Include executive summary, market analysis, and recommendation.
    """
    
    response = model.generate_content(prompt)
    return response.text
```

#### Speech-to-Text Integration
```python
# Example: Video pitch transcription
from google.cloud import speech

def transcribe_video_pitch(audio_content: bytes) -> dict:
    client = speech.SpeechClient()
    
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        language_code="en-US",
        enable_speaker_diarization=True,
        diarization_speaker_count=2,
        enable_automatic_punctuation=True,
    )
    
    response = client.recognize(
        config=config,
        audio=speech.RecognitionAudio(content=audio_content)
    )
    
    return process_transcription_results(response.results)
```

#### Dialogflow CX for AI Interviews
```python
# Example: AI interview session
from google.cloud import dialogflowcx

def conduct_ai_interview(session_id: str, founder_response: str) -> dict:
    client = dialogflowcx.SessionsClient()
    session = client.session_path(
        PROJECT_ID, LOCATION, AGENT_ID, session_id
    )
    
    text_input = dialogflowcx.TextInput(text=founder_response)
    query_input = dialogflowcx.QueryInput(
        text=text_input,
        language_code="en-US"
    )
    
    response = client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    
    return {
        "ai_response": response.query_result.response_messages[0].text.text[0],
        "confidence": response.query_result.intent_detection_confidence,
        "next_question": generate_dynamic_question(response)
    }
```

### Data Services

#### BigQuery Integration
```python
# Example: Startup benchmarking queries
from google.cloud import bigquery

def benchmark_startup(company_data: dict) -> dict:
    client = bigquery.Client()
    
    query = f"""
    SELECT 
        AVG(funding_amount) as avg_funding,
        AVG(valuation) as avg_valuation,
        COUNT(*) as peer_count
    FROM `{PROJECT_ID}.startup_data.companies`
    WHERE sector = @sector
        AND stage = @stage
        AND founded_year BETWEEN @year_min AND @year_max
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("sector", "STRING", company_data["sector"]),
            bigquery.ScalarQueryParameter("stage", "STRING", company_data["stage"]),
            bigquery.ScalarQueryParameter("year_min", "INT64", company_data["founded_year"] - 2),
            bigquery.ScalarQueryParameter("year_max", "INT64", company_data["founded_year"] + 2),
        ]
    )
    
    return list(client.query(query, job_config=job_config))[0]
```

## 📁 Project Structure

```
AIAlchemy/
├── README.md
├── docker-compose.yml
├── .github/
│   └── workflows/
│       ├── backend-ci.yml
│       ├── frontend-ci.yml
│       └── deploy.yml
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Configuration management
│   │   ├── dependencies.py         # Dependency injection
│   │   ├── agents/                 # Multi-agent system
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py       # Abstract base agent class
│   │   │   ├── data_ingestion.py   # Document/media processing agent
│   │   │   ├── market_intelligence.py # Market research agent
│   │   │   ├── interview_agent.py  # AI interview conductor
│   │   │   ├── risk_assessment.py  # Risk analysis agent
│   │   │   └── memo_generator.py   # Investment memo writer
│   │   ├── api/                    # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # Authentication endpoints
│   │   │   ├── evaluations.py      # Startup evaluation endpoints
│   │   │   ├── pipeline.py         # Deal pipeline management
│   │   │   ├── analytics.py        # Analytics and reporting
│   │   │   ├── interviews.py       # AI interview management
│   │   │   └── settings.py         # User preferences
│   │   ├── core/                   # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── security.py         # Authentication & authorization
│   │   │   ├── database.py         # Database connection
│   │   │   ├── google_cloud.py     # GCP service integrations
│   │   │   └── exceptions.py       # Custom exception classes
│   │   ├── models/                 # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py             # User and authentication
│   │   │   ├── startup.py          # Startup information
│   │   │   ├── evaluation.py       # Evaluation records
│   │   │   ├── interview.py        # Interview sessions
│   │   │   └── memo.py             # Investment memos
│   │   ├── schemas/                # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py             # User-related schemas
│   │   │   ├── startup.py          # Startup data schemas
│   │   │   ├── evaluation.py       # Evaluation schemas
│   │   │   └── memo.py             # Memo schemas
│   │   ├── services/               # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py     # Authentication logic
│   │   │   ├── evaluation_service.py # Evaluation orchestration
│   │   │   ├── document_service.py # Document processing
│   │   │   ├── interview_service.py # Interview management
│   │   │   └── analytics_service.py # Analytics computation
│   │   ├── ml/                     # Machine learning models
│   │   │   ├── __init__.py
│   │   │   ├── risk_model.py       # Risk assessment model
│   │   │   ├── founder_model.py    # Founder evaluation model
│   │   │   ├── market_model.py     # Market analysis model
│   │   │   └── training/           # Model training scripts
│   │   │       ├── train_risk_model.py
│   │   │       └── data_preparation.py
│   │   └── utils/                  # Utility functions
│   │       ├── __init__.py
│   │       ├── file_handlers.py    # File processing utilities
│   │       ├── email_utils.py      # Email notifications
│   │       └── validators.py       # Data validation
│   ├── tests/                      # Test suite
│   │   ├── __init__.py
│   │   ├── conftest.py             # Test configuration
│   │   ├── test_agents/            # Agent tests
│   │   ├── test_api/               # API endpoint tests
│   │   ├── test_services/          # Service layer tests
│   │   └── test_ml/                # ML model tests
│   ├── alembic/                    # Database migrations
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── requirements.txt            # Python dependencies
│   ├── requirements-dev.txt        # Development dependencies
│   ├── Dockerfile                  # Backend container
│   └── alembic.ini                 # Migration configuration
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── manifest.json
│   ├── src/
│   │   ├── index.tsx               # Application entry point
│   │   ├── App.tsx                 # Main application component
│   │   ├── components/             # Reusable UI components
│   │   │   ├── common/             # Common components
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Loading.tsx
│   │   │   │   └── GlassPanel.tsx  # Glassmorphism component
│   │   │   ├── dashboard/          # Dashboard components
│   │   │   │   ├── MetricsCards.tsx
│   │   │   │   ├── PipelineOverview.tsx
│   │   │   │   └── RecentEvaluations.tsx
│   │   │   ├── evaluation/         # Evaluation components
│   │   │   │   ├── UploadForm.tsx
│   │   │   │   ├── ProcessingView.tsx
│   │   │   │   └── ResultsView.tsx
│   │   │   ├── pipeline/           # Pipeline management
│   │   │   │   ├── KanbanBoard.tsx
│   │   │   │   ├── StartupCard.tsx
│   │   │   │   └── FilterPanel.tsx
│   │   │   ├── memo/               # Investment memo viewer
│   │   │   │   ├── MemoViewer.tsx
│   │   │   │   ├── ScoringPanel.tsx
│   │   │   │   └── CommentsPanel.tsx
│   │   │   ├── analytics/          # Analytics dashboard
│   │   │   │   ├── ChartsGrid.tsx
│   │   │   │   ├── PerformanceMetrics.tsx
│   │   │   │   └── SectorAnalysis.tsx
│   │   │   └── settings/           # Settings interface
│   │   │       ├── AIConfiguration.tsx
│   │   │       ├── TeamManagement.tsx
│   │   │       └── Integrations.tsx
│   │   ├── pages/                  # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Pipeline.tsx
│   │   │   ├── NewEvaluation.tsx
│   │   │   ├── MemoViewer.tsx
│   │   │   ├── Analytics.tsx
│   │   │   └── Settings.tsx
│   │   ├── hooks/                  # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useEvaluations.ts
│   │   │   └── useWebSocket.ts
│   │   ├── services/               # API services
│   │   │   ├── api.ts              # API client configuration
│   │   │   ├── authService.ts      # Authentication API
│   │   │   ├── evaluationService.ts # Evaluation API
│   │   │   └── analyticsService.ts  # Analytics API
│   │   ├── store/                  # Redux store
│   │   │   ├── index.ts            # Store configuration
│   │   │   ├── authSlice.ts        # Authentication state
│   │   │   ├── evaluationSlice.ts  # Evaluation state
│   │   │   └── uiSlice.ts          # UI state
│   │   ├── types/                  # TypeScript type definitions
│   │   │   ├── auth.ts
│   │   │   ├── evaluation.ts
│   │   │   └── api.ts
│   │   ├── utils/                  # Utility functions
│   │   │   ├── constants.ts
│   │   │   ├── formatters.ts
│   │   │   └── validators.ts
│   │   └── styles/                 # Global styles and themes
│   │       ├── globals.css
│   │       ├── theme.ts            # MUI theme configuration
│   │       └── glassmorphism.css   # Glassmorphism styles
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── .env.example
├── mobile/                         # React Native mobile app (future)
├── docs/                           # Documentation
│   ├── api.md                      # API documentation
│   ├── deployment.md               # Deployment guide
│   ├── architecture.md             # System architecture
│   └── contributing.md             # Contribution guidelines
├── scripts/                        # Development scripts
│   ├── setup.sh                    # Initial setup script
│   ├── deploy.sh                   # Deployment script
│   └── backup.sh                   # Database backup script
├── terraform/                      # Infrastructure as code
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
└── k8s/                           # Kubernetes manifests
    ├── backend-deployment.yaml
    ├── frontend-deployment.yaml
    └── ingress.yaml
```

## 🚀 Installation

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **Google Cloud SDK**
- **PostgreSQL 15+** (for local development)

### 1. Clone Repository

```bash
git clone https://github.com/your-username/AIAlchemy.git
cd AIAlchemy
```

### 2. Google Cloud Setup

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable \
    aiplatform.googleapis.com \
    documentai.googleapis.com \
    speech.googleapis.com \
    dialogflow.googleapis.com \
    bigquery.googleapis.com \
    storage.googleapis.com \
    run.googleapis.com

# Create service account and download key
gcloud iam service-accounts create AIAlchemy-service \
    --display-name="AIAlchemy Service Account"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:AIAlchemy-service@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud iam service-accounts keys create ./google-cloud-key.json \
    --iam-account=AIAlchemy-service@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Setup database
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm start
```

### 5. Docker Setup (Alternative)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

## ⚙️ Configuration

### Backend Configuration (.env)

```bash
# Application Settings
APP_NAME=AIAlchemy
APP_VERSION=1.0.0
DEBUG=True
SECRET_KEY=your-super-secure-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/AIAlchemy
REDIS_URL=redis://localhost:6379/0

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./google-cloud-key.json
GOOGLE_CLOUD_LOCATION=us-central1

# AI/ML Service Configuration
VERTEX_AI_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
DOCUMENT_AI_PROCESSOR_ID=your-processor-id
DIALOGFLOW_AGENT_ID=your-agent-id
GEMINI_API_KEY=your-gemini-api-key

# External API Keys
CRUNCHBASE_API_KEY=your-crunchbase-key
LINKEDIN_API_KEY=your-linkedin-key
NEWS_API_KEY=your-news-api-key

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Security
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# File Storage
MAX_FILE_SIZE_MB=100
ALLOWED_FILE_TYPES=pdf,ppt,pptx,mp4,mp3,wav

# Feature Flags
ENABLE_AI_INTERVIEWS=True
ENABLE_REAL_TIME_BENCHMARKING=True
ENABLE_ADVANCED_ANALYTICS=True
```

### Frontend Configuration (.env.local)

```bash
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_VERSION=v1

# Authentication
REACT_APP_JWT_TOKEN_KEY=AIAlchemy_token

# Google Services
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
REACT_APP_GOOGLE_ANALYTICS_ID=your-ga-id

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_REAL_TIME_UPDATES=true
REACT_APP_ENABLE_MOBILE_APP=false

# UI Configuration
REACT_APP_THEME_MODE=dark
REACT_APP_PRIMARY_COLOR=#1565C0
REACT_APP_SECONDARY_COLOR=#43A047
```

## 🔧 Development

### Backend Development

#### Setting Up Development Environment

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests
pytest tests/ -v --cov=app

# Run type checking
mypy app/

# Format code
black app/ tests/
isort app/ tests/

# Run linting
flake8 app/ tests/
```

#### Database Operations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Reset database
alembic downgrade base
alembic upgrade head
```

#### Running Individual Agents

```bash
# Test data ingestion agent
python -m app.agents.data_ingestion --test-file sample_pitch.pdf

# Test market intelligence agent
python -m app.agents.market_intelligence --company "TechCorp AI" --sector "SaaS"

# Test interview agent
python -m app.agents.interview_agent --session-id test-session

# Test risk assessment agent
python -m app.agents.risk_assessment --evaluation-id 123

# Test memo generator
python -m app.agents.memo_generator --evaluation-id 123
```

### Frontend Development

#### Development Commands

```bash
# Start development server with hot reload
npm start

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage --watchAll=false

# Build production bundle
npm run build

# Analyze bundle size
npm run analyze

# Type checking
npm run type-check

# Linting
npm run lint
npm run lint:fix

# Format code
npm run format
```

#### Component Development

```bash
# Generate new component
npx generate-react-cli component ComponentName

# Run Storybook for component development
npm run storybook

# Build Storybook
npm run build-storybook
```

### Testing Strategy

#### Backend Testing

```python
# Example: Test evaluation service
import pytest
from app.services.evaluation_service import EvaluationService
from app.schemas.startup import StartupCreate

@pytest.mark.asyncio
async def test_create_evaluation():
    service = EvaluationService()
    startup_data = StartupCreate(
        name="TechCorp AI",
        sector="SaaS",
        stage="Series A",
        founded_year=2022
    )
    
    evaluation = await service.create_evaluation(startup_data)
    assert evaluation.id is not None
    assert evaluation.status == "processing"

# Example: Test AI agent
@pytest.mark.asyncio
async def test_risk_assessment_agent():
    from app.agents.risk_assessment import RiskAssessmentAgent
    
    agent = RiskAssessmentAgent()
    risk_score = await agent.assess_risk({
        "revenue": 500000,
        "growth_rate": 300,
        "team_size": 15,
        "funding_raised": 2000000
    })
    
    assert 0 <= risk_score <= 10
```

#### Frontend Testing

```typescript
// Example: Component test
import { render, screen } from '@testing-library/react';
import { StartupCard } from '../components/pipeline/StartupCard';

test('renders startup card with correct information', () => {
  const startup = {
    id: 1,
    name: 'TechCorp AI',
    sector: 'SaaS',
    stage: 'Series A',
    score: 8.7
  };

  render(<StartupCard startup={startup} />);
  
  expect(screen.getByText('TechCorp AI')).toBeInTheDocument();
  expect(screen.getByText('8.7/10')).toBeInTheDocument();
});

// Example: Hook test
import { renderHook } from '@testing-library/react';
import { useEvaluations } from '../hooks/useEvaluations';

test('useEvaluations returns correct data', async () => {
  const { result } = renderHook(() => useEvaluations());
  
  expect(result.current.isLoading).toBe(true);
  
  await waitFor(() => {
    expect(result.current.isLoading).toBe(false);
    expect(result.current.evaluations).toHaveLength(3);
  });
});
```

## 🚀 Deployment

### Local Deployment with Docker

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy locally
docker-compose -f docker-compose.prod.yml up -d

# Check deployment
docker-compose ps
docker-compose logs
```

### Google Cloud Run Deployment

#### 1. Build and Push Images

```bash
# Configure Docker for Google Container Registry
gcloud auth configure-docker

# Build and push backend
cd backend
docker build -t gcr.io/YOUR_PROJECT_ID/AIAlchemy-backend:latest .
docker push gcr.io/YOUR_PROJECT_ID/AIAlchemy-backend:latest

# Build and push frontend
cd ../frontend
docker build -t gcr.io/YOUR_PROJECT_ID/AIAlchemy-frontend:latest .
docker push gcr.io/YOUR_PROJECT_ID/AIAlchemy-frontend:latest
```

#### 2. Deploy to Cloud Run

```bash
# Deploy backend service
gcloud run deploy AIAlchemy-backend \
    --image gcr.io/YOUR_PROJECT_ID/AIAlchemy-backend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 100 \
    --set-env-vars="DATABASE_URL=postgresql://user:pass@host:5432/db" \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID"

# Deploy frontend service
gcloud run deploy AIAlchemy-frontend \
    --image gcr.io/YOUR_PROJECT_ID/AIAlchemy-frontend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --set-env-vars="REACT_APP_API_BASE_URL=https://AIAlchemy-backend-xxx.run.app"

# Get service URLs
gcloud run services list --platform managed
```

#### 3. Setup Cloud SQL Database

```bash
# Create Cloud SQL instance
gcloud sql instances create AIAlchemy-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=your-secure-password

# Create database
gcloud sql databases create AIAlchemy --instance=AIAlchemy-db

# Create user
gcloud sql users create AIAlchemy-user \
    --instance=AIAlchemy-db \
    --password=secure-user-password
```

### Kubernetes Deployment

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: AIAlchemy-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: AIAlchemy-backend
  template:
    metadata:
      labels:
        app: AIAlchemy-backend
    spec:
      containers:
      - name: backend
        image: gcr.io/YOUR_PROJECT_ID/AIAlchemy-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: AIAlchemy-secrets
              key: database-url
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /var/secrets/google/key.json
        volumeMounts:
        - name: google-cloud-key
          mountPath: /var/secrets/google
      volumes:
      - name: google-cloud-key
        secret:
          secretName: google-cloud-key
---
apiVersion: v1
kind: Service
metadata:
  name: AIAlchemy-backend-service
spec:
  selector:
    app: AIAlchemy-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get deployments
kubectl get services
kubectl get pods

# View logs
kubectl logs -f deployment/AIAlchemy-backend
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy to Google Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Setup Google Cloud SDK
      uses: google-github-actions/setup-gcloud@v1
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ secrets.GCP_PROJECT_ID }}
        
    - name: Configure Docker
      run: gcloud auth configure-docker
      
    - name: Build and push backend
      run: |
        cd backend
        docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/AIAlchemy-backend:${{ github.sha }} .
        docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/AIAlchemy-backend:${{ github.sha }}
        
    - name: Deploy backend to Cloud Run
      run: |
        gcloud run deploy AIAlchemy-backend \
          --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/AIAlchemy-backend:${{ github.sha }} \
          --platform managed \
          --region us-central1 \
          --allow-unauthenticated
          
    - name: Build and push frontend
      run: |
        cd frontend
        docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/AIAlchemy-frontend:${{ github.sha }} .
        docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/AIAlchemy-frontend:${{ github.sha }}
        
    - name: Deploy frontend to Cloud Run
      run: |
        gcloud run deploy AIAlchemy-frontend \
          --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/AIAlchemy-frontend:${{ github.sha }} \
          --platform managed \
          --region us-central1 \
          --allow-unauthenticated
```

## 📚 API Documentation

### Authentication

```bash
# Login
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "investor@vc-firm.com",
  "password": "secure-password"
}

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Evaluations

```bash
# Create new evaluation
POST /api/v1/evaluations/
Authorization: Bearer {token}
Content-Type: multipart/form-data

{
  "company_name": "TechCorp AI",
  "sector": "SaaS",
  "stage": "Series A",
  "pitch_deck": (file),
  "video_pitch": (file)
}

# Get evaluation status
GET /api/v1/evaluations/{evaluation_id}/status
Authorization: Bearer {token}

# Response
{
  "id": "123",
  "status": "processing",
  "progress": 75,
  "estimated_completion": "2024-01-15T10:30:00Z",
  "current_stage": "ai_interview"
}

# Get evaluation results
GET /api/v1/evaluations/{evaluation_id}/memo
Authorization: Bearer {token}

# Response
{
  "overall_score": 8.7,
  "risk_level": "low",
  "recommendation": "invest",
  "sections": {
    "executive_summary": "...",
    "market_analysis": "...",
    "founder_assessment": "...",
    "risk_analysis": "..."
  }
}
```

### AI Interviews

```bash
# Schedule AI interview
POST /api/v1/interviews/schedule
Authorization: Bearer {token}

{
  "evaluation_id": "123",
  "founder_email": "founder@startup.com",
  "preferred_times": ["2024-01-15T14:00:00Z", "2024-01-15T16:00:00Z"]
}

# Get interview session
GET /api/v1/interviews/{session_id}
Authorization: Bearer {token}

# Send interview response
POST /api/v1/interviews/{session_id}/respond
{
  "response": "Our main competitive advantage is our proprietary AI algorithm...",
  "audio_file": (optional file)
}
```

### Pipeline Management

```bash
# Get pipeline overview
GET /api/v1/pipeline/
Authorization: Bearer {token}

# Response
{
  "stages": {
    "new_applications": 24,
    "processing": 8,
    "interview_scheduled": 5,
    "final_review": 6,
    "decided": 12
  },
  "items": [
    {
      "id": "123",
      "company_name": "TechCorp AI",
      "stage": "processing",
      "score": null,
      "submitted_at": "2024-01-15T08:00:00Z"
    }
  ]
}

# Move startup to different stage
PATCH /api/v1/pipeline/{evaluation_id}/stage
{
  "stage": "final_review",
  "notes": "Ready for partner review"
}
```

### Analytics

```bash
# Get platform analytics
GET /api/v1/analytics/dashboard
Authorization: Bearer {token}

# Response
{
  "metrics": {
    "total_evaluations": 2847,
    "average_processing_time": 3.2,
    "ai_accuracy_rate": 94.7,
    "success_prediction_rate": 87.3
  },
  "charts": {
    "evaluation_volume": [...],
    "sector_breakdown": [...],
    "success_rates": [...]
  }
}

# Get sector analysis
GET /api/v1/analytics/sectors
Authorization: Bearer {token}

# Get benchmark data
GET /api/v1/analytics/benchmark?sector=SaaS&stage=SeriesA
Authorization: Bearer {token}
```

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Install dependencies**: Follow installation guide
4. **Make changes**: Implement your feature
5. **Write tests**: Add comprehensive test coverage
6. **Run tests**: `pytest` (backend) and `npm test` (frontend)
7. **Commit changes**: `git commit -m 'Add amazing feature'`
8. **Push branch**: `git push origin feature/amazing-feature`
9. **Open Pull Request**: Submit PR with detailed description

### Code Style Guidelines

#### Python (Backend)
- Follow **PEP 8** style guide
- Use **Black** for code formatting
- Use **isort** for import sorting  
- Use **type hints** for all functions
- Write **docstrings** for all classes and methods
- Maximum line length: **88 characters**

```python
# Example of good Python code style
from typing import List, Optional
import asyncio

class StartupEvaluator:
    """AI-powered startup evaluation service."""
    
    def __init__(self, config: EvaluatorConfig) -> None:
        """Initialize evaluator with configuration."""
        self.config = config
        self.agents = self._initialize_agents()
    
    async def evaluate_startup(
        self, 
        startup_data: StartupData,
        options: Optional[EvaluationOptions] = None
    ) -> EvaluationResult:
        """
        Evaluate startup using multi-agent AI system.
        
        Args:
            startup_data: Company information and materials
            options: Optional evaluation parameters
            
        Returns:
            Complete evaluation with scoring and recommendations
        """
        # Implementation here
        pass
```

#### TypeScript (Frontend)
- Follow **Airbnb TypeScript Style Guide**
- Use **Prettier** for code formatting
- Use **ESLint** for linting
- Prefer **functional components** with hooks
- Use **proper typing** for all props and state
- Maximum line length: **100 characters**

```typescript
// Example of good TypeScript code style
interface StartupCardProps {
  startup: Startup;
  onSelect?: (startup: Startup) => void;
  isLoading?: boolean;
}

export const StartupCard: React.FC<StartupCardProps> = ({
  startup,
  onSelect,
  isLoading = false
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const handleClick = useCallback(() => {
    if (onSelect && !isLoading) {
      onSelect(startup);
    }
  }, [startup, onSelect, isLoading]);
  
  return (
    <GlassPanel 
      onClick={handleClick}
      className={`startup-card ${isExpanded ? 'expanded' : ''}`}
    >
      <CardContent startup={startup} />
    </GlassPanel>
  );
};
```

### Pull Request Guidelines

#### PR Title Format
```
[Type] Brief description of changes

Types: feat, fix, docs, style, refactor, test, chore
Examples:
- feat: Add AI interview scheduling functionality
- fix: Resolve memory leak in document processing
- docs: Update API documentation for evaluation endpoints
```

#### PR Description Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)  
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] New tests added for new functionality

## Google Cloud Integration
- [ ] Uses appropriate GCP services
- [ ] Follows GCP best practices
- [ ] Updated environment configuration
- [ ] Tested with actual GCP services

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Documentation updated
- [ ] No merge conflicts
```

### Issue Templates

#### Bug Report
```markdown
## Bug Description
A clear and concise description of what the bug is.

## To Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Environment
- OS: [e.g. macOS 12.0]
- Browser: [e.g. Chrome 96]
- Python version: [e.g. 3.11]
- Node.js version: [e.g. 18.17]

## Additional Context
Add any other context about the problem here.
```

#### Feature Request
```markdown
## Feature Description
A clear and concise description of what you want to happen.

## Problem Statement
What problem does this feature solve?

## Proposed Solution
How should this feature work?

## Alternative Solutions
Any alternative approaches you've considered.

## Google Cloud Integration
How would this feature integrate with existing GCP services?

## Additional Context
Add any other context or screenshots about the feature request here.
```

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 AIAlchemy Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support & Contact

### For Hackathon Judges
- **Demo Request**: [Schedule Demo](https://calendly.com/AIAlchemy-demo)
- **Technical Questions**: [technical@AIAlchemy.com](mailto:technical@AIAlchemy.com)
- **GitHub Issues**: [Create Issue](https://github.com/your-username/AIAlchemy/issues/new)

### For Contributors
- **Discord Community**: [Join Discord](https://discord.gg/AIAlchemy)
- **Slack Workspace**: [Join Slack](https://AIAlchemy.slack.com)
- **Developer Forum**: [Visit Forum](https://forum.AIAlchemy.com)

### For Potential Users
- **Product Demo**: [Book Demo](https://AIAlchemy.com/demo)
- **Sales Inquiry**: [sales@AIAlchemy.com](mailto:sales@AIAlchemy.com)
- **Partnership**: [partnerships@AIAlchemy.com](mailto:partnerships@AIAlchemy.com)

---

**Built with ❤️ for the Google Cloud GenAI Exchange Hackathon 2025**

**AIAlchemy - Where AI Meets Investment Intelligence**
