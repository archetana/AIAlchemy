"""
File Upload API endpoints
Handles file uploads, downloads, and management for startup applications
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import io
from datetime import datetime

from app.database import get_db
from app.services.file_storage import file_storage_service
from app.crud import startup_crud
from app.models import UploadedFile, StartupApplication
from sqlalchemy import select

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

@router.post("/startup/{startup_id}/files")
async def upload_startup_files(
    startup_id: int,
    files: List[UploadFile] = File(...),
    file_type: str = Form("document", description="Type of files: pitch_deck, financial_docs, team_info, legal_docs, etc."),
    description: Optional[str] = Form(None, description="Optional description of the files"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload multiple files for a startup application
    
    Supported file types:
    - Documents: PDF, DOC, DOCX, PPT, PPTX
    - Images: JPG, PNG, GIF
    - Videos: MP4, MOV, AVI  
    - Audio: MP3, WAV, M4A
    """
    
    # Verify startup exists
    startup = await startup_crud.get_startup_by_id(db, startup_id)
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Upload file using storage service
            file_metadata = await file_storage_service.upload_file(
                file=file,
                startup_id=startup_id,
                file_type=file_type,
                description=description
            )
            
            # Create database record
            db_file = UploadedFile(
                id=file_metadata['file_id'],
                startup_application_id=startup_id,
                original_filename=file_metadata['original_filename'],
                stored_filename=file_metadata['stored_filename'],
                file_path=file_metadata['storage_path'],
                file_type=file_type,
                content_type=file_metadata['content_type'],
                file_size=file_metadata['file_size'],
                file_hash=file_metadata['file_hash'],
                description=description,
                upload_timestamp=datetime.fromisoformat(file_metadata['upload_timestamp'].replace('Z', '+00:00')),
                is_processed=False,
                metadata_json={
                    'scan_result': file_metadata['scan_result'],
                    'storage_backend': file_metadata['storage_backend'],
                    'relative_path': file_metadata['relative_path']
                }
            )
            
            db.add(db_file)
            uploaded_files.append({
                'file_id': file_metadata['file_id'],
                'filename': file_metadata['original_filename'],
                'size': file_metadata['file_size'],
                'type': file_metadata['content_type'],
                'status': 'uploaded'
            })
            
        except HTTPException as e:
            errors.append({
                'filename': file.filename,
                'error': e.detail,
                'status_code': e.status_code
            })
        except Exception as e:
            errors.append({
                'filename': file.filename, 
                'error': f"Upload failed: {str(e)}",
                'status_code': 500
            })
    
    # Commit successful uploads
    if uploaded_files:
        await db.commit()
    
    return {
        'success': len(uploaded_files) > 0,
        'uploaded_files': uploaded_files,
        'errors': errors,
        'summary': {
            'total_files': len(files),
            'successful_uploads': len(uploaded_files),
            'failed_uploads': len(errors)
        }
    }

@router.get("/startup/{startup_id}/files")
async def get_startup_files(
    startup_id: int,
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of files to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get list of files uploaded for a startup"""
    
    # Verify startup exists
    startup = await startup_crud.get_startup_by_id(db, startup_id)
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    # Build query
    query = select(UploadedFile).where(UploadedFile.startup_application_id == startup_id)
    
    if file_type:
        query = query.where(UploadedFile.file_type == file_type)
    
    query = query.order_by(UploadedFile.upload_timestamp.desc()).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    files = result.scalars().all()
    
    # Format response
    file_list = []
    for file in files:
        file_list.append({
            'file_id': file.id,
            'original_filename': file.original_filename,
            'file_type': file.file_type,
            'content_type': file.content_type,
            'file_size': file.file_size,
            'description': file.description,
            'upload_timestamp': file.upload_timestamp.isoformat(),
            'is_processed': file.is_processed,
            'download_url': f"/api/uploads/files/{file.id}",
            'metadata': file.metadata_json
        })
    
    return {
        'success': True,
        'startup_id': startup_id,
        'files': file_list,
        'total_files': len(file_list),
        'file_types': list(set(f['file_type'] for f in file_list)) if file_list else []
    }

@router.get("/files/{file_id}")
async def download_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Download a specific file"""
    
    # Get file record from database
    query = select(UploadedFile).where(UploadedFile.id == file_id)
    result = await db.execute(query)
    db_file = result.scalar_one_or_none()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Get file content from storage
        file_content = await file_storage_service.get_file(db_file.file_path)
        
        # Create streaming response
        file_stream = io.BytesIO(file_content)
        
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=db_file.content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{db_file.original_filename}"',
                'Content-Length': str(len(file_content))
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a specific file"""
    
    # Get file record from database
    query = select(UploadedFile).where(UploadedFile.id == file_id)
    result = await db.execute(query)
    db_file = result.scalar_one_or_none()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Delete from storage
        deleted = await file_storage_service.delete_file(db_file.file_path)
        
        if deleted:
            # Delete from database
            await db.delete(db_file)
            await db.commit()
            
            return {
                'success': True,
                'message': f"File '{db_file.original_filename}' deleted successfully",
                'file_id': file_id
            }
        else:
            return {
                'success': False,
                'message': "File not found in storage, but database record removed",
                'file_id': file_id
            }
            
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.get("/stats/summary")
async def get_upload_stats(
    startup_id: Optional[int] = Query(None, description="Filter stats by startup ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get upload statistics and summary"""
    
    from sqlalchemy import func, case
    
    # Base query
    query = select(
        func.count(UploadedFile.id).label('total_files'),
        func.sum(UploadedFile.file_size).label('total_size'),
        func.count(case((UploadedFile.is_processed == True, 1))).label('processed_files'),
        func.count(case((UploadedFile.is_processed == False, 1))).label('pending_files')
    )
    
    if startup_id:
        query = query.where(UploadedFile.startup_application_id == startup_id)
    
    result = await db.execute(query)
    stats = result.first()
    
    # Get file type breakdown
    type_query = select(
        UploadedFile.file_type,
        func.count(UploadedFile.id).label('count'),
        func.sum(UploadedFile.file_size).label('total_size')
    ).group_by(UploadedFile.file_type)
    
    if startup_id:
        type_query = type_query.where(UploadedFile.startup_application_id == startup_id)
    
    type_result = await db.execute(type_query)
    file_types = [
        {
            'file_type': row.file_type,
            'count': row.count,
            'total_size': row.total_size or 0
        }
        for row in type_result
    ]
    
    return {
        'success': True,
        'total_files': stats.total_files or 0,
        'total_size_bytes': stats.total_size or 0,
        'total_size_mb': round((stats.total_size or 0) / (1024 * 1024), 2),
        'processed_files': stats.processed_files or 0,
        'pending_files': stats.pending_files or 0,
        'file_types': file_types,
        'storage_backend': 'gcs' if file_storage_service.use_gcs else 'local'
    }