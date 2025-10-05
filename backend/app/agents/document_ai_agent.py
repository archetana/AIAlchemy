"""
Document AI Agent for AIAlchemy

Processes various document formats (PDF, PPT, DOCX) using Google Document AI
and extracts structured data for startup evaluation.
"""

import asyncio
import io
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, BinaryIO
from datetime import datetime
import mimetypes

try:
    from google.cloud import documentai
    from google.oauth2 import service_account
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    documentai = None

import aiofiles
from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentConfig, ProcessingResult


class DocumentMetadata(BaseModel):
    """Metadata for processed documents"""
    filename: str
    file_size: int
    mime_type: str
    page_count: Optional[int] = None
    language: Optional[str] = None
    processing_method: str
    confidence_score: Optional[float] = None


class FinancialData(BaseModel):
    """Extracted financial information"""
    revenue_current: Optional[float] = None
    revenue_projected: Optional[float] = None
    funding_amount: Optional[float] = None
    funding_stage: Optional[str] = None
    burn_rate: Optional[float] = None
    runway_months: Optional[int] = None
    valuation: Optional[float] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)


class TeamData(BaseModel):
    """Extracted team information"""
    founders: List[str] = Field(default_factory=list)
    team_size: Optional[int] = None
    key_roles: List[str] = Field(default_factory=list)
    advisors: List[str] = Field(default_factory=list)
    experience: Dict[str, str] = Field(default_factory=dict)


class BusinessData(BaseModel):
    """Extracted business information"""
    company_name: Optional[str] = None
    industry: Optional[str] = None
    business_model: Optional[str] = None
    target_market: Optional[str] = None
    market_size: Optional[str] = None
    competitive_advantage: Optional[str] = None
    problem_statement: Optional[str] = None
    solution_description: Optional[str] = None


class DocumentContent(BaseModel):
    """Structured document content"""
    raw_text: str
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    financial_data: FinancialData = Field(default_factory=FinancialData)
    team_data: TeamData = Field(default_factory=TeamData)
    business_data: BusinessData = Field(default_factory=BusinessData)
    metadata: DocumentMetadata
    extraction_confidence: float = 0.0


class DocumentAIConfig(AgentConfig):
    """Configuration for Document AI Agent"""
    name: str = "document_ai_agent"
    project_id: Optional[str] = None
    location: str = "us"  # Document AI location
    processor_id: Optional[str] = None
    processor_version: Optional[str] = None
    credentials_path: Optional[str] = None
    max_file_size_mb: int = 50
    supported_formats: List[str] = Field(default_factory=lambda: [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'image/png',
        'image/jpeg',
        'image/tiff'
    ])


class DocumentAIAgent(BaseAgent):
    """
    Document AI Agent for processing startup documents.
    
    Features:
    - Multi-format document processing (PDF, PPT, DOCX, images)
    - Structured data extraction for startup-specific content
    - Financial data parsing and validation
    - Team information extraction
    - Business model analysis
    """
    
    def __init__(self, config: DocumentAIConfig):
        super().__init__(config)
        self.config: DocumentAIConfig = config
        self.client = None
        self.processor_name = None
        
        if GOOGLE_AI_AVAILABLE:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Document AI client"""
        try:
            if self.config.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.config.credentials_path
                )
                self.client = documentai.DocumentProcessorServiceClient(
                    credentials=credentials
                )
            else:
                # Use default credentials (environment variable or metadata service)
                self.client = documentai.DocumentProcessorServiceClient()
            
            if self.config.project_id and self.config.processor_id:
                self.processor_name = self.client.processor_path(
                    self.config.project_id,
                    self.config.location,
                    self.config.processor_id
                )
                
            self.logger.info("Document AI client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Document AI client: {e}")
            self.client = None
    
    async def process(
        self, 
        file_data: Union[str, BinaryIO, bytes], 
        processing_id: str,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process document and extract structured content.
        
        Args:
            file_data: File path, file object, or raw bytes
            processing_id: Unique processing identifier
            filename: Original filename (for metadata)
            mime_type: MIME type of the file
            **kwargs: Additional processing parameters
            
        Returns:
            Dictionary containing extracted document content
        """
        
        # Prepare file content
        content, file_metadata = await self._prepare_file_content(
            file_data, filename, mime_type
        )
        
        # Validate file format
        if file_metadata.mime_type not in self.config.supported_formats:
            raise ValueError(f"Unsupported file format: {file_metadata.mime_type}")
        
        # Validate file size
        if file_metadata.file_size > self.config.max_file_size_mb * 1024 * 1024:
            raise ValueError(f"File too large: {file_metadata.file_size} bytes")
        
        # Process document
        if self.client and self.processor_name:
            document_content = await self._process_with_document_ai(
                content, file_metadata, processing_id
            )
        else:
            # Fallback to basic text extraction
            self.logger.warning(
                "Document AI not available, using fallback text extraction"
            )
            document_content = await self._process_with_fallback(
                content, file_metadata, processing_id
            )
        
        return {
            "document_content": document_content.dict(),
            "processing_id": processing_id,
            "extraction_method": "document_ai" if self.client else "fallback"
        }
    
    async def _prepare_file_content(
        self,
        file_data: Union[str, BinaryIO, bytes],
        filename: Optional[str],
        mime_type: Optional[str]
    ) -> tuple[bytes, DocumentMetadata]:
        """Prepare file content and metadata"""
        
        if isinstance(file_data, str):
            # File path
            file_path = Path(file_data)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_data}")
            
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
            
            filename = filename or file_path.name
            mime_type = mime_type or mimetypes.guess_type(str(file_path))[0]
            file_size = file_path.stat().st_size
            
        elif isinstance(file_data, bytes):
            # Raw bytes
            content = file_data
            filename = filename or "document"
            file_size = len(content)
            
        else:
            # File object
            content = file_data.read()
            if hasattr(file_data, 'name'):
                filename = filename or Path(file_data.name).name
            else:
                filename = filename or "document"
            file_size = len(content)
        
        # Determine MIME type if not provided
        if not mime_type and filename:
            mime_type = mimetypes.guess_type(filename)[0]
        
        mime_type = mime_type or 'application/octet-stream'
        
        metadata = DocumentMetadata(
            filename=filename,
            file_size=file_size,
            mime_type=mime_type,
            processing_method="document_ai" if self.client else "fallback"
        )
        
        return content, metadata
    
    async def _process_with_document_ai(
        self,
        content: bytes,
        metadata: DocumentMetadata,
        processing_id: str
    ) -> DocumentContent:
        """Process document using Google Document AI"""
        
        try:
            # Create the request
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=documentai.RawDocument(
                    content=content,
                    mime_type=metadata.mime_type
                )
            )
            
            # Process the document
            result = self.client.process_document(request=request)
            document = result.document
            
            # Extract raw text
            raw_text = document.text
            
            # Extract structured data
            structured_data = await self._extract_structured_data(document)
            
            # Extract startup-specific data
            financial_data = self._extract_financial_data(document, raw_text)
            team_data = self._extract_team_data(document, raw_text)
            business_data = self._extract_business_data(document, raw_text)
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(document)
            
            # Update metadata
            metadata.page_count = len(document.pages)
            metadata.confidence_score = confidence
            
            return DocumentContent(
                raw_text=raw_text,
                structured_data=structured_data,
                financial_data=financial_data,
                team_data=team_data,
                business_data=business_data,
                metadata=metadata,
                extraction_confidence=confidence
            )
            
        except Exception as e:
            self.logger.error(f"Document AI processing failed: {e}")
            # Fallback to basic processing
            return await self._process_with_fallback(content, metadata, processing_id)
    
    async def _process_with_fallback(
        self,
        content: bytes,
        metadata: DocumentMetadata,
        processing_id: str
    ) -> DocumentContent:
        """Fallback processing without Document AI"""
        
        # Basic text extraction (placeholder - would implement PDF/DOCX parsers)
        raw_text = f"[Fallback processing for {metadata.filename}]\n"
        raw_text += f"File size: {metadata.file_size} bytes\n"
        raw_text += f"MIME type: {metadata.mime_type}\n"
        raw_text += "Content extraction requires Document AI integration."
        
        return DocumentContent(
            raw_text=raw_text,
            structured_data={"fallback": True},
            financial_data=FinancialData(),
            team_data=TeamData(),
            business_data=BusinessData(),
            metadata=metadata,
            extraction_confidence=0.1
        )
    
    async def _extract_structured_data(self, document) -> Dict[str, Any]:
        """Extract structured data from Document AI result"""
        structured = {
            "pages": len(document.pages),
            "entities": [],
            "tables": [],
            "form_fields": []
        }
        
        # Extract entities
        for entity in document.entities:
            structured["entities"].append({
                "type": entity.type_,
                "text": entity.text_anchor.content if entity.text_anchor else "",
                "confidence": entity.confidence
            })
        
        # Extract tables
        for page in document.pages:
            for table in page.tables:
                table_data = {
                    "rows": len(table.body_rows),
                    "columns": len(table.header_rows[0].cells) if table.header_rows else 0,
                    "content": []
                }
                
                # Extract table content (simplified)
                for row in table.body_rows:
                    row_data = []
                    for cell in row.cells:
                        cell_text = ""
                        for segment in cell.layout.text_anchor.text_segments:
                            cell_text += document.text[segment.start_index:segment.end_index]
                        row_data.append(cell_text.strip())
                    table_data["content"].append(row_data)
                
                structured["tables"].append(table_data)
        
        return structured
    
    def _extract_financial_data(self, document, raw_text: str) -> FinancialData:
        """Extract financial data from document"""
        financial = FinancialData()
        
        # Use regex patterns to find financial information
        import re
        
        # Revenue patterns
        revenue_patterns = [
            r'revenue[:\s]+\$?([0-9,]+(?:\.[0-9]{2})?)[kmb]?',
            r'sales[:\s]+\$?([0-9,]+(?:\.[0-9]{2})?)[kmb]?',
            r'\$([0-9,]+(?:\.[0-9]{2})?)[kmb]?\s+revenue'
        ]
        
        for pattern in revenue_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1).replace(',', ''))
                    # Convert k, m, b to actual numbers
                    if 'k' in match.group(0).lower():
                        amount *= 1000
                    elif 'm' in match.group(0).lower():
                        amount *= 1000000
                    elif 'b' in match.group(0).lower():
                        amount *= 1000000000
                    financial.revenue_current = amount
                    break
                except ValueError:
                    continue
        
        # Funding patterns
        funding_patterns = [
            r'seeking[:\s]+\$?([0-9,]+(?:\.[0-9]{2})?)[kmb]?',
            r'funding[:\s]+\$?([0-9,]+(?:\.[0-9]{2})?)[kmb]?',
            r'raise[:\s]+\$?([0-9,]+(?:\.[0-9]{2})?)[kmb]?'
        ]
        
        for pattern in funding_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1).replace(',', ''))
                    if 'k' in match.group(0).lower():
                        amount *= 1000
                    elif 'm' in match.group(0).lower():
                        amount *= 1000000
                    elif 'b' in match.group(0).lower():
                        amount *= 1000000000
                    financial.funding_amount = amount
                    break
                except ValueError:
                    continue
        
        return financial
    
    def _extract_team_data(self, document, raw_text: str) -> TeamData:
        """Extract team data from document"""
        team = TeamData()
        
        # Extract founder names (simplified pattern matching)
        import re
        
        founder_patterns = [
            r'founder[s]?[:\s]+([A-Za-z\s,]+)',
            r'ceo[:\s]+([A-Za-z\s]+)',
            r'founded by[:\s]+([A-Za-z\s,]+)'
        ]
        
        for pattern in founder_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                founders_text = match.group(1).strip()
                # Split by commas and clean
                founders = [f.strip() for f in founders_text.split(',') if f.strip()]
                team.founders.extend(founders[:3])  # Limit to 3 founders
                break
        
        # Team size pattern
        team_size_pattern = r'team[:\s]+([0-9]+)'
        match = re.search(team_size_pattern, raw_text, re.IGNORECASE)
        if match:
            try:
                team.team_size = int(match.group(1))
            except ValueError:
                pass
        
        return team
    
    def _extract_business_data(self, document, raw_text: str) -> BusinessData:
        """Extract business data from document"""
        business = BusinessData()
        
        # Extract company name (look for title or header patterns)
        lines = raw_text.split('\n')
        if lines:
            # First non-empty line might be company name
            for line in lines[:5]:
                line = line.strip()
                if line and len(line) < 100:  # Reasonable company name length
                    business.company_name = line
                    break
        
        # Industry/sector patterns
        import re
        
        industry_patterns = [
            r'industry[:\s]+([A-Za-z\s&-]+)',
            r'sector[:\s]+([A-Za-z\s&-]+)',
            r'vertical[:\s]+([A-Za-z\s&-]+)'
        ]
        
        for pattern in industry_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                business.industry = match.group(1).strip()
                break
        
        # Problem statement (look for "problem" section)
        problem_match = re.search(
            r'problem[:\s]+(.*?)(?=solution|opportunity|market|$)', 
            raw_text, 
            re.IGNORECASE | re.DOTALL
        )
        if problem_match:
            business.problem_statement = problem_match.group(1).strip()[:500]  # Limit length
        
        # Solution description
        solution_match = re.search(
            r'solution[:\s]+(.*?)(?=problem|market|team|$)', 
            raw_text, 
            re.IGNORECASE | re.DOTALL
        )
        if solution_match:
            business.solution_description = solution_match.group(1).strip()[:500]  # Limit length
        
        return business
    
    def _calculate_confidence_score(self, document) -> float:
        """Calculate overall confidence score for extraction"""
        if not hasattr(document, 'entities') or not document.entities:
            return 0.5  # Base confidence for successful processing
        
        # Average confidence from entities
        entity_confidences = [entity.confidence for entity in document.entities if entity.confidence]
        
        if entity_confidences:
            return sum(entity_confidences) / len(entity_confidences)
        
        return 0.7  # Default confidence for successful Document AI processing
    
    async def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return self.config.supported_formats
    
    async def validate_document(self, file_data: Union[str, BinaryIO, bytes]) -> Dict[str, Any]:
        """
        Validate document without full processing.
        
        Returns validation result with file info and compatibility.
        """
        try:
            content, metadata = await self._prepare_file_content(file_data, None, None)
            
            return {
                "valid": True,
                "metadata": metadata.dict(),
                "supported": metadata.mime_type in self.config.supported_formats,
                "size_ok": metadata.file_size <= self.config.max_file_size_mb * 1024 * 1024
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "supported": False,
                "size_ok": False
            }