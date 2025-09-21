"""
Mock data generation for AIAlchemy platform
Creates realistic test data for all entities
"""

import asyncio
from datetime import datetime, timedelta
import random
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_local
from app.models import (
    User, Industry, StartupApplication, Founder, UploadedFile,
    FinancialMetric, InvestmentMemo, EvaluationHistory,
    PipelineMetrics, InvestmentWeights,
    ApplicationStatus, FundingStage, FileStatus, UserRole
)

# Sample data
INDUSTRIES = [
    {"name": "Artificial Intelligence", "description": "AI/ML platforms and solutions"},
    {"name": "FinTech", "description": "Financial technology and services"},
    {"name": "HealthTech", "description": "Digital health and medical technology"},
    {"name": "EdTech", "description": "Educational technology and e-learning"},
    {"name": "E-commerce", "description": "Online retail and marketplace platforms"},
    {"name": "SaaS", "description": "Software as a Service platforms"},
    {"name": "CleanTech", "description": "Clean energy and environmental technology"},
    {"name": "BioTech", "description": "Biotechnology and life sciences"},
    {"name": "Mobility", "description": "Transportation and logistics technology"},
    {"name": "Gaming", "description": "Video games and interactive entertainment"}
]

USERS = [
    {"email": "john.smith@aialchemy.vc", "full_name": "John Smith", "title": "Senior Partner", "role": UserRole.PARTNER},
    {"email": "sarah.chen@aialchemy.vc", "full_name": "Sarah Chen", "title": "Investment Analyst", "role": UserRole.ANALYST},
    {"email": "michael.brown@aialchemy.vc", "full_name": "Michael Brown", "title": "Principal", "role": UserRole.ANALYST},
    {"email": "lisa.wang@aialchemy.vc", "full_name": "Lisa Wang", "title": "Associate", "role": UserRole.ANALYST},
    {"email": "david.garcia@aialchemy.vc", "full_name": "David Garcia", "title": "Managing Partner", "role": UserRole.ADMIN},
    {"email": "emily.johnson@aialchemy.vc", "full_name": "Emily Johnson", "title": "Senior Analyst", "role": UserRole.ANALYST},
]

STARTUP_COMPANIES = [
    {
        "company_name": "TechFlow AI",
        "website": "https://techflow.ai",
        "contact_email": "founder@techflow.ai",
        "contact_name": "Alex Rivera",
        "contact_phone": "+1-555-0101",
        "funding_stage": FundingStage.SERIES_A,
        "funding_amount_requested": 15000000,
        "current_arr": 2400000,
        "gross_margin": 82.5,
        "runway_months": 18,
        "industry": "Artificial Intelligence"
    },
    {
        "company_name": "GreenPay",
        "website": "https://greenpay.com",
        "contact_email": "ceo@greenpay.com",
        "contact_name": "Maria Santos",
        "contact_phone": "+1-555-0102", 
        "funding_stage": FundingStage.SEED,
        "funding_amount_requested": 3500000,
        "current_arr": 840000,
        "gross_margin": 75.2,
        "runway_months": 24,
        "industry": "FinTech"
    },
    {
        "company_name": "HealthLink Pro",
        "website": "https://healthlinkpro.com",
        "contact_email": "founders@healthlinkpro.com",
        "contact_name": "Dr. James Wilson",
        "contact_phone": "+1-555-0103",
        "funding_stage": FundingStage.SERIES_B,
        "funding_amount_requested": 25000000,
        "current_arr": 8500000,
        "gross_margin": 88.1,
        "runway_months": 36,
        "industry": "HealthTech"
    },
    {
        "company_name": "EduSmart Labs",
        "website": "https://edusmartlabs.com", 
        "contact_email": "hello@edusmartlabs.com",
        "contact_name": "Jennifer Kim",
        "contact_phone": "+1-555-0104",
        "funding_stage": FundingStage.PRE_SEED,
        "funding_amount_requested": 1200000,
        "current_arr": 180000,
        "gross_margin": 68.9,
        "runway_months": 12,
        "industry": "EdTech"
    },
    {
        "company_name": "CloudSync Solutions",
        "website": "https://cloudsync.io",
        "contact_email": "contact@cloudsync.io",
        "contact_name": "Robert Lee",
        "contact_phone": "+1-555-0105",
        "funding_stage": FundingStage.SERIES_A,
        "funding_amount_requested": 12000000,
        "current_arr": 3200000,
        "gross_margin": 91.3,
        "runway_months": 22,
        "industry": "SaaS"
    },
    {
        "company_name": "Quantum Commerce",
        "website": "https://quantumcommerce.com",
        "contact_email": "team@quantumcommerce.com",
        "contact_name": "Amanda Foster",
        "contact_phone": "+1-555-0106",
        "funding_stage": FundingStage.SEED,
        "funding_amount_requested": 5000000,
        "current_arr": 1100000,
        "gross_margin": 72.8,
        "runway_months": 20,
        "industry": "E-commerce"
    },
    {
        "company_name": "EcoTech Innovations",
        "website": "https://ecotech-innovations.com",
        "contact_email": "info@ecotech-innovations.com", 
        "contact_name": "Carlos Rodriguez",
        "contact_phone": "+1-555-0107",
        "funding_stage": FundingStage.SERIES_A,
        "funding_amount_requested": 18000000,
        "current_arr": 920000,
        "gross_margin": 65.4,
        "runway_months": 30,
        "industry": "CleanTech"
    },
    {
        "company_name": "BioGen Analytics",
        "website": "https://biogen-analytics.com",
        "contact_email": "contact@biogen-analytics.com",
        "contact_name": "Dr. Susan White",
        "contact_phone": "+1-555-0108",
        "funding_stage": FundingStage.SERIES_B,
        "funding_amount_requested": 35000000,
        "current_arr": 6800000,
        "gross_margin": 89.7,
        "runway_months": 42,
        "industry": "BioTech"
    }
]

FOUNDERS_DATA = {
    "TechFlow AI": [
        {"name": "Alex Rivera", "title": "CEO & Co-Founder", "years_experience": 12, 
         "linkedin_url": "https://linkedin.com/in/alex-rivera", 
         "previous_companies": "Former VP Engineering at DataCorp, Senior Engineer at Google",
         "education": "MS Computer Science - Stanford University"},
        {"name": "Sarah Kim", "title": "CTO & Co-Founder", "years_experience": 10,
         "linkedin_url": "https://linkedin.com/in/sarah-kim-tech",
         "previous_companies": "Former Lead AI Engineer at Microsoft, Research Scientist at OpenAI", 
         "education": "PhD Machine Learning - MIT"}
    ],
    "GreenPay": [
        {"name": "Maria Santos", "title": "CEO & Founder", "years_experience": 8,
         "linkedin_url": "https://linkedin.com/in/maria-santos-fintech",
         "previous_companies": "Former Product Director at Stripe, Senior Manager at PayPal",
         "education": "MBA - Wharton School, BS Finance - UC Berkeley"}
    ],
    "HealthLink Pro": [
        {"name": "Dr. James Wilson", "title": "CEO & Co-Founder", "years_experience": 15,
         "linkedin_url": "https://linkedin.com/in/dr-james-wilson",
         "previous_companies": "Former Chief Medical Officer at HealthTech Inc, Practicing Physician",
         "education": "MD - Harvard Medical School, MS Biomedical Engineering - Johns Hopkins"},
        {"name": "Rachel Park", "title": "CPO & Co-Founder", "years_experience": 9,
         "linkedin_url": "https://linkedin.com/in/rachel-park-product",
         "previous_companies": "Former Senior Product Manager at Epic Systems, Product Lead at Cerner",
         "education": "MS Health Informatics - UCSF"}
    ]
}

async def create_industries(session: AsyncSession) -> List[Industry]:
    """Create industry records"""
    from sqlalchemy import select
    
    # Check if industries already exist
    result = await session.execute(select(Industry))
    existing_industries = result.scalars().all()
    if existing_industries:
        print("Industries already exist, using existing data...")
        return existing_industries
    
    industries = []
    for industry_data in INDUSTRIES:
        industry = Industry(**industry_data)
        session.add(industry)
        industries.append(industry)
    
    await session.commit()
    for industry in industries:
        await session.refresh(industry)
    return industries

async def create_users(session: AsyncSession) -> List[User]:
    """Create user records"""
    from sqlalchemy import select
    
    # Check if users already exist
    result = await session.execute(select(User))
    existing_users = result.scalars().all()
    if existing_users:
        print("Users already exist, using existing data...")
        return existing_users
    
    users = []
    for user_data in USERS:
        user = User(**user_data)
        session.add(user)
        users.append(user)
    
    await session.commit()
    for user in users:
        await session.refresh(user)
    return users

async def create_startups(session: AsyncSession, industries: List[Industry], users: List[User]) -> List[StartupApplication]:
    """Create startup application records"""
    from sqlalchemy import select
    
    # Check if startups already exist
    result = await session.execute(select(StartupApplication))
    existing_startups = result.scalars().all()
    if existing_startups:
        print("Startups already exist, using existing data...")
        return existing_startups
    
    industry_map = {ind.name: ind.id for ind in industries}
    
    startups = []
    for i, startup_data in enumerate(STARTUP_COMPANIES):
        # Copy data and add relationships
        data = startup_data.copy()
        industry_name = data.pop("industry")
        data["industry_id"] = industry_map[industry_name]
        
        # Assign status and analyst
        statuses = [
            ApplicationStatus.NEW,
            ApplicationStatus.DATA_PROCESSING, 
            ApplicationStatus.AI_ANALYSIS,
            ApplicationStatus.MANUAL_REVIEW,
            ApplicationStatus.PARTNER_REVIEW,
            ApplicationStatus.COMPLETED
        ]
        data["status"] = statuses[i % len(statuses)]
        data["assigned_analyst_id"] = random.choice(users).id if data["status"] != ApplicationStatus.NEW else None
        
        # Add AI scores and timestamps
        data["ai_score"] = random.uniform(65.0, 95.0)
        data["manual_score"] = random.uniform(60.0, 90.0) if data["status"] in [ApplicationStatus.MANUAL_REVIEW, ApplicationStatus.PARTNER_REVIEW, ApplicationStatus.COMPLETED] else None
        
        # Set timestamps
        base_time = datetime.now() - timedelta(days=random.randint(1, 60))
        data["submitted_at"] = base_time
        if data["assigned_analyst_id"]:
            data["assigned_at"] = base_time + timedelta(hours=random.randint(1, 48))
        if data["status"] == ApplicationStatus.COMPLETED:
            data["completed_at"] = base_time + timedelta(days=random.randint(5, 30))
            data["final_rating"] = random.choice(["Strong Invest", "Invest", "Pass", "Watch"])
        
        startup = StartupApplication(**data)
        session.add(startup)
        startups.append(startup)
    
    await session.commit()
    for startup in startups:
        await session.refresh(startup)
    return startups

async def create_founders(session: AsyncSession, startups: List[StartupApplication]):
    """Create founder records"""
    for startup in startups:
        if startup.company_name in FOUNDERS_DATA:
            for founder_data in FOUNDERS_DATA[startup.company_name]:
                founder_data["startup_application_id"] = startup.id
                founder = Founder(**founder_data)
                session.add(founder)
    
    await session.commit()

async def create_uploaded_files(session: AsyncSession, startups: List[StartupApplication]):
    """Create uploaded file records"""
    file_types = ["pitch_deck", "financial_model", "business_plan", "market_research", "legal_docs"]
    
    for startup in startups:
        # Each startup has 2-4 files
        num_files = random.randint(2, 4)
        for i in range(num_files):
            file_type = random.choice(file_types)
            file_data = {
                "startup_application_id": startup.id,
                "filename": f"{startup.company_name.lower().replace(' ', '_')}_{file_type}.pdf",
                "original_filename": f"{file_type.replace('_', ' ').title()}.pdf",
                "file_type": file_type,
                "file_size": random.randint(500000, 5000000),  # 500KB - 5MB
                "mime_type": "application/pdf",
                "file_path": f"/uploads/{startup.id}/{file_type}.pdf",
                "status": FileStatus.COMPLETED if startup.status != ApplicationStatus.NEW else random.choice([FileStatus.PROCESSING, FileStatus.COMPLETED]),
                "processing_progress": 100 if startup.status != ApplicationStatus.NEW else random.randint(60, 100),
                "uploaded_at": startup.submitted_at + timedelta(minutes=random.randint(5, 60))
            }
            
            if file_data["status"] == FileStatus.COMPLETED:
                file_data["processed_at"] = file_data["uploaded_at"] + timedelta(minutes=random.randint(5, 30))
            
            file_obj = UploadedFile(**file_data)
            session.add(file_obj)
    
    await session.commit()

async def create_financial_metrics(session: AsyncSession, startups: List[StartupApplication]):
    """Create financial metric records"""
    for startup in startups:
        if startup.status in [ApplicationStatus.AI_ANALYSIS, ApplicationStatus.MANUAL_REVIEW, ApplicationStatus.PARTNER_REVIEW, ApplicationStatus.COMPLETED]:
            metrics = [
                {"metric_name": "ARR", "metric_value": startup.current_arr, "metric_unit": "$", "metric_period": "2024", "data_source": "pitch_deck"},
                {"metric_name": "Gross Margin", "metric_value": startup.gross_margin, "metric_unit": "%", "metric_period": "2024", "data_source": "financial_model"},
                {"metric_name": "Runway", "metric_value": startup.runway_months, "metric_unit": "months", "metric_period": "Current", "data_source": "financial_model"},
                {"metric_name": "Monthly Growth Rate", "metric_value": random.uniform(8.0, 25.0), "metric_unit": "%", "metric_period": "Q4 2024", "data_source": "pitch_deck"},
                {"metric_name": "CAC", "metric_value": random.uniform(100.0, 500.0), "metric_unit": "$", "metric_period": "2024", "data_source": "financial_model"},
                {"metric_name": "LTV", "metric_value": random.uniform(1500.0, 8000.0), "metric_unit": "$", "metric_period": "2024", "data_source": "pitch_deck"}
            ]
            
            for metric_data in metrics:
                metric_data["startup_application_id"] = startup.id
                metric = FinancialMetric(**metric_data)
                session.add(metric)
    
    await session.commit()

async def create_investment_memos(session: AsyncSession, startups: List[StartupApplication], users: List[User]):
    """Create investment memo records"""
    for startup in startups:
        if startup.status in [ApplicationStatus.MANUAL_REVIEW, ApplicationStatus.PARTNER_REVIEW, ApplicationStatus.COMPLETED]:
            author = next(u for u in users if u.id == startup.assigned_analyst_id)
            
            memo_data = {
                "startup_application_id": startup.id,
                "author_id": author.id,
                "executive_summary": f"{startup.company_name} is a {startup.funding_stage.value.replace('_', ' ')} stage company in the {startup.industry.name if startup.industry else 'technology'} sector with strong traction and experienced leadership.",
                "investment_highlights": "• Strong product-market fit with growing customer base\n• Experienced founding team with relevant domain expertise\n• Large addressable market with significant growth potential\n• Proprietary technology and competitive advantages",
                "market_analysis": f"The {startup.industry.name if startup.industry else 'technology'} market is experiencing rapid growth with increasing demand for innovative solutions.",
                "business_model_analysis": f"Revenue model based on SaaS subscriptions with current ARR of ${startup.current_arr:,.0f} and {startup.gross_margin:.1f}% gross margins.",
                "team_analysis": "Strong founding team with complementary skills and relevant industry experience. Team has previously scaled similar businesses.",
                "financial_analysis": f"Strong unit economics with {startup.runway_months} months of runway. Company is well-positioned for {startup.funding_stage.value.replace('_', ' ')} funding round.",
                "risks_concerns": "• Market competition from established players\n• Execution risk in scaling operations\n• Regulatory considerations in target markets",
                "recommendation": startup.final_rating if startup.final_rating else "Strong Invest",
                "recommended_investment": startup.funding_amount_requested * 0.6 if startup.funding_amount_requested else 5000000,
                "proposed_valuation": startup.funding_amount_requested * 3.5 if startup.funding_amount_requested else 25000000,
                "is_draft": startup.status != ApplicationStatus.COMPLETED,
                "partner_review_scheduled": startup.status == ApplicationStatus.PARTNER_REVIEW,
                "approved": startup.status == ApplicationStatus.COMPLETED
            }
            
            if startup.status == ApplicationStatus.PARTNER_REVIEW:
                memo_data["partner_review_date"] = datetime.now() + timedelta(days=random.randint(1, 7))
            
            memo = InvestmentMemo(**memo_data)
            session.add(memo)
    
    await session.commit()

async def create_evaluation_history(session: AsyncSession, startups: List[StartupApplication]):
    """Create evaluation history records"""
    for startup in startups:
        if startup.status != ApplicationStatus.NEW:
            # Create status transition history
            statuses = [ApplicationStatus.NEW, ApplicationStatus.DATA_PROCESSING, ApplicationStatus.AI_ANALYSIS]
            
            if startup.status in [ApplicationStatus.MANUAL_REVIEW, ApplicationStatus.PARTNER_REVIEW, ApplicationStatus.COMPLETED]:
                statuses.append(ApplicationStatus.MANUAL_REVIEW)
            if startup.status in [ApplicationStatus.PARTNER_REVIEW, ApplicationStatus.COMPLETED]:
                statuses.append(ApplicationStatus.PARTNER_REVIEW)
            if startup.status == ApplicationStatus.COMPLETED:
                statuses.append(ApplicationStatus.COMPLETED)
            
            current_time = startup.submitted_at
            for i in range(1, len(statuses)):
                time_in_stage = random.randint(30, 2880)  # 30 minutes to 2 days in minutes
                current_time += timedelta(minutes=time_in_stage)
                
                history_data = {
                    "startup_application_id": startup.id,
                    "previous_status": statuses[i-1],
                    "new_status": statuses[i],
                    "time_in_previous_stage": time_in_stage,
                    "created_at": current_time,
                    "notes": f"Transitioned from {statuses[i-1].value} to {statuses[i].value}"
                }
                
                history = EvaluationHistory(**history_data)
                session.add(history)
    
    await session.commit()

async def create_pipeline_metrics(session: AsyncSession):
    """Create pipeline metrics for dashboard"""
    metrics_data = {
        "total_applications": len(STARTUP_COMPANIES),
        "applications_in_ai_processing": 2,
        "completed_evaluations": 2,
        "average_ai_score": 78.5,
        "average_processing_time": 12.3,
        "data_processing_conversion": 92.5,
        "ai_analysis_conversion": 85.7,
        "partner_review_conversion": 73.2,
        "avg_days_data_processing": 1.2,
        "avg_days_ai_analysis": 3.8,
        "avg_days_manual_review": 7.5
    }
    
    metrics = PipelineMetrics(**metrics_data)
    session.add(metrics)
    await session.commit()

async def create_investment_weights(session: AsyncSession, users: List[User]):
    """Create investment weights configuration"""
    admin_user = next(u for u in users if u.role == UserRole.ADMIN)
    
    weights_data = {
        "market_size_weight": 25.0,
        "team_experience_weight": 30.0,
        "business_model_weight": 20.0,
        "traction_weight": 15.0,
        "financial_health_weight": 10.0,
        "created_by_id": admin_user.id,
        "is_active": True
    }
    
    weights = InvestmentWeights(**weights_data)
    session.add(weights)
    await session.commit()

async def seed_database():
    """Main function to seed the database with mock data"""
    async with async_session_local() as session:
        print("🌱 Seeding database with mock data...")
        
        print("📊 Creating industries...")
        industries = await create_industries(session)
        
        print("👥 Creating users...")
        users = await create_users(session)
        
        print("🚀 Creating startup applications...")
        startups = await create_startups(session, industries, users)
        
        print("👨‍💼 Creating founder profiles...")
        await create_founders(session, startups)
        
        print("📁 Creating uploaded files...")
        await create_uploaded_files(session, startups)
        
        print("💰 Creating financial metrics...")
        await create_financial_metrics(session, startups)
        
        print("📝 Creating investment memos...")
        await create_investment_memos(session, startups, users)
        
        print("📈 Creating evaluation history...")
        await create_evaluation_history(session, startups)
        
        print("📊 Creating pipeline metrics...")
        await create_pipeline_metrics(session)
        
        print("⚖️ Creating investment weights...")
        await create_investment_weights(session, users)
        
        print("✅ Database seeding completed successfully!")
        print(f"Created: {len(industries)} industries, {len(users)} users, {len(startups)} startups")

if __name__ == "__main__":
    asyncio.run(seed_database())