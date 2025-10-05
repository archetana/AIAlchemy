"""
Base Agent Class for AIAlchemy Multi-Agent System

Provides common functionality and interface for all AI agents.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
from pathlib import Path

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration model for agents"""
    name: str
    version: str = "1.0.0"
    timeout: int = 300  # 5 minutes default
    retry_attempts: int = 3
    retry_delay: float = 1.0
    enable_logging: bool = True
    log_level: str = "INFO"


class ProcessingResult(BaseModel):
    """Standard result format for agent processing"""
    agent_name: str
    processing_id: str
    status: str  # success, failed, partial
    timestamp: datetime
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    processing_time_ms: Optional[int] = None


class BaseAgent(ABC):
    """
    Abstract base class for all AIAlchemy agents.
    
    Provides common functionality including:
    - Logging and monitoring
    - Error handling and retries
    - Result standardization
    - Configuration management
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = self._setup_logger()
        self._processing_count = 0
        self._error_count = 0
        
    def _setup_logger(self) -> logging.Logger:
        """Set up structured logging for the agent"""
        logger = logging.getLogger(f"aialchemy.agents.{self.config.name}")
        logger.setLevel(getattr(logging, self.config.log_level))
        
        if not logger.handlers and self.config.enable_logging:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def process_with_retry(
        self, 
        data: Any, 
        processing_id: str,
        **kwargs
    ) -> ProcessingResult:
        """
        Process data with automatic retry logic and standardized result format.
        
        Args:
            data: Input data to process
            processing_id: Unique identifier for this processing request
            **kwargs: Additional arguments passed to the process method
            
        Returns:
            ProcessingResult with standardized format
        """
        start_time = datetime.now()
        processing_start_ms = int(start_time.timestamp() * 1000)
        
        last_error = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                self.logger.info(
                    f"Processing attempt {attempt + 1}/{self.config.retry_attempts} "
                    f"for {processing_id}"
                )
                
                # Execute the actual processing
                result_data = await asyncio.wait_for(
                    self.process(data, processing_id, **kwargs),
                    timeout=self.config.timeout
                )
                
                # Calculate processing time
                end_time = datetime.now()
                processing_time_ms = int((end_time.timestamp() - start_time.timestamp()) * 1000)
                
                # Create successful result
                result = ProcessingResult(
                    agent_name=self.config.name,
                    processing_id=processing_id,
                    status="success",
                    timestamp=end_time,
                    data=result_data if isinstance(result_data, dict) else {"result": result_data},
                    metadata={
                        "attempt": attempt + 1,
                        "processing_start": start_time.isoformat(),
                        "processing_end": end_time.isoformat(),
                    },
                    processing_time_ms=processing_time_ms
                )
                
                self._processing_count += 1
                self.logger.info(f"Successfully processed {processing_id}")
                return result
                
            except asyncio.TimeoutError:
                last_error = f"Processing timeout after {self.config.timeout} seconds"
                self.logger.warning(f"Timeout on attempt {attempt + 1}: {last_error}")
                
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Error on attempt {attempt + 1}: {last_error}")
                
            # Wait before retry (except on last attempt)
            if attempt < self.config.retry_attempts - 1:
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff
        
        # All attempts failed
        self._error_count += 1
        end_time = datetime.now()
        processing_time_ms = int((end_time.timestamp() - start_time.timestamp()) * 1000)
        
        return ProcessingResult(
            agent_name=self.config.name,
            processing_id=processing_id,
            status="failed",
            timestamp=end_time,
            data={},
            metadata={
                "attempts": self.config.retry_attempts,
                "processing_start": start_time.isoformat(),
                "processing_end": end_time.isoformat(),
            },
            errors=[f"Failed after {self.config.retry_attempts} attempts: {last_error}"],
            processing_time_ms=processing_time_ms
        )
    
    @abstractmethod
    async def process(self, data: Any, processing_id: str, **kwargs) -> Dict[str, Any]:
        """
        Abstract method for processing data. Must be implemented by subclasses.
        
        Args:
            data: Input data to process
            processing_id: Unique identifier for this processing request
            **kwargs: Additional processing parameters
            
        Returns:
            Dictionary containing processed results
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the agent.
        
        Returns:
            Dictionary with health status and metrics
        """
        return {
            "agent_name": self.config.name,
            "version": self.config.version,
            "status": "healthy",
            "processing_count": self._processing_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._processing_count, 1),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return {
            "processing_count": self._processing_count,
            "error_count": self._error_count,
            "success_rate": (self._processing_count - self._error_count) / max(self._processing_count, 1),
            "agent_config": self.config.dict()
        }