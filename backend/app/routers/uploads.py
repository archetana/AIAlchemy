"""
File Upload API endpoints
Handles file uploads and processing for startup materials
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os
import aiofiles
from pathlib import Path
import uuid

from app.database import get_db
from app.schemas import UploadedFile as UploadedFileSchema
from app.models import UploadedFile, StartupApplication, FileStatus

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

# Configure upload directory
UPLOAD_DIR = Path("/tmp/uploads")  # Use /tmp for sandbox environment
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv"}

@router.post("/startup/{startup_id}/files", response_model=List[UploadedFileSchema])
async def upload_startup_files(
    startup_id: int,
    file_type: str = Form(..., description="Type of file: pitch_deck, financial_model, etc."),
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload multiple files for a startup application
    """
    try:
        # Verify startup exists
        from sqlalchemy import select
        startup_query = select(StartupApplication).where(StartupApplication.id == startup_id)
        startup_result = await db.execute(startup_query)
        startup = startup_result.scalar_one_or_none()
        
        if not startup:
            raise HTTPException(status_code=404, detail="Startup not found")
        
        uploaded_files = []
        
        for file in files:
            # Validate file
            if not file.filename:
                continue
            
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            
            # Check file size
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} is too large. Maximum size: 10MB"
                )
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = UPLOAD_DIR / str(startup_id) / unique_filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            # Create database record
            uploaded_file = UploadedFile(
                startup_application_id=startup_id,
                filename=unique_filename,
                original_filename=file.filename,
                file_type=file_type,
                file_size=len(content),
                mime_type=file.content_type or "application/octet-stream",
                file_path=str(file_path),
                status=FileStatus.PROCESSING,
                processing_progress=0
            )
            
            db.add(uploaded_file)
            await db.flush()  # Get the ID
            await db.refresh(uploaded_file)
            
            uploaded_files.append(uploaded_file)
        
        await db.commit()
        
        # Simulate file processing (in real app, this would be async background task)
        for uploaded_file in uploaded_files:
            uploaded_file.status = FileStatus.COMPLETED
            uploaded_file.processing_progress = 100
        
        await db.commit()
        
        return uploaded_files
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload files: {str(e)}")

@router.get("/startup/{startup_id}/files", response_model=List[UploadedFileSchema])
async def get_startup_files(
    startup_id: int,
    file_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all uploaded files for a startup
    """
    try:
        from sqlalchemy import select, and_
        
        query = select(UploadedFile).where(UploadedFile.startup_application_id == startup_id)
        
        if file_type:
            query = query.where(UploadedFile.file_type == file_type)
        
        query = query.order_by(UploadedFile.uploaded_at.desc())
        
        result = await db.execute(query)
        files = result.scalars().all()
        
        return files
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch files: {str(e)}")

@router.get("/files/{file_id}")
async def download_file(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Download a specific file
    """
    try:
        from sqlalchemy import select
        
        query = select(UploadedFile).where(UploadedFile.id == file_id)
        result = await db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = Path(file_record.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(
            path=file_path,
            filename=file_record.original_filename,
            media_type=file_record.mime_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific file
    """
    try:
        from sqlalchemy import select
        
        query = select(UploadedFile).where(UploadedFile.id == file_id)
        result = await db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete file from disk
        file_path = Path(file_record.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # Delete record from database
        await db.delete(file_record)
        await db.commit()
        
        return {
            "success": True,
            "data": {
                "file_id": file_id,
                "message": "File deleted successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.get("/files/{file_id}/processing-status")
async def get_file_processing_status(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get file processing status
    """
    try:
        from sqlalchemy import select
        
        query = select(UploadedFile).where(UploadedFile.id == file_id)
        result = await db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "success": True,
            "data": {
                "file_id": file_id,
                "status": file_record.status.value,
                "progress": file_record.processing_progress,
                "processed_at": file_record.processed_at,
                "extraction_metadata": file_record.extraction_metadata
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get processing status: {str(e)}")

@router.post("/files/{file_id}/extract-data")
async def extract_file_data(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Simulate data extraction from uploaded file
    In production, this would trigger background processing
    """
    try:
        from datetime import datetime
        from sqlalchemy import select
        
        query = select(UploadedFile).where(UploadedFile.id == file_id)
        result = await db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Simulate extraction metadata based on file type
        extraction_metadata = {}
        
        if file_record.file_type == "pitch_deck":
            extraction_metadata = {
                "slides_count": 12,
                "extracted_text": "Sample pitch deck content...",
                "key_metrics": ["ARR: $2.4M", "Growth Rate: 15%", "Team Size: 25"],
                "market_size": "$50B TAM"
            }
        elif file_record.file_type == "financial_model":
            extraction_metadata = {
                "revenue_projections": {"2024": 2400000, "2025": 3600000, "2026": 5400000},
                "expenses": {"2024": 1800000, "2025": 2700000, "2026": 3780000},
                "key_ratios": {"gross_margin": 75.2, "burn_rate": 150000},
                "metrics_extracted": 15
            }
        
        # Update file record
        file_record.extraction_metadata = extraction_metadata
        file_record.status = FileStatus.COMPLETED
        file_record.processing_progress = 100
        file_record.processed_at = datetime.now()
        
        await db.commit()
        
        return {
            "success": True,
            "data": {
                "file_id": file_id,
                "extraction_completed": True,
                "metadata": extraction_metadata
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract data: {str(e)}")

@router.get("/stats/summary")
async def get_upload_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get file upload statistics
    """
    try:
        from sqlalchemy import select, func
        
        # Total files
        total_query = select(func.count(UploadedFile.id))
        total_result = await db.execute(total_query)
        total_files = total_result.scalar() or 0
        
        # Files by status
        status_query = select(
            UploadedFile.status,
            func.count(UploadedFile.id)
        ).group_by(UploadedFile.status)
        
        status_result = await db.execute(status_query)
        status_counts = {status.value: count for status, count in status_result.all()}
        
        # Files by type
        type_query = select(
            UploadedFile.file_type,
            func.count(UploadedFile.id)
        ).group_by(UploadedFile.file_type)
        
        type_result = await db.execute(type_query)
        type_counts = dict(type_result.all())
        
        # Total storage used
        size_query = select(func.sum(UploadedFile.file_size))
        size_result = await db.execute(size_query)
        total_size = size_result.scalar() or 0
        
        return {
            "success": True,
            "data": {
                "total_files": total_files,
                "status_breakdown": status_counts,
                "file_type_breakdown": type_counts,
                "total_storage_bytes": total_size,
                "total_storage_mb": round(total_size / (1024 * 1024), 2)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch upload stats: {str(e)}")