"""
Hybrid Database Service
Supports both SQLAlchemy (local/dev) and Supabase (production) backends
"""

import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.supabase_client import get_supabase_client
from app.models import StartupApplication, ApplicationStatus, FundingStage
from app.crud import startup_crud
from app.schemas import StartupApplicationCreate, StartupApplicationUpdate

class DatabaseService:
    """Hybrid database service that works with both SQLAlchemy and Supabase"""
    
    def __init__(self):
        from app.core.config import get_settings
        settings = get_settings()
        
        # Use the smart detection logic from config
        self.use_supabase = settings.should_use_supabase
        
        if self.use_supabase:
            self.supabase = get_supabase_client()
            print(f"🔧 DatabaseService: Using Supabase (URL: {settings.supabase_url[:30]}...)")
        else:
            print(f"[DatabaseService] Using SQLAlchemy ({settings.database_url})")
    
    async def create_startup(
        self, 
        startup_data: Union[StartupApplicationCreate, Dict[str, Any]],
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """Create a new startup application"""
        
        if self.use_supabase:
            return await self._create_startup_supabase(startup_data)
        else:
            return await self._create_startup_sqlalchemy(startup_data, session)
    
    async def get_startup(
        self, 
        startup_id: int,
        session: Optional[AsyncSession] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a startup by ID"""
        
        if self.use_supabase:
            return await self._get_startup_supabase(startup_id)
        else:
            return await self._get_startup_sqlalchemy(startup_id, session)
    
    async def update_startup(
        self,
        startup_id: int,
        startup_data: Union[StartupApplicationUpdate, Dict[str, Any]],
        session: Optional[AsyncSession] = None
    ) -> Optional[Dict[str, Any]]:
        """Update a startup application"""
        
        if self.use_supabase:
            return await self._update_startup_supabase(startup_id, startup_data)
        else:
            return await self._update_startup_sqlalchemy(startup_id, startup_data, session)
    
    async def list_startups(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """List startups with pagination and filters"""
        
        if self.use_supabase:
            return await self._list_startups_supabase(page, page_size, filters)
        else:
            return await self._list_startups_sqlalchemy(page, page_size, filters, session)
    
    # SQLAlchemy implementations
    async def _create_startup_sqlalchemy(
        self, 
        startup_data: StartupApplicationCreate,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Create startup using SQLAlchemy"""
        return await startup_crud.create_startup(session, startup_data)
    
    async def _get_startup_sqlalchemy(
        self, 
        startup_id: int,
        session: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Get startup using SQLAlchemy"""
        startup = await startup_crud.get_startup_by_id(session, startup_id)
        if not startup:
            return None
        
        # Convert SQLAlchemy model to dict
        return {
            "id": startup.id,
            "company_name": startup.company_name,
            "website": startup.website,
            "contact_email": startup.contact_email,
            "contact_name": startup.contact_name,
            "contact_phone": startup.contact_phone,
            "industry_id": startup.industry_id,
            "funding_stage": startup.funding_stage.value if startup.funding_stage else None,
            "funding_amount_requested": startup.funding_amount_requested,
            "current_arr": startup.current_arr,
            "gross_margin": startup.gross_margin,
            "runway_months": startup.runway_months,
            "status": startup.status.value if startup.status else None,
            "ai_score": startup.ai_score,
            "manual_score": startup.manual_score,
            "final_rating": startup.final_rating,
            "created_at": startup.created_at.isoformat() if startup.created_at else None,
            "updated_at": startup.updated_at.isoformat() if startup.updated_at else None,
            "industry": {
                "id": startup.industry.id,
                "name": startup.industry.name,
                "description": startup.industry.description
            } if startup.industry else None
        }
    
    async def _update_startup_sqlalchemy(
        self,
        startup_id: int,
        startup_data: StartupApplicationUpdate,
        session: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Update startup using SQLAlchemy"""
        startup = await startup_crud.update_startup(session, startup_id, startup_data)
        if not startup:
            return None
        
        # Return simple dict to avoid serialization issues
        return {
            "id": startup.id,
            "company_name": startup.company_name,
            "contact_email": startup.contact_email,
            "status": startup.status.value if startup.status else None,
            "updated_at": startup.updated_at.isoformat() if startup.updated_at else None
        }
    
    async def _list_startups_sqlalchemy(
        self,
        page: int,
        page_size: int,
        filters: Optional[Dict[str, Any]],
        session: AsyncSession
    ) -> Dict[str, Any]:
        """List startups using SQLAlchemy"""
        # Use existing CRUD method
        return await startup_crud.get_startups_paginated(
            session, 
            page=page, 
            page_size=page_size, 
            filters=filters or {}
        )
    
    # Supabase implementations
    async def _create_startup_supabase(
        self, 
        startup_data: Union[StartupApplicationCreate, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create startup using Supabase"""
        # Convert Pydantic model to dict if needed
        if hasattr(startup_data, 'dict'):
            data = startup_data.dict()
        else:
            data = startup_data
        
        # Convert enum values to strings
        if 'funding_stage' in data and data['funding_stage']:
            data['funding_stage'] = data['funding_stage'].value if hasattr(data['funding_stage'], 'value') else str(data['funding_stage'])
        
        if 'status' in data and data['status']:
            data['status'] = data['status'].value if hasattr(data['status'], 'value') else str(data['status'])
        else:
            data['status'] = 'new'
        
        # Add timestamps
        now = datetime.utcnow().isoformat()
        data['created_at'] = now
        data['updated_at'] = now
        
        result = self.supabase.table('startup_applications').insert(data).execute()
        
        if result.data:
            return {
                "success": True,
                "data": result.data[0],
                "message": "Startup application created successfully"
            }
        else:
            raise Exception("Failed to create startup application")
    
    async def _get_startup_supabase(self, startup_id: int) -> Optional[Dict[str, Any]]:
        """Get startup using Supabase"""
        result = self.supabase.table('startup_applications').select('*').eq('id', startup_id).execute()
        
        if result.data:
            return result.data[0]
        return None
    
    async def _update_startup_supabase(
        self,
        startup_id: int,
        startup_data: Union[StartupApplicationUpdate, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Update startup using Supabase"""
        # Convert Pydantic model to dict if needed
        if hasattr(startup_data, 'dict'):
            data = startup_data.dict(exclude_unset=True)
        else:
            data = startup_data
        
        # Convert enum values to strings
        if 'funding_stage' in data and data['funding_stage']:
            data['funding_stage'] = data['funding_stage'].value if hasattr(data['funding_stage'], 'value') else str(data['funding_stage'])
        
        if 'status' in data and data['status']:
            data['status'] = data['status'].value if hasattr(data['status'], 'value') else str(data['status'])
        
        # Add update timestamp
        data['updated_at'] = datetime.utcnow().isoformat()
        
        result = self.supabase.table('startup_applications').update(data).eq('id', startup_id).execute()
        
        if result.data:
            return {
                "success": True,
                "data": result.data[0],
                "message": "Startup application updated successfully"
            }
        return None
    
    async def _list_startups_supabase(
        self,
        page: int,
        page_size: int,
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """List startups using Supabase"""
        query = self.supabase.table('startup_applications').select('*')
        
        # Apply filters
        if filters:
            if 'status' in filters:
                query = query.eq('status', filters['status'])
            if 'industry_id' in filters:
                query = query.eq('industry_id', filters['industry_id'])
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        
        result = query.execute()
        
        # Get total count
        count_result = self.supabase.table('startup_applications').select('id', count='exact').execute()
        total = len(count_result.data) if count_result.data else 0
        
        return {
            "items": result.data or [],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
            "has_next": page * page_size < total,
            "has_prev": page > 1
        }

# Global instance
db_service = DatabaseService()