"""
CRUD operations for database entities
Optimized for fast responses with proper indexing and pagination
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from math import ceil

from app.models import (
    StartupApplication, User, Industry, Founder, UploadedFile,
    FinancialMetric, InvestmentMemo, EvaluationHistory,
    PipelineMetrics, InvestmentWeights,
    ApplicationStatus, FundingStage, UserRole
)
from app.schemas import (
    StartupFilters, PaginationParams, PaginatedStartups,
    StartupApplicationCreate, StartupApplicationUpdate,
    InvestmentMemoCreate, InvestmentMemoUpdate
)

class StartupCRUD:
    """CRUD operations for StartupApplication"""
    
    async def get_startups_paginated(
        self,
        session: AsyncSession,
        filters: StartupFilters,
        pagination: PaginationParams,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """
        Get paginated startups with filters and sorting
        Optimized with proper joins and indexing
        """
        # Build base query - simplified for better serialization performance
        query = select(
            StartupApplication.id,
            StartupApplication.company_name,
            StartupApplication.contact_email,
            StartupApplication.status,
            StartupApplication.funding_stage,
            StartupApplication.ai_score,
            StartupApplication.manual_score,
            StartupApplication.final_rating,
            StartupApplication.created_at,
            StartupApplication.updated_at,
            StartupApplication.industry_id,
            StartupApplication.assigned_analyst_id
        )
        
        # Apply filters
        conditions = []
        
        if filters.status:
            conditions.append(StartupApplication.status == filters.status)
        
        if filters.industry_id:
            conditions.append(StartupApplication.industry_id == filters.industry_id)
            
        if filters.funding_stage:
            conditions.append(StartupApplication.funding_stage == filters.funding_stage)
            
        if filters.assigned_analyst_id:
            conditions.append(StartupApplication.assigned_analyst_id == filters.assigned_analyst_id)
            
        if filters.min_ai_score is not None:
            conditions.append(StartupApplication.ai_score >= filters.min_ai_score)
            
        if filters.max_ai_score is not None:
            conditions.append(StartupApplication.ai_score <= filters.max_ai_score)
            
        if filters.search:
            search_term = f"%{filters.search}%"
            conditions.append(
                or_(
                    StartupApplication.company_name.ilike(search_term),
                    StartupApplication.contact_email.ilike(search_term),
                    StartupApplication.contact_name.ilike(search_term)
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply sorting
        sort_column = getattr(StartupApplication, sort_by, StartupApplication.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Get total count for pagination
        count_query = select(func.count()).select_from(
            query.subquery() if conditions else StartupApplication
        )
        if conditions:
            count_query = select(func.count(StartupApplication.id))
            if conditions:
                count_query = count_query.where(and_(*conditions))
        
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        offset = (pagination.page - 1) * pagination.page_size
        query = query.offset(offset).limit(pagination.page_size)
        
        # Execute query
        result = await session.execute(query)
        rows = result.all()
        
        # Convert to serializable format
        items = []
        for row in rows:
            item = {
                "id": row.id,
                "company_name": row.company_name,
                "contact_email": row.contact_email,
                "status": row.status.value if row.status else None,
                "funding_stage": row.funding_stage.value if row.funding_stage else None,
                "ai_score": row.ai_score,
                "manual_score": row.manual_score,
                "final_rating": row.final_rating,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                "industry_id": row.industry_id,
                "assigned_analyst_id": row.assigned_analyst_id
            }
            items.append(item)
        
        # Calculate pagination metadata
        pages = ceil(total / pagination.page_size) if total > 0 else 1
        has_next = pagination.page < pages
        has_prev = pagination.page > 1
        
        return {
            "items": items,
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size,
            "pages": pages,
            "has_next": has_next,
            "has_prev": has_prev
        }
    
    async def get_startup_by_id(
        self,
        session: AsyncSession,
        startup_id: int
    ) -> Optional[StartupApplication]:
        """Get startup by ID with all related data"""
        query = select(StartupApplication).options(
            joinedload(StartupApplication.industry),
            joinedload(StartupApplication.assigned_analyst),
            selectinload(StartupApplication.founders),
            selectinload(StartupApplication.uploaded_files),
            selectinload(StartupApplication.financial_metrics),
            selectinload(StartupApplication.investment_memo),
            selectinload(StartupApplication.evaluation_history)
        ).where(StartupApplication.id == startup_id)
        
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def create_startup(
        self,
        session: AsyncSession,
        startup_data: StartupApplicationCreate
    ) -> StartupApplication:
        """Create new startup application"""
        startup = StartupApplication(**startup_data.dict())
        session.add(startup)
        await session.commit()
        await session.refresh(startup)
        return startup
    
    async def update_startup(
        self,
        session: AsyncSession,
        startup_id: int,
        startup_data: StartupApplicationUpdate
    ) -> Optional[StartupApplication]:
        """Update startup application"""
        query = select(StartupApplication).where(StartupApplication.id == startup_id)
        result = await session.execute(query)
        startup = result.scalar_one_or_none()
        
        if not startup:
            return None
        
        update_data = startup_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(startup, field, value)
        
        await session.commit()
        await session.refresh(startup)
        return startup

class DashboardCRUD:
    """CRUD operations for dashboard metrics"""
    
    async def get_dashboard_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics"""
        
        # Total applications
        total_apps_query = select(func.count(StartupApplication.id))
        total_apps_result = await session.execute(total_apps_query)
        total_applications = total_apps_result.scalar() or 0
        
        # Applications in AI processing
        ai_processing_query = select(func.count(StartupApplication.id)).where(
            StartupApplication.status.in_([ApplicationStatus.DATA_PROCESSING, ApplicationStatus.AI_ANALYSIS])
        )
        ai_processing_result = await session.execute(ai_processing_query)
        ai_processing = ai_processing_result.scalar() or 0
        
        # Completed evaluations
        completed_query = select(func.count(StartupApplication.id)).where(
            StartupApplication.status == ApplicationStatus.COMPLETED
        )
        completed_result = await session.execute(completed_query)
        completed_analysis = completed_result.scalar() or 0
        
        # Average AI score
        avg_score_query = select(func.avg(StartupApplication.ai_score)).where(
            StartupApplication.ai_score.isnot(None)
        )
        avg_score_result = await session.execute(avg_score_query)
        average_score = float(avg_score_result.scalar() or 0)
        
        # Recent applications (last 10) - simplified for serialization
        recent_query = select(
            StartupApplication.id,
            StartupApplication.company_name,
            StartupApplication.status,
            StartupApplication.ai_score,
            StartupApplication.created_at
        ).order_by(desc(StartupApplication.created_at)).limit(10)
        
        recent_result = await session.execute(recent_query)
        recent_applications = [
            {
                "id": row.id,
                "company_name": row.company_name,
                "status": row.status.value,
                "ai_score": row.ai_score,
                "created_at": row.created_at.isoformat()
            }
            for row in recent_result.all()
        ]
        
        # Pipeline metrics - simplified
        pipeline_query = select(PipelineMetrics).order_by(desc(PipelineMetrics.calculated_at)).limit(1)
        pipeline_result = await session.execute(pipeline_query)
        pipeline_metrics_obj = pipeline_result.scalar_one_or_none()
        
        pipeline_metrics = None
        if pipeline_metrics_obj:
            pipeline_metrics = {
                "total_applications": pipeline_metrics_obj.total_applications,
                "applications_in_ai_processing": pipeline_metrics_obj.applications_in_ai_processing,
                "completed_evaluations": pipeline_metrics_obj.completed_evaluations,
                "average_ai_score": pipeline_metrics_obj.average_ai_score,
                "calculated_at": pipeline_metrics_obj.calculated_at.isoformat()
            }
        
        return {
            "total_applications": total_applications,
            "ai_processing": ai_processing,
            "completed_analysis": completed_analysis,
            "average_score": round(average_score, 1),
            "recent_applications": recent_applications,
            "pipeline_metrics": pipeline_metrics
        }

class PipelineCRUD:
    """CRUD operations for deal pipeline"""
    
    async def get_pipeline_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """Get deal pipeline statistics"""
        
        # Applications by status
        status_query = select(
            StartupApplication.status,
            func.count(StartupApplication.id)
        ).group_by(StartupApplication.status)
        
        status_result = await session.execute(status_query)
        stages = {status.value: count for status, count in status_result.all()}
        
        # Conversion rates (simplified calculation)
        total_apps = sum(stages.values())
        conversion_rates = {}
        if total_apps > 0:
            conversion_rates = {
                "data_processing": (stages.get("ai_analysis", 0) / total_apps) * 100,
                "ai_analysis": (stages.get("manual_review", 0) / total_apps) * 100,
                "manual_review": (stages.get("partner_review", 0) / total_apps) * 100,
                "partner_review": (stages.get("completed", 0) / total_apps) * 100
            }
        
        # Average days per stage (from evaluation history)
        avg_days_query = select(
            EvaluationHistory.new_status,
            func.avg(EvaluationHistory.time_in_previous_stage)
        ).group_by(EvaluationHistory.new_status)
        
        avg_days_result = await session.execute(avg_days_query)
        avg_days_per_stage = {
            status.value: round((avg_minutes or 0) / 1440, 1)  # Convert minutes to days
            for status, avg_minutes in avg_days_result.all()
        }
        
        # Bottlenecks (statuses with most applications)
        bottlenecks = dict(sorted(stages.items(), key=lambda x: x[1], reverse=True)[:3])
        
        # Weekly throughput (completed applications in last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        
        weekly_query = select(func.count(StartupApplication.id)).where(
            and_(
                StartupApplication.status == ApplicationStatus.COMPLETED,
                StartupApplication.completed_at >= week_ago
            )
        )
        weekly_result = await session.execute(weekly_query)
        weekly_throughput = weekly_result.scalar() or 0
        
        return {
            "stages": stages,
            "conversion_rates": conversion_rates,
            "avg_days_per_stage": avg_days_per_stage,
            "bottlenecks": bottlenecks,
            "weekly_throughput": weekly_throughput
        }

class InvestmentMemoCRUD:
    """CRUD operations for investment memos"""
    
    async def get_memo_by_startup_id(
        self,
        session: AsyncSession,
        startup_id: int
    ) -> Optional[InvestmentMemo]:
        """Get investment memo for a startup"""
        query = select(InvestmentMemo).options(
            joinedload(InvestmentMemo.author),
            joinedload(InvestmentMemo.startup_application)
        ).where(InvestmentMemo.startup_application_id == startup_id)
        
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def create_memo(
        self,
        session: AsyncSession,
        memo_data: InvestmentMemoCreate,
        author_id: int
    ) -> InvestmentMemo:
        """Create new investment memo"""
        memo = InvestmentMemo(**memo_data.dict(), author_id=author_id)
        session.add(memo)
        await session.commit()
        await session.refresh(memo)
        return memo
    
    async def update_memo(
        self,
        session: AsyncSession,
        memo_id: int,
        memo_data: InvestmentMemoUpdate
    ) -> Optional[InvestmentMemo]:
        """Update investment memo"""
        query = select(InvestmentMemo).where(InvestmentMemo.id == memo_id)
        result = await session.execute(query)
        memo = result.scalar_one_or_none()
        
        if not memo:
            return None
        
        update_data = memo_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(memo, field, value)
        
        await session.commit()
        await session.refresh(memo)
        return memo

class UserCRUD:
    """CRUD operations for users"""
    
    async def get_all_users(self, session: AsyncSession) -> List[User]:
        """Get all users"""
        query = select(User).where(User.is_active == True).order_by(User.full_name)
        result = await session.execute(query)
        return result.scalars().all()
    
    async def get_user_by_id(self, session: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

class IndustryCRUD:
    """CRUD operations for industries"""
    
    async def get_all_industries(self, session: AsyncSession) -> List[Industry]:
        """Get all industries"""
        query = select(Industry).order_by(Industry.name)
        result = await session.execute(query)
        return result.scalars().all()

# Create instances
startup_crud = StartupCRUD()
dashboard_crud = DashboardCRUD()
pipeline_crud = PipelineCRUD()
memo_crud = InvestmentMemoCRUD()
user_crud = UserCRUD()
industry_crud = IndustryCRUD()