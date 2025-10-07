#!/usr/bin/env python3
"""
Document AI Integration Script
Integrates Google Document AI and Landing AI with the vector database
"""

import asyncio
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

# Document AI Service Implementations
class GoogleDocumentAI:
    """Google Document AI integration"""
    
    def __init__(self, project_id: str, processor_id: str, location: str = "us"):
        self.project_id = project_id
        self.processor_id = processor_id
        self.location = location
        
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process document using Google Document AI"""
        try:
            from google.cloud import documentai
            
            # Initialize client
            client = documentai.DocumentProcessorServiceClient()
            
            # Read file
            with open(file_path, "rb") as image:
                image_content = image.read()
            
            # Configure request
            name = client.processor_path(self.project_id, self.location, self.processor_id)
            request = documentai.ProcessRequest(
                name=name,
                raw_document=documentai.RawDocument(
                    content=image_content,
                    mime_type=self._get_mime_type(file_path)
                )
            )
            
            # Process document
            result = client.process_document(request=request)
            document = result.document
            
            # Extract structured data
            extracted_data = self._extract_structured_data(document)
            
            return {
                "service": "google_document_ai",
                "raw_text": document.text,
                "structured_data": extracted_data,
                "confidence": self._calculate_average_confidence(document),
                "page_count": len(document.pages),
                "processing_time_ms": 0  # Would be measured in real implementation
            }
            
        except Exception as e:
            return {
                "service": "google_document_ai",
                "error": str(e),
                "raw_text": "",
                "structured_data": {},
                "confidence": 0
            }
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type based on file extension"""
        ext = Path(file_path).suffix.lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.tiff': 'image/tiff'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def _extract_structured_data(self, document) -> Dict[str, Any]:
        """Extract structured data from Document AI response"""
        structured_data = {}
        
        # Extract entities
        if hasattr(document, 'entities'):
            for entity in document.entities:
                if entity.confidence > 0.5:  # Only high-confidence entities
                    structured_data[entity.type_] = {
                        "value": entity.text_anchor.content if hasattr(entity.text_anchor, 'content') else entity.mention_text,
                        "confidence": entity.confidence
                    }
        
        # Extract form fields
        if hasattr(document, 'pages'):
            for page in document.pages:
                if hasattr(page, 'form_fields'):
                    for field in page.form_fields:
                        if field.field_name and field.field_value:
                            field_name = self._get_text(field.field_name, document.text)
                            field_value = self._get_text(field.field_value, document.text)
                            structured_data[field_name] = field_value
        
        return structured_data
    
    def _get_text(self, layout, full_text: str) -> str:
        """Extract text from layout object"""
        if hasattr(layout, 'text_anchor') and hasattr(layout.text_anchor, 'text_segments'):
            segments = layout.text_anchor.text_segments
            text = ""
            for segment in segments:
                start_index = int(segment.start_index) if hasattr(segment, 'start_index') else 0
                end_index = int(segment.end_index) if hasattr(segment, 'end_index') else len(full_text)
                text += full_text[start_index:end_index]
            return text.strip()
        return ""
    
    def _calculate_average_confidence(self, document) -> float:
        """Calculate average confidence score"""
        confidences = []
        
        if hasattr(document, 'entities'):
            confidences.extend([entity.confidence for entity in document.entities])
        
        if hasattr(document, 'pages'):
            for page in document.pages:
                if hasattr(page, 'form_fields'):
                    for field in page.form_fields:
                        if hasattr(field, 'field_value') and hasattr(field.field_value, 'confidence'):
                            confidences.append(field.field_value.confidence)
        
        return sum(confidences) / len(confidences) * 100 if confidences else 0


class LandingAI:
    """Landing AI Agentic Document Extraction integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.landing.ai/v1/ade"
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process document using Landing AI ADE"""
        try:
            import aiohttp
            import aiofiles
            
            # Read file
            async with aiofiles.open(file_path, 'rb') as f:
                file_content = await f.read()
            
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/octet-stream"
            }
            
            # Step 1: Parse document
            async with aiohttp.ClientSession() as session:
                parse_url = f"{self.base_url}/parse"
                async with session.post(parse_url, headers=headers, data=file_content) as response:
                    if response.status != 200:
                        raise Exception(f"Parse API failed: {await response.text()}")
                    
                    parse_result = await response.json()
            
            # Step 2: Extract structured data
            extraction_schema = self._create_extraction_schema()
            
            async with aiohttp.ClientSession() as session:
                extract_url = f"{self.base_url}/extract"
                extract_payload = {
                    "markdown": parse_result.get("markdown", ""),
                    "extraction_schema": extraction_schema
                }
                
                async with session.post(extract_url, headers={"Authorization": f"Bearer {self.api_key}"}, json=extract_payload) as response:
                    if response.status != 200:
                        raise Exception(f"Extract API failed: {await response.text()}")
                    
                    extract_result = await response.json()
            
            return {
                "service": "landing_ai",
                "raw_text": parse_result.get("markdown", ""),
                "structured_data": extract_result.get("extraction", {}),
                "confidence": extract_result.get("confidence", 0),
                "page_count": parse_result.get("page_count", 1),
                "processing_time_ms": 0  # Would be measured in real implementation
            }
            
        except Exception as e:
            return {
                "service": "landing_ai",
                "error": str(e),
                "raw_text": "",
                "structured_data": {},
                "confidence": 0
            }
    
    def _create_extraction_schema(self) -> Dict[str, Any]:
        """Create extraction schema for startup documents"""
        return {
            "company_info": {
                "company_name": {"type": "string", "description": "Company name"},
                "website": {"type": "string", "description": "Company website URL"},
                "founded_year": {"type": "integer", "description": "Year company was founded"},
                "industry": {"type": "string", "description": "Primary industry or sector"}
            },
            "financial_info": {
                "revenue_current": {"type": "number", "description": "Current annual revenue"},
                "revenue_previous": {"type": "number", "description": "Previous year revenue"},
                "funding_requested": {"type": "number", "description": "Amount of funding requested"},
                "valuation": {"type": "number", "description": "Company valuation"},
                "burn_rate": {"type": "number", "description": "Monthly burn rate"},
                "runway_months": {"type": "integer", "description": "Runway in months"}
            },
            "team_info": {
                "founders": {"type": "array", "description": "List of founders and key team members"},
                "team_size": {"type": "integer", "description": "Total team size"},
                "key_hires": {"type": "array", "description": "Key recent hires or planned hires"}
            },
            "product_info": {
                "product_description": {"type": "string", "description": "Product or service description"},
                "target_market": {"type": "string", "description": "Target market description"},
                "competitive_advantage": {"type": "string", "description": "Key competitive advantages"},
                "technology_stack": {"type": "array", "description": "Technologies used"}
            },
            "traction_metrics": {
                "users_total": {"type": "integer", "description": "Total number of users"},
                "users_monthly_active": {"type": "integer", "description": "Monthly active users"},
                "customer_count": {"type": "integer", "description": "Number of paying customers"},
                "partnerships": {"type": "array", "description": "Key partnerships or clients"}
            }
        }


class DocumentProcessingService:
    """Main service that coordinates document processing and vector storage"""
    
    def __init__(self):
        self.google_ai = None
        self.landing_ai = None
        self._setup_services()
    
    def _setup_services(self):
        """Initialize AI services based on available credentials"""
        # Google Document AI
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        processor_id = os.getenv('DOCUMENT_AI_PROCESSOR_ID')
        if project_id and processor_id:
            self.google_ai = GoogleDocumentAI(project_id, processor_id)
        
        # Landing AI
        landing_ai_key = os.getenv('LANDING_AI_API_KEY')
        if landing_ai_key:
            self.landing_ai = LandingAI(landing_ai_key)
    
    async def process_document_with_best_service(
        self, 
        file_path: str, 
        preferred_service: Optional[str] = None
    ) -> Dict[str, Any]:
        """Choose the best service based on document type and availability"""
        
        file_size = os.path.getsize(file_path)
        file_ext = Path(file_path).suffix.lower()
        
        # Decision logic for service selection
        if preferred_service == "google_document_ai" and self.google_ai:
            return await self.google_ai.process_document(file_path)
        elif preferred_service == "landing_ai" and self.landing_ai:
            return await self.landing_ai.process_document(file_path)
        else:
            # Auto-select best service
            if file_ext == '.pdf' and file_size > 10 * 1024 * 1024:  # Large PDFs
                service = self.google_ai if self.google_ai else self.landing_ai
            elif file_ext in ['.png', '.jpg', '.jpeg']:  # Images
                service = self.landing_ai if self.landing_ai else self.google_ai
            else:  # Default to Landing AI for structured extraction
                service = self.landing_ai if self.landing_ai else self.google_ai
            
            if service:
                return await service.process_document(file_path)
            else:
                raise Exception("No document processing service available")
    
    def calculate_processing_cost(self, result: Dict[str, Any]) -> int:
        """Calculate processing cost in cents"""
        service = result.get("service", "")
        page_count = result.get("page_count", 1)
        
        if service == "google_document_ai":
            # Google Document AI pricing: $30/1000 pages for custom extraction
            return max(int((page_count / 1000) * 3000), 3)  # Minimum 3 cents
        
        elif service == "landing_ai":
            # Landing AI pricing: 3 credits per page, $0.01 per credit
            return page_count * 3
        
        return 0


# Integration with existing vector service
async def integrate_with_vector_db():
    """Integration example showing how to connect document AI with vector storage"""
    
    from app.services.vector_document_service import vector_document_service
    
    processing_service = DocumentProcessingService()
    
    async def process_and_store_document(
        startup_id: int,
        file_path: str,
        document_type: str,
        preferred_service: Optional[str] = None
    ) -> str:
        """Process a document and store it in the vector database"""
        
        # Step 1: Extract content using AI service
        extraction_result = await processing_service.process_document_with_best_service(
            file_path, preferred_service
        )
        
        if extraction_result.get("error"):
            raise Exception(f"Document processing failed: {extraction_result['error']}")
        
        # Step 2: Calculate processing cost
        processing_cost_cents = processing_service.calculate_processing_cost(extraction_result)
        
        # Step 3: Prepare content categories based on extracted data
        content_categories = []
        structured_data = extraction_result.get("structured_data", {})
        
        if structured_data.get("financial_info"):
            content_categories.append("financial")
        if structured_data.get("team_info"):
            content_categories.append("team")
        if structured_data.get("product_info"):
            content_categories.append("product")
        if structured_data.get("traction_metrics"):
            content_categories.append("traction")
        
        # Step 4: Extract key entities for better searchability
        key_entities = {
            "companies": [structured_data.get("company_info", {}).get("company_name", "")],
            "founders": structured_data.get("team_info", {}).get("founders", []),
            "technologies": structured_data.get("product_info", {}).get("technology_stack", []),
            "industry": [structured_data.get("company_info", {}).get("industry", "")]
        }
        
        # Step 5: Store in vector database
        document_id = await vector_document_service.store_document_vector(
            startup_id=startup_id,
            document_type=document_type,
            filename=Path(file_path).name,
            raw_text=extraction_result["raw_text"],
            structured_data=structured_data,
            extraction_service=extraction_result["service"],
            extraction_confidence=extraction_result.get("confidence"),
            file_url=f"gs://your-bucket/{startup_id}/{Path(file_path).name}",
            content_categories=content_categories,
            key_entities=key_entities
        )
        
        # Step 6: Update processing cost in database (if needed for tracking)
        # This would be added to your existing startup application record
        
        return document_id
    
    return process_and_store_document


# Example usage and testing
async def main():
    """Example usage of the document AI integration"""
    
    # Initialize processing service
    processing_service = DocumentProcessingService()
    
    # Example: Process a sample document
    sample_file = "sample_pitch_deck.pdf"
    
    if os.path.exists(sample_file):
        print("Processing sample document...")
        result = await processing_service.process_document_with_best_service(sample_file)
        
        print(f"Service used: {result['service']}")
        print(f"Text length: {len(result['raw_text'])}")
        print(f"Structured data fields: {list(result['structured_data'].keys())}")
        print(f"Confidence: {result.get('confidence', 'N/A')}")
        
        # Calculate cost
        cost_cents = processing_service.calculate_processing_cost(result)
        print(f"Processing cost: ${cost_cents/100:.2f}")
    
    # Example: Integration with vector database
    process_and_store = await integrate_with_vector_db()
    
    # This would be called when a user uploads a document
    # document_id = await process_and_store(
    #     startup_id=123,
    #     file_path="path/to/document.pdf", 
    #     document_type="pitch_deck"
    # )


if __name__ == "__main__":
    asyncio.run(main())