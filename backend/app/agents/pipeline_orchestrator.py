"""
Pipeline Orchestrator for AIAlchemy

Coordinates the multi-agent workflow for document processing and memo generation.
Manages async task execution, status tracking, and error recovery.
"""

import asyncio
import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable
import logging

from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentConfig, ProcessingResult
from .document_ai_agent import DocumentAIAgent, DocumentAIConfig, DocumentContent
from .memo_generator_agent import MemoGeneratorAgent, MemoGeneratorConfig, InvestmentMemo, MemoSection


class PipelineStage(str, Enum):
    """Pipeline processing stages"""
    INITIALIZATION = "initialization"
    DOCUMENT_VALIDATION = "document_validation"
    DOCUMENT_PROCESSING = "document_processing"
    DATA_EXTRACTION = "data_extraction"
    MEMO_GENERATION = "memo_generation"
    QUALITY_ASSURANCE = "quality_assurance"
    FINALIZATION = "finalization"
    COMPLETED = "completed"
    FAILED = "failed"


class PipelineStatus(str, Enum):
    """Overall pipeline status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StageResult(BaseModel):
    """Result of a pipeline stage"""
    stage: PipelineStage
    status: str  # success, failed, skipped
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class PipelineProgress(BaseModel):
    """Pipeline execution progress"""
    pipeline_id: str
    status: PipelineStatus
    current_stage: PipelineStage
    stages_completed: List[PipelineStage] = Field(default_factory=list)
    stages_failed: List[PipelineStage] = Field(default_factory=list)
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration_ms: Optional[int] = None
    progress_percentage: float = 0.0
    
    # Stage results
    stage_results: Dict[str, StageResult] = Field(default_factory=dict)
    
    # Final outputs
    document_content: Optional[DocumentContent] = None
    investment_memo: Optional[InvestmentMemo] = None
    
    # Metadata
    input_files: List[str] = Field(default_factory=list)
    processing_config: Dict[str, Any] = Field(default_factory=dict)
    
    def calculate_progress(self):
        """Calculate progress percentage based on completed stages"""
        total_stages = len(PipelineStage) - 2  # Exclude COMPLETED and FAILED
        completed_count = len(self.stages_completed)
        self.progress_percentage = min((completed_count / total_stages) * 100, 100.0)


class PipelineConfig(BaseModel):
    """Configuration for pipeline orchestration"""
    pipeline_id: Optional[str] = None
    document_ai_config: DocumentAIConfig
    memo_generator_config: MemoGeneratorConfig
    
    # Processing options
    enable_parallel_processing: bool = True
    max_concurrent_stages: int = 3
    auto_retry_failed_stages: bool = True
    max_stage_retries: int = 2
    stage_timeout_minutes: int = 10
    
    # Memo generation options
    memo_sections: Optional[List[MemoSection]] = None
    memo_template: str = "comprehensive"
    custom_instructions: Optional[str] = None
    
    # Quality assurance
    enable_quality_checks: bool = True
    min_confidence_score: float = 0.7
    require_manual_review: bool = False
    
    # Callbacks and hooks
    stage_completion_callback: Optional[str] = None  # URL or function name
    progress_update_callback: Optional[str] = None


class PipelineOrchestrator:
    """
    Orchestrates the complete document processing and memo generation pipeline.
    
    Features:
    - Multi-stage async processing workflow
    - Real-time progress tracking and status updates
    - Error handling and automatic retry mechanisms
    - Quality assurance and validation checks
    - Customizable processing configurations
    - Event callbacks and monitoring hooks
    """
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = logging.getLogger("aialchemy.pipeline_orchestrator")
        
        # Initialize agents
        self.document_agent = DocumentAIAgent(config.document_ai_config)
        self.memo_agent = MemoGeneratorAgent(config.memo_generator_config)
        
        # Active pipelines tracking
        self.active_pipelines: Dict[str, PipelineProgress] = {}
        
        # Stage definitions with dependencies
        self.stage_dependencies = {
            PipelineStage.INITIALIZATION: [],
            PipelineStage.DOCUMENT_VALIDATION: [PipelineStage.INITIALIZATION],
            PipelineStage.DOCUMENT_PROCESSING: [PipelineStage.DOCUMENT_VALIDATION],
            PipelineStage.DATA_EXTRACTION: [PipelineStage.DOCUMENT_PROCESSING],
            PipelineStage.MEMO_GENERATION: [PipelineStage.DATA_EXTRACTION],
            PipelineStage.QUALITY_ASSURANCE: [PipelineStage.MEMO_GENERATION],
            PipelineStage.FINALIZATION: [PipelineStage.QUALITY_ASSURANCE],
        }
    
    async def start_pipeline(
        self,
        file_data: Union[str, bytes, List[Union[str, bytes]]],
        filenames: Optional[List[str]] = None,
        pipeline_id: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> PipelineProgress:
        """
        Start a new document processing pipeline.
        
        Args:
            file_data: Input file(s) - paths, bytes, or file objects
            filenames: Original filenames for metadata
            pipeline_id: Custom pipeline ID (auto-generated if not provided)
            custom_config: Override default configuration
            
        Returns:
            PipelineProgress object for tracking
        """
        
        # Generate pipeline ID
        if not pipeline_id:
            pipeline_id = f"pipeline_{uuid.uuid4().hex[:8]}"
        
        # Prepare input files list
        if not isinstance(file_data, list):
            file_data = [file_data]
        
        if filenames and not isinstance(filenames, list):
            filenames = [filenames]
        
        # Initialize pipeline progress
        progress = PipelineProgress(
            pipeline_id=pipeline_id,
            status=PipelineStatus.PENDING,
            current_stage=PipelineStage.INITIALIZATION,
            start_time=datetime.now(),
            input_files=filenames or [f"file_{i}" for i in range(len(file_data))],
            processing_config=custom_config or {}
        )
        
        # Store in active pipelines
        self.active_pipelines[pipeline_id] = progress
        
        self.logger.info(f"Starting pipeline {pipeline_id} with {len(file_data)} files")
        
        # Start async processing
        asyncio.create_task(self._execute_pipeline(pipeline_id, file_data, filenames))
        
        return progress
    
    async def _execute_pipeline(
        self,
        pipeline_id: str,
        file_data: List[Union[str, bytes]],
        filenames: Optional[List[str]] = None
    ):
        """Execute the complete pipeline workflow"""
        
        progress = self.active_pipelines[pipeline_id]
        progress.status = PipelineStatus.RUNNING
        
        try:
            # Stage 1: Initialization
            await self._execute_stage(
                pipeline_id,
                PipelineStage.INITIALIZATION,
                self._stage_initialization,
                {"file_data": file_data, "filenames": filenames}
            )
            
            # Stage 2: Document Validation
            await self._execute_stage(
                pipeline_id,
                PipelineStage.DOCUMENT_VALIDATION,
                self._stage_document_validation,
                {"file_data": file_data, "filenames": filenames}
            )
            
            # Stage 3: Document Processing
            await self._execute_stage(
                pipeline_id,
                PipelineStage.DOCUMENT_PROCESSING,
                self._stage_document_processing,
                {"file_data": file_data[0], "filename": filenames[0] if filenames else None}  # Process first file
            )
            
            # Stage 4: Data Extraction (included in document processing)
            await self._execute_stage(
                pipeline_id,
                PipelineStage.DATA_EXTRACTION,
                self._stage_data_extraction,
                {}
            )
            
            # Stage 5: Memo Generation
            await self._execute_stage(
                pipeline_id,
                PipelineStage.MEMO_GENERATION,
                self._stage_memo_generation,
                {}
            )
            
            # Stage 6: Quality Assurance
            await self._execute_stage(
                pipeline_id,
                PipelineStage.QUALITY_ASSURANCE,
                self._stage_quality_assurance,
                {}
            )
            
            # Stage 7: Finalization
            await self._execute_stage(
                pipeline_id,
                PipelineStage.FINALIZATION,
                self._stage_finalization,
                {}
            )
            
            # Pipeline completed successfully
            progress.status = PipelineStatus.COMPLETED
            progress.current_stage = PipelineStage.COMPLETED
            progress.end_time = datetime.now()
            progress.total_duration_ms = int(
                (progress.end_time - progress.start_time).total_seconds() * 1000
            )
            progress.calculate_progress()
            
            self.logger.info(f"Pipeline {pipeline_id} completed successfully")
            
        except Exception as e:
            # Pipeline failed
            progress.status = PipelineStatus.FAILED
            progress.current_stage = PipelineStage.FAILED
            progress.end_time = datetime.now()
            progress.total_duration_ms = int(
                (progress.end_time - progress.start_time).total_seconds() * 1000
            )
            
            self.logger.error(f"Pipeline {pipeline_id} failed: {e}")
            
            # Add error to current stage result
            if progress.current_stage in progress.stage_results:
                progress.stage_results[progress.current_stage.value].errors.append(str(e))
        
        # Trigger completion callback if configured
        await self._trigger_completion_callback(pipeline_id, progress)
    
    async def _execute_stage(
        self,
        pipeline_id: str,
        stage: PipelineStage,
        stage_function: Callable,
        stage_args: Dict[str, Any]
    ):
        """Execute a single pipeline stage with error handling"""
        
        progress = self.active_pipelines[pipeline_id]
        progress.current_stage = stage
        
        # Check dependencies
        for dep_stage in self.stage_dependencies.get(stage, []):
            if dep_stage not in progress.stages_completed:
                raise RuntimeError(f"Stage {stage} dependency {dep_stage} not completed")
        
        # Create stage result
        stage_result = StageResult(
            stage=stage,
            status="running",
            start_time=datetime.now()
        )
        
        progress.stage_results[stage.value] = stage_result
        
        self.logger.info(f"Pipeline {pipeline_id}: Starting stage {stage}")
        
        try:
            # Execute stage with timeout
            result_data = await asyncio.wait_for(
                stage_function(pipeline_id, **stage_args),
                timeout=self.config.stage_timeout_minutes * 60
            )
            
            # Stage completed successfully
            stage_result.status = "success"
            stage_result.end_time = datetime.now()
            stage_result.duration_ms = int(
                (stage_result.end_time - stage_result.start_time).total_seconds() * 1000
            )
            stage_result.data = result_data or {}
            
            progress.stages_completed.append(stage)
            progress.calculate_progress()
            
            self.logger.info(f"Pipeline {pipeline_id}: Completed stage {stage}")
            
            # Trigger progress callback
            await self._trigger_progress_callback(pipeline_id, progress)
            
        except Exception as e:
            # Stage failed
            stage_result.status = "failed"
            stage_result.end_time = datetime.now()
            stage_result.duration_ms = int(
                (stage_result.end_time - stage_result.start_time).total_seconds() * 1000
            )
            stage_result.errors.append(str(e))
            
            progress.stages_failed.append(stage)
            
            self.logger.error(f"Pipeline {pipeline_id}: Stage {stage} failed: {e}")
            
            # Retry logic
            if (self.config.auto_retry_failed_stages and 
                len([r for r in progress.stage_results.values() if r.stage == stage and r.status == "failed"]) <= self.config.max_stage_retries):
                
                self.logger.info(f"Pipeline {pipeline_id}: Retrying stage {stage}")
                await self._execute_stage(pipeline_id, stage, stage_function, stage_args)
            else:
                raise e
    
    # Stage implementation methods
    
    async def _stage_initialization(self, pipeline_id: str, **kwargs) -> Dict[str, Any]:
        """Initialize pipeline and validate configuration"""
        
        file_data = kwargs.get('file_data', [])
        filenames = kwargs.get('filenames', [])
        
        # Validate inputs
        if not file_data:
            raise ValueError("No input files provided")
        
        # Validate agent configurations
        if not await self.document_agent.health_check():
            raise RuntimeError("Document AI agent not healthy")
        
        if not await self.memo_agent.health_check():
            raise RuntimeError("Memo Generator agent not healthy")
        
        return {
            "input_file_count": len(file_data),
            "filenames": filenames,
            "agents_initialized": True
        }
    
    async def _stage_document_validation(self, pipeline_id: str, **kwargs) -> Dict[str, Any]:
        """Validate document format and accessibility"""
        
        file_data = kwargs.get('file_data', [])
        validation_results = []
        
        for i, file in enumerate(file_data):
            try:
                validation = await self.document_agent.validate_document(file)
                validation_results.append(validation)
                
                if not validation.get('valid', False):
                    raise ValueError(f"File {i} validation failed: {validation.get('error', 'Unknown error')}")
                
                if not validation.get('supported', False):
                    raise ValueError(f"File {i} format not supported")
                
            except Exception as e:
                raise ValueError(f"Validation failed for file {i}: {str(e)}")
        
        return {
            "validation_results": validation_results,
            "all_files_valid": True
        }
    
    async def _stage_document_processing(self, pipeline_id: str, **kwargs) -> Dict[str, Any]:
        """Process document with Document AI agent"""
        
        file_data = kwargs.get('file_data')
        filename = kwargs.get('filename')
        
        if not file_data:
            raise ValueError("No file data provided for processing")
        
        # Process document
        processing_result = await self.document_agent.process_with_retry(
            file_data,
            f"{pipeline_id}_doc_processing",
            filename=filename
        )
        
        if processing_result.status != "success":
            raise RuntimeError(f"Document processing failed: {processing_result.errors}")
        
        # Store document content in pipeline progress
        progress = self.active_pipelines[pipeline_id]
        progress.document_content = DocumentContent(**processing_result.data["document_content"])
        
        return {
            "processing_result": processing_result.dict(),
            "extraction_confidence": progress.document_content.extraction_confidence
        }
    
    async def _stage_data_extraction(self, pipeline_id: str, **kwargs) -> Dict[str, Any]:
        """Extract and validate structured data"""
        
        progress = self.active_pipelines[pipeline_id]
        
        if not progress.document_content:
            raise RuntimeError("No document content available for data extraction")
        
        document_content = progress.document_content
        
        # Validate extraction quality
        if document_content.extraction_confidence < self.config.min_confidence_score:
            progress.stage_results[PipelineStage.DATA_EXTRACTION.value].warnings.append(
                f"Low extraction confidence: {document_content.extraction_confidence:.2f}"
            )
        
        # Extract key data points
        extraction_summary = {
            "company_name": document_content.business_data.company_name,
            "industry": document_content.business_data.industry,
            "founders_count": len(document_content.team_data.founders),
            "has_financial_data": bool(document_content.financial_data.revenue_current or document_content.financial_data.funding_amount),
            "text_length": len(document_content.raw_text),
            "confidence_score": document_content.extraction_confidence
        }
        
        return {
            "extraction_summary": extraction_summary,
            "data_quality_check": "passed"
        }
    
    async def _stage_memo_generation(self, pipeline_id: str, **kwargs) -> Dict[str, Any]:
        """Generate investment memo using Gemini Pro agent"""
        
        progress = self.active_pipelines[pipeline_id]
        
        if not progress.document_content:
            raise RuntimeError("No document content available for memo generation")
        
        # Determine memo sections to generate
        memo_sections = self.config.memo_sections
        if not memo_sections:
            # Use template-based sections
            templates = await self.memo_agent.get_memo_templates()
            memo_sections = templates.get(self.config.memo_template, list(MemoSection))
        
        # Generate memo
        memo_result = await self.memo_agent.process_with_retry(
            progress.document_content,
            f"{pipeline_id}_memo_generation",
            memo_sections=memo_sections,
            custom_instructions=self.config.custom_instructions
        )
        
        if memo_result.status != "success":
            raise RuntimeError(f"Memo generation failed: {memo_result.errors}")
        
        # Store memo in pipeline progress
        progress.investment_memo = InvestmentMemo(**memo_result.data["investment_memo"])
        
        return {
            "memo_result": memo_result.dict(),
            "memo_sections_generated": len(memo_sections),
            "total_words": progress.investment_memo.get_total_words(),
            "overall_score": progress.investment_memo.overall_score
        }
    
    async def _stage_quality_assurance(self, pipeline_id: str, **kwargs) -> Dict[str, Any]:
        """Perform quality assurance checks"""
        
        progress = self.active_pipelines[pipeline_id]
        qa_results = {
            "checks_passed": 0,
            "checks_failed": 0,
            "issues": [],
            "recommendations": []
        }
        
        # Check memo completeness
        if progress.investment_memo:
            memo = progress.investment_memo
            
            # Check word count
            word_count = memo.get_total_words()
            if word_count < 500:
                qa_results["issues"].append("Memo is too short (< 500 words)")
                qa_results["checks_failed"] += 1
            else:
                qa_results["checks_passed"] += 1
            
            # Check key sections
            required_sections = [memo.executive_summary, memo.investment_thesis, memo.recommendation]
            if not all(section.strip() for section in required_sections):
                qa_results["issues"].append("Missing critical memo sections")
                qa_results["checks_failed"] += 1
            else:
                qa_results["checks_passed"] += 1
            
            # Check scoring
            if memo.overall_score < 10 or memo.overall_score > 90:
                qa_results["recommendations"].append("Review scoring - may be too extreme")
            
        # Check document confidence
        if progress.document_content:
            if progress.document_content.extraction_confidence < self.config.min_confidence_score:
                qa_results["issues"].append(
                    f"Low document extraction confidence: {progress.document_content.extraction_confidence:.2f}"
                )
                qa_results["checks_failed"] += 1
            else:
                qa_results["checks_passed"] += 1
        
        # Determine if manual review is required
        requires_manual_review = (
            self.config.require_manual_review or
            qa_results["checks_failed"] > 0 or
            (progress.investment_memo and progress.investment_memo.overall_score > 80)  # High-score investments
        )
        
        qa_results["requires_manual_review"] = requires_manual_review
        
        return qa_results
    
    async def _stage_finalization(self, pipeline_id: str, **kwargs) -> Dict[str, Any]:
        """Finalize pipeline and prepare outputs"""
        
        progress = self.active_pipelines[pipeline_id]
        
        # Prepare final output package
        final_output = {
            "pipeline_id": pipeline_id,
            "processing_summary": {
                "total_duration_ms": progress.total_duration_ms,
                "stages_completed": len(progress.stages_completed),
                "stages_failed": len(progress.stages_failed),
                "success_rate": len(progress.stages_completed) / len(self.stage_dependencies)
            }
        }
        
        # Include document content if available
        if progress.document_content:
            final_output["document_summary"] = {
                "company_name": progress.document_content.business_data.company_name,
                "extraction_confidence": progress.document_content.extraction_confidence,
                "text_length": len(progress.document_content.raw_text)
            }
        
        # Include memo summary if available
        if progress.investment_memo:
            final_output["memo_summary"] = {
                "overall_score": progress.investment_memo.overall_score,
                "recommendation": progress.investment_memo.recommendation_type.value,
                "risk_level": progress.investment_memo.risk_level.value,
                "word_count": progress.investment_memo.get_total_words(),
                "success_probability": progress.investment_memo.success_probability
            }
        
        return final_output
    
    # Utility methods
    
    async def get_pipeline_status(self, pipeline_id: str) -> Optional[PipelineProgress]:
        """Get current status of a pipeline"""
        return self.active_pipelines.get(pipeline_id)
    
    async def cancel_pipeline(self, pipeline_id: str) -> bool:
        """Cancel a running pipeline"""
        if pipeline_id in self.active_pipelines:
            progress = self.active_pipelines[pipeline_id]
            if progress.status == PipelineStatus.RUNNING:
                progress.status = PipelineStatus.CANCELLED
                progress.end_time = datetime.now()
                return True
        return False
    
    async def retry_failed_stage(self, pipeline_id: str, stage: PipelineStage) -> bool:
        """Retry a specific failed stage"""
        if pipeline_id not in self.active_pipelines:
            return False
        
        progress = self.active_pipelines[pipeline_id]
        
        if stage in progress.stages_failed:
            # Remove from failed stages and retry
            progress.stages_failed.remove(stage)
            
            # Stage functions mapping
            stage_functions = {
                PipelineStage.DOCUMENT_VALIDATION: self._stage_document_validation,
                PipelineStage.DOCUMENT_PROCESSING: self._stage_document_processing,
                PipelineStage.DATA_EXTRACTION: self._stage_data_extraction,
                PipelineStage.MEMO_GENERATION: self._stage_memo_generation,
                PipelineStage.QUALITY_ASSURANCE: self._stage_quality_assurance,
                PipelineStage.FINALIZATION: self._stage_finalization,
            }
            
            stage_function = stage_functions.get(stage)
            if stage_function:
                try:
                    await self._execute_stage(pipeline_id, stage, stage_function, {})
                    return True
                except Exception as e:
                    self.logger.error(f"Retry failed for stage {stage}: {e}")
            
        return False
    
    async def _trigger_progress_callback(self, pipeline_id: str, progress: PipelineProgress):
        """Trigger progress update callback if configured"""
        if self.config.progress_update_callback:
            try:
                # Placeholder for webhook/callback implementation
                self.logger.info(f"Progress callback triggered for {pipeline_id}: {progress.progress_percentage:.1f}%")
            except Exception as e:
                self.logger.error(f"Progress callback failed: {e}")
    
    async def _trigger_completion_callback(self, pipeline_id: str, progress: PipelineProgress):
        """Trigger completion callback if configured"""
        if self.config.stage_completion_callback:
            try:
                # Placeholder for webhook/callback implementation
                self.logger.info(f"Completion callback triggered for {pipeline_id}: {progress.status}")
            except Exception as e:
                self.logger.error(f"Completion callback failed: {e}")
    
    def get_active_pipelines(self) -> Dict[str, PipelineProgress]:
        """Get all active pipelines"""
        return self.active_pipelines.copy()
    
    def cleanup_completed_pipelines(self, max_age_hours: int = 24):
        """Clean up old completed pipelines"""
        current_time = datetime.now()
        to_remove = []
        
        for pipeline_id, progress in self.active_pipelines.items():
            if progress.status in [PipelineStatus.COMPLETED, PipelineStatus.FAILED, PipelineStatus.CANCELLED]:
                if progress.end_time:
                    age_hours = (current_time - progress.end_time).total_seconds() / 3600
                    if age_hours > max_age_hours:
                        to_remove.append(pipeline_id)
        
        for pipeline_id in to_remove:
            del self.active_pipelines[pipeline_id]
            self.logger.info(f"Cleaned up old pipeline: {pipeline_id}")
        
        return len(to_remove)