"""
Document Processing API Endpoints for AIAlchemy

Handles document upload, validation, processing, and memo generation
using the multi-agent AI system.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import (
    StartupApplication, UploadedFile, ProcessingPipeline, 
    DocumentExtraction, GeneratedMemo, FileValidationLog,
    DocumentProcessingStatus, PipelineStage
)
from app.agents import DocumentAIAgent, MemoGeneratorAgent, PipelineOrchestrator
from app.agents.document_ai_agent import DocumentAIConfig
from app.agents.memo_generator_agent import MemoGeneratorConfig, MemoSection
from app.agents.pipeline_orchestrator import PipelineConfig
from app.services.enhanced_file_storage import (
    EnhancedFileStorageService, FileStorageConfig
)

router = APIRouter(prefix="/api/v1/document-processing", tags=["document-processing"])
logger = logging.getLogger(__name__)

# Pydantic Models for API

class DocumentUploadRequest(BaseModel):
    startup_application_id: int
    file_type: str = "pitch_deck"  # pitch_deck, financial_docs, team_info, etc.
    description: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    success: bool
    file_id: str
    validation_result: Dict[str, Any]
    upload_metadata: Dict[str, Any]
    message: str


class PipelineStartRequest(BaseModel):
    startup_application_id: int
    file_ids: List[str]
    processing_options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    memo_sections: Optional[List[MemoSection]] = None
    custom_instructions: Optional[str] = None


class PipelineStatusResponse(BaseModel):
    pipeline_id: str
    status: DocumentProcessingStatus
    current_stage: PipelineStage
    progress_percentage: float
    stages_completed: List[PipelineStage]
    stages_failed: List[PipelineStage]
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_duration_ms: Optional[int] = None
    error_message: Optional[str] = None


class DocumentExtractionResponse(BaseModel):
    extraction_id: int
    file_id: str
    confidence_score: float
    company_name: Optional[str] = None
    industry: Optional[str] = None
    financial_summary: Dict[str, Any]
    team_summary: Dict[str, Any]
    business_summary: Dict[str, Any]
    extraction_quality: str


class MemoResponse(BaseModel):
    memo_id: int
    startup_application_id: int
    overall_score: float
    recommendation_type: str
    risk_level: str
    success_probability: float
    sections: Dict[str, str]
    key_strengths: List[str]
    key_concerns: List[str]
    generation_metadata: Dict[str, Any]


# Initialize services (in production, these would be dependency injected)
file_storage_service = EnhancedFileStorageService(FileStorageConfig())

def get_pipeline_orchestrator() -> PipelineOrchestrator:
    """Get configured pipeline orchestrator"""
    
    # Create agent configurations
    doc_ai_config = DocumentAIConfig(
        name="document_ai_agent",
        project_id="your-gcp-project",  # Would come from environment
        location="us",
        timeout=300,
        max_file_size_mb=50
    )
    
    memo_config = MemoGeneratorConfig(
        name="memo_generator_agent",
        gemini_model="gemini-1.5-pro",
        max_tokens=8192,
        temperature=0.7,
        timeout=600
    )
    
    # Create pipeline configuration
    pipeline_config = PipelineConfig(
        document_ai_config=doc_ai_config,
        memo_generator_config=memo_config,
        enable_parallel_processing=True,
        max_concurrent_stages=3,
        auto_retry_failed_stages=True,
        stage_timeout_minutes=10
    )
    
    return PipelineOrchestrator(pipeline_config)


# API Endpoints

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    startup_application_id: int = Form(...),
    file_type: str = Form("pitch_deck"),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload and validate a document for processing.
    
    This endpoint handles secure file upload with comprehensive validation
    including virus scanning, format verification, and metadata extraction.
    """
    
    try:
        # Validate startup application exists
        startup = db.query(StartupApplication).filter(
            StartupApplication.id == startup_application_id
        ).first()
        
        if not startup:
            raise HTTPException(
                status_code=404,
                detail="Startup application not found"
            )
        
        # Validate file
        validation_result = await file_storage_service.validate_file(file)
        
        if not validation_result.valid:
            return DocumentUploadResponse(
                success=False,
                file_id="",
                validation_result=validation_result.dict(),
                upload_metadata={},
                message=f"File validation failed: {', '.join(validation_result.validation_errors)}"
            )
        
        # Store file
        storage_result = await file_storage_service.store_file(
            file,
            validate_first=False,  # Already validated
            metadata={
                "startup_application_id": startup_application_id,
                "file_type": file_type,
                "description": description,
                "uploaded_by": "api_user"  # Would get from auth context
            }
        )
        
        if not storage_result.success:
            raise HTTPException(
                status_code=500,
                detail=f"File storage failed: {', '.join(storage_result.errors)}"
            )
        
        # Create database record
        uploaded_file = UploadedFile(
            id=storage_result.file_id,
            startup_application_id=startup_application_id,
            original_filename=validation_result.original_filename,
            stored_filename=validation_result.filename,
            file_type=file_type,
            content_type=validation_result.mime_type,
            file_size=validation_result.file_size,
            file_hash=validation_result.file_hash,
            file_path=storage_result.storage_path,
            storage_backend="gcs" if storage_result.public_url else "local",
            description=description,
            metadata_json=storage_result.metadata,
            is_safe=validation_result.virus_scan_result in [None, "OK"],
            upload_timestamp=datetime.now()
        )
        
        db.add(uploaded_file)
        
        # Create validation log
        validation_log = FileValidationLog(
            file_id=storage_result.file_id,
            validation_passed=validation_result.valid,
            file_size_bytes=validation_result.file_size,
            detected_mime_type=validation_result.mime_type,
            file_hash_sha256=validation_result.file_hash,
            virus_scan_performed=validation_result.virus_scan_result is not None,
            virus_scan_result=validation_result.virus_scan_result or "not_scanned",
            validation_errors=validation_result.validation_errors,
            validation_warnings=validation_result.validation_warnings,
            content_type_verified=True
        )
        
        db.add(validation_log)
        db.commit()
        
        logger.info(f"Document uploaded successfully: {storage_result.file_id}")
        
        return DocumentUploadResponse(
            success=True,
            file_id=storage_result.file_id,
            validation_result=validation_result.dict(),
            upload_metadata=storage_result.metadata,
            message="Document uploaded and validated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@router.post("/pipeline/start")
async def start_processing_pipeline(
    request: PipelineStartRequest,
    db: Session = Depends(get_db)
):
    """
    Start the document processing pipeline for uploaded files.
    
    This initiates the complete workflow from document processing
    to investment memo generation.
    """
    
    try:
        # Validate startup application
        startup = db.query(StartupApplication).filter(
            StartupApplication.id == request.startup_application_id
        ).first()
        
        if not startup:
            raise HTTPException(
                status_code=404,
                detail="Startup application not found"
            )
        
        # Validate all file IDs exist
        files = db.query(UploadedFile).filter(
            UploadedFile.id.in_(request.file_ids),
            UploadedFile.startup_application_id == request.startup_application_id
        ).all()
        
        if len(files) != len(request.file_ids):
            raise HTTPException(
                status_code=400,
                detail="One or more files not found or don't belong to this startup"
            )
        
        # Check if there's already an active pipeline for this startup
        existing_pipeline = db.query(ProcessingPipeline).filter(
            ProcessingPipeline.startup_application_id == request.startup_application_id,
            ProcessingPipeline.status.in_([
                DocumentProcessingStatus.PENDING,
                DocumentProcessingStatus.VALIDATING,
                DocumentProcessingStatus.PROCESSING,
                DocumentProcessingStatus.EXTRACTING
            ])
        ).first()
        
        if existing_pipeline:
            raise HTTPException(
                status_code=409,
                detail=f"Pipeline already running for this startup: {existing_pipeline.id}"
            )
        
        # Get pipeline orchestrator
        orchestrator = get_pipeline_orchestrator()
        
        # Prepare file data for processing
        file_paths = []
        filenames = []
        
        for file in files:
            # Retrieve file content
            file_content = await file_storage_service.retrieve_file(file.id, file.file_path)
            if not file_content:
                raise HTTPException(
                    status_code=500,
                    detail=f"Could not retrieve file content for {file.id}"
                )
            
            file_paths.append(file_content)
            filenames.append(file.original_filename)
        
        # Start pipeline
        pipeline_progress = await orchestrator.start_pipeline(
            file_data=file_paths,
            filenames=filenames,
            custom_config={
                "startup_application_id": request.startup_application_id,
                "memo_sections": request.memo_sections,
                "custom_instructions": request.custom_instructions,
                **request.processing_options
            }
        )
        
        # Create database record
        db_pipeline = ProcessingPipeline(
            id=pipeline_progress.pipeline_id,
            startup_application_id=request.startup_application_id,
            status=DocumentProcessingStatus.PENDING,
            current_stage=PipelineStage.INITIALIZATION,
            progress_percentage=0.0,
            stages_completed=[],
            stages_failed=[],
            processing_config=request.processing_options,
            input_files=request.file_ids,
            started_at=pipeline_progress.start_time
        )
        
        db.add(db_pipeline)
        db.commit()
        
        logger.info(f"Processing pipeline started: {pipeline_progress.pipeline_id}")
        
        return {
            "pipeline_id": pipeline_progress.pipeline_id,
            "status": "started",
            "message": "Processing pipeline initiated successfully",
            "estimated_completion_minutes": 10  # Rough estimate
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pipeline start failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start processing pipeline: {str(e)}"
        )


@router.get("/pipeline/{pipeline_id}/status", response_model=PipelineStatusResponse)
async def get_pipeline_status(
    pipeline_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the current status of a processing pipeline.
    
    Provides real-time updates on pipeline progress, current stage,
    and any errors or warnings.
    """
    
    try:
        # Get pipeline from database
        pipeline = db.query(ProcessingPipeline).filter(
            ProcessingPipeline.id == pipeline_id
        ).first()
        
        if not pipeline:
            raise HTTPException(
                status_code=404,
                detail="Pipeline not found"
            )
        
        # Get live status from orchestrator if pipeline is active
        orchestrator = get_pipeline_orchestrator()
        live_progress = await orchestrator.get_pipeline_status(pipeline_id)
        
        # Update database with live status if available
        if live_progress:
            pipeline.status = DocumentProcessingStatus(live_progress.status.value)
            pipeline.current_stage = PipelineStage(live_progress.current_stage.value)
            pipeline.progress_percentage = live_progress.progress_percentage
            pipeline.stages_completed = [stage.value for stage in live_progress.stages_completed]
            pipeline.stages_failed = [stage.value for stage in live_progress.stages_failed]
            
            if live_progress.end_time:
                pipeline.completed_at = live_progress.end_time
                pipeline.total_duration_ms = live_progress.total_duration_ms
            
            db.commit()
        
        return PipelineStatusResponse(
            pipeline_id=pipeline.id,
            status=pipeline.status,
            current_stage=pipeline.current_stage,
            progress_percentage=pipeline.progress_percentage,
            stages_completed=[PipelineStage(stage) for stage in pipeline.stages_completed],
            stages_failed=[PipelineStage(stage) for stage in pipeline.stages_failed],
            started_at=pipeline.started_at,
            completed_at=pipeline.completed_at,
            total_duration_ms=pipeline.total_duration_ms,
            error_message=pipeline.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pipeline status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve pipeline status: {str(e)}"
        )


@router.get("/pipeline/{pipeline_id}/results")
async def get_pipeline_results(
    pipeline_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the complete results of a finished processing pipeline.
    
    Returns document extraction results and generated investment memo.
    """
    
    try:
        # Get pipeline
        pipeline = db.query(ProcessingPipeline).filter(
            ProcessingPipeline.id == pipeline_id
        ).first()
        
        if not pipeline:
            raise HTTPException(
                status_code=404,
                detail="Pipeline not found"
            )
        
        if pipeline.status != DocumentProcessingStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Pipeline not completed. Current status: {pipeline.status}"
            )
        
        # Get document extractions
        extractions = db.query(DocumentExtraction).filter(
            DocumentExtraction.pipeline_id == pipeline_id
        ).all()
        
        # Get generated memo
        memo = db.query(GeneratedMemo).filter(
            GeneratedMemo.pipeline_id == pipeline_id
        ).first()
        
        # Format results
        extraction_results = []
        for extraction in extractions:
            extraction_results.append(DocumentExtractionResponse(
                extraction_id=extraction.id,
                file_id=extraction.file_id,
                confidence_score=extraction.confidence_score or 0.0,
                company_name=extraction.company_name,
                industry=extraction.industry,
                financial_summary={
                    "revenue_current": extraction.revenue_current,
                    "revenue_projected": extraction.revenue_projected,
                    "funding_amount": extraction.funding_amount,
                    "funding_stage": extraction.funding_stage,
                    "burn_rate": extraction.burn_rate,
                    "runway_months": extraction.runway_months,
                    "valuation": extraction.valuation
                },
                team_summary={
                    "founders": extraction.founders or [],
                    "team_size": extraction.team_size,
                    "key_roles": extraction.key_roles or [],
                    "advisors": extraction.advisors or []
                },
                business_summary={
                    "problem_statement": extraction.problem_statement,
                    "solution_description": extraction.solution_description
                },
                extraction_quality=extraction.extraction_quality or "medium"
            ))
        
        memo_result = None
        if memo:
            memo_result = MemoResponse(
                memo_id=memo.id,
                startup_application_id=memo.startup_application_id,
                overall_score=memo.overall_score or 0.0,
                recommendation_type=memo.recommendation_type or "hold",
                risk_level=memo.risk_level or "medium",
                success_probability=memo.success_probability or 0.5,
                sections={
                    "executive_summary": memo.executive_summary or "",
                    "investment_thesis": memo.investment_thesis or "",
                    "company_overview": memo.company_overview or "",
                    "market_analysis": memo.market_analysis or "",
                    "business_model": memo.business_model or "",
                    "team_assessment": memo.team_assessment or "",
                    "financial_analysis": memo.financial_analysis or "",
                    "risk_assessment": memo.risk_assessment or "",
                    "competitive_landscape": memo.competitive_landscape or "",
                    "recommendation": memo.recommendation or ""
                },
                key_strengths=memo.key_strengths or [],
                key_concerns=memo.key_concerns or [],
                generation_metadata={
                    "generation_method": memo.generation_method,
                    "generation_model": memo.generation_model,
                    "generation_time_ms": memo.generation_time_ms,
                    "total_words": memo.total_words,
                    "confidence_score": memo.confidence_score
                }
            )
        
        return {
            "pipeline_id": pipeline_id,
            "startup_application_id": pipeline.startup_application_id,
            "status": pipeline.status,
            "completed_at": pipeline.completed_at,
            "total_duration_ms": pipeline.total_duration_ms,
            "document_extractions": extraction_results,
            "investment_memo": memo_result,
            "processing_summary": {
                "stages_completed": pipeline.stages_completed,
                "stages_failed": pipeline.stages_failed,
                "progress_percentage": pipeline.progress_percentage
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pipeline results: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve pipeline results: {str(e)}"
        )


@router.post("/pipeline/{pipeline_id}/cancel")
async def cancel_pipeline(
    pipeline_id: str,
    db: Session = Depends(get_db)
):
    """
    Cancel a running processing pipeline.
    """
    
    try:
        # Get pipeline
        pipeline = db.query(ProcessingPipeline).filter(
            ProcessingPipeline.id == pipeline_id
        ).first()
        
        if not pipeline:
            raise HTTPException(
                status_code=404,
                detail="Pipeline not found"
            )
        
        if pipeline.status not in [
            DocumentProcessingStatus.PENDING,
            DocumentProcessingStatus.VALIDATING,
            DocumentProcessingStatus.PROCESSING,
            DocumentProcessingStatus.EXTRACTING
        ]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel pipeline in status: {pipeline.status}"
            )
        
        # Cancel in orchestrator
        orchestrator = get_pipeline_orchestrator()
        cancelled = await orchestrator.cancel_pipeline(pipeline_id)
        
        if cancelled:
            # Update database
            pipeline.status = DocumentProcessingStatus.CANCELLED
            pipeline.completed_at = datetime.now()
            pipeline.error_message = "Pipeline cancelled by user"
            db.commit()
            
            return {"message": "Pipeline cancelled successfully"}
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to cancel pipeline"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel pipeline: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel pipeline: {str(e)}"
        )


@router.get("/files/{file_id}/validation")
async def get_file_validation(
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed validation information for an uploaded file.
    """
    
    try:
        # Get file
        file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get validation log
        validation_log = db.query(FileValidationLog).filter(
            FileValidationLog.file_id == file_id
        ).first()
        
        return {
            "file_id": file_id,
            "original_filename": file.original_filename,
            "file_size": file.file_size,
            "content_type": file.content_type,
            "is_safe": file.is_safe,
            "validation_log": validation_log.dict() if validation_log else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file validation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve file validation: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the document processing service.
    """
    
    try:
        # Check file storage service
        storage_stats = await file_storage_service.get_storage_stats()
        
        # Check agents (would be more comprehensive in production)
        orchestrator = get_pipeline_orchestrator()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "file_storage": storage_stats,
                "document_ai_agent": "available",
                "memo_generator_agent": "available",
                "pipeline_orchestrator": "available"
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )