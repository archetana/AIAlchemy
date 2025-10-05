"""
Memo Generator Agent for AIAlchemy

Uses Gemini Pro to generate comprehensive investment memos from structured startup data.
Provides intelligent analysis, risk assessment, and investment recommendations.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

try:
    import google.generativeai as genai
    from google.oauth2 import service_account
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    logging.getLogger(__name__).warning("Gemini Pro not available - using template-based memo generation")

from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentConfig, ProcessingResult
from .document_ai_agent import DocumentContent, FinancialData, TeamData, BusinessData


class MemoSection(str, Enum):
    """Available memo sections"""
    EXECUTIVE_SUMMARY = "executive_summary"
    INVESTMENT_THESIS = "investment_thesis"
    COMPANY_OVERVIEW = "company_overview"
    MARKET_ANALYSIS = "market_analysis"
    BUSINESS_MODEL = "business_model"
    TEAM_ASSESSMENT = "team_assessment"
    FINANCIAL_ANALYSIS = "financial_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    COMPETITIVE_LANDSCAPE = "competitive_landscape"
    RECOMMENDATION = "recommendation"


class InvestmentRecommendation(str, Enum):
    """Investment recommendation types"""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    PASS = "pass"
    STRONG_PASS = "strong_pass"


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM_LOW = "medium_low"
    MEDIUM = "medium"
    MEDIUM_HIGH = "medium_high"
    HIGH = "high"


class MemoMetadata(BaseModel):
    """Metadata for generated memo"""
    generated_at: datetime
    processing_id: str
    company_name: Optional[str] = None
    analyst: str = "AIAlchemy AI"
    version: str = "1.0"
    sections_included: List[MemoSection]
    total_words: int = 0
    confidence_score: float = 0.0
    generation_time_ms: int = 0


class InvestmentMemo(BaseModel):
    """Complete investment memo structure"""
    metadata: MemoMetadata
    executive_summary: str = ""
    investment_thesis: str = ""
    company_overview: str = ""
    market_analysis: str = ""
    business_model: str = ""
    team_assessment: str = ""
    financial_analysis: str = ""
    risk_assessment: str = ""
    competitive_landscape: str = ""
    recommendation: str = ""
    
    # Structured analysis results
    overall_score: float = 0.0  # 0-100 scale
    recommendation_type: InvestmentRecommendation = InvestmentRecommendation.HOLD
    risk_level: RiskLevel = RiskLevel.MEDIUM
    key_strengths: List[str] = Field(default_factory=list)
    key_concerns: List[str] = Field(default_factory=list)
    success_probability: float = 0.0  # 0-1 scale
    
    def get_total_words(self) -> int:
        """Calculate total word count of memo"""
        sections = [
            self.executive_summary, self.investment_thesis, self.company_overview,
            self.market_analysis, self.business_model, self.team_assessment,
            self.financial_analysis, self.risk_assessment, self.competitive_landscape,
            self.recommendation
        ]
        return sum(len(section.split()) for section in sections)


class MemoGeneratorConfig(AgentConfig):
    """Configuration for Memo Generator Agent"""
    name: str = "memo_generator_agent"
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-pro"
    max_tokens: int = 8192
    temperature: float = 0.7
    credentials_path: Optional[str] = None
    memo_template: str = "comprehensive"  # comprehensive, executive, technical
    target_length: int = 2000  # target word count
    include_charts: bool = False  # future feature for chart generation
    custom_prompts: Dict[str, str] = Field(default_factory=dict)


class MemoGeneratorAgent(BaseAgent):
    """
    Memo Generator Agent using Gemini Pro for intelligent investment memo creation.
    
    Features:
    - Comprehensive investment memo generation
    - Multi-section analysis (market, team, financials, risks)
    - Customizable memo templates and prompts
    - Structured scoring and recommendations
    - Risk assessment and success probability analysis
    """
    
    def __init__(self, config: MemoGeneratorConfig):
        super().__init__(config)
        self.config: MemoGeneratorConfig = config
        self.model = None
        
        if GEMINI_AVAILABLE:
            self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini Pro client"""
        try:
            if self.config.gemini_api_key:
                genai.configure(api_key=self.config.gemini_api_key)
            else:
                # Try to use credentials from file or environment
                if self.config.credentials_path:
                    # Note: Gemini typically uses API key, not service account
                    self.logger.warning(
                        "Gemini uses API key authentication, credentials_path may not be applicable"
                    )
            
            # Initialize the model
            self.model = genai.GenerativeModel(
                model_name=self.config.gemini_model,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                )
            )
            
            self.logger.info(f"Gemini {self.config.gemini_model} initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {e}")
            self.model = None
    
    async def process(
        self,
        document_content: DocumentContent,
        processing_id: str,
        memo_sections: Optional[List[MemoSection]] = None,
        custom_instructions: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate investment memo from document content.
        
        Args:
            document_content: Extracted and structured document content
            processing_id: Unique processing identifier
            memo_sections: Specific sections to include (default: all)
            custom_instructions: Additional instructions for memo generation
            **kwargs: Additional processing parameters
            
        Returns:
            Dictionary containing generated investment memo
        """
        
        if not self.model:
            # Fallback to template-based generation
            memo = await self._generate_fallback_memo(
                document_content, processing_id, memo_sections
            )
        else:
            memo = await self._generate_with_gemini(
                document_content, processing_id, memo_sections, custom_instructions
            )
        
        return {
            "investment_memo": memo.dict(),
            "processing_id": processing_id,
            "generation_method": "gemini_pro" if self.model else "fallback"
        }
    
    async def _generate_with_gemini(
        self,
        document_content: DocumentContent,
        processing_id: str,
        memo_sections: Optional[List[MemoSection]] = None,
        custom_instructions: Optional[str] = None
    ) -> InvestmentMemo:
        """Generate memo using Gemini Pro"""
        
        start_time = datetime.now()
        sections_to_generate = memo_sections or list(MemoSection)
        
        # Create memo metadata
        metadata = MemoMetadata(
            generated_at=start_time,
            processing_id=processing_id,
            company_name=document_content.business_data.company_name,
            sections_included=sections_to_generate,
            confidence_score=document_content.extraction_confidence
        )
        
        # Initialize memo
        memo = InvestmentMemo(metadata=metadata)
        
        # Generate each section
        for section in sections_to_generate:
            try:
                section_content = await self._generate_memo_section(
                    section, document_content, custom_instructions
                )
                setattr(memo, section.value, section_content)
                
            except Exception as e:
                self.logger.error(f"Failed to generate section {section}: {e}")
                setattr(memo, section.value, f"[Error generating {section.value}]")
        
        # Generate structured analysis
        await self._analyze_and_score(memo, document_content)
        
        # Update metadata
        end_time = datetime.now()
        memo.metadata.total_words = memo.get_total_words()
        memo.metadata.generation_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return memo
    
    async def _generate_memo_section(
        self,
        section: MemoSection,
        document_content: DocumentContent,
        custom_instructions: Optional[str] = None
    ) -> str:
        """Generate a specific memo section using Gemini"""
        
        # Build context from document content
        context = self._build_context(document_content)
        
        # Get section-specific prompt
        prompt = self._get_section_prompt(section, context, custom_instructions)
        
        # Generate content with Gemini
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            if response.parts:
                return response.parts[0].text.strip()
            else:
                return f"[No content generated for {section.value}]"
                
        except Exception as e:
            self.logger.error(f"Gemini generation failed for {section}: {e}")
            return f"[Generation error for {section.value}: {str(e)}]"
    
    def _build_context(self, document_content: DocumentContent) -> str:
        """Build context string from document content"""
        
        context_parts = []
        
        # Company and business info
        if document_content.business_data.company_name:
            context_parts.append(f"Company: {document_content.business_data.company_name}")
        
        if document_content.business_data.industry:
            context_parts.append(f"Industry: {document_content.business_data.industry}")
        
        if document_content.business_data.problem_statement:
            context_parts.append(f"Problem: {document_content.business_data.problem_statement}")
        
        if document_content.business_data.solution_description:
            context_parts.append(f"Solution: {document_content.business_data.solution_description}")
        
        # Team information
        if document_content.team_data.founders:
            founders = ", ".join(document_content.team_data.founders)
            context_parts.append(f"Founders: {founders}")
        
        if document_content.team_data.team_size:
            context_parts.append(f"Team Size: {document_content.team_data.team_size}")
        
        # Financial data
        if document_content.financial_data.revenue_current:
            context_parts.append(f"Current Revenue: ${document_content.financial_data.revenue_current:,.0f}")
        
        if document_content.financial_data.funding_amount:
            context_parts.append(f"Funding Sought: ${document_content.financial_data.funding_amount:,.0f}")
        
        if document_content.financial_data.funding_stage:
            context_parts.append(f"Funding Stage: {document_content.financial_data.funding_stage}")
        
        # Raw text excerpt
        if document_content.raw_text:
            text_excerpt = document_content.raw_text[:1500] + "..." if len(document_content.raw_text) > 1500 else document_content.raw_text
            context_parts.append(f"Document Content:\n{text_excerpt}")
        
        return "\n".join(context_parts)
    
    def _get_section_prompt(
        self,
        section: MemoSection,
        context: str,
        custom_instructions: Optional[str] = None
    ) -> str:
        """Get Gemini prompt for specific memo section"""
        
        base_instruction = (
            "You are an expert venture capital analyst. Generate a professional "
            "investment memo section based on the provided startup information. "
            "Be analytical, objective, and provide specific insights backed by data."
        )
        
        if custom_instructions:
            base_instruction += f" Additional instructions: {custom_instructions}"
        
        section_prompts = {
            MemoSection.EXECUTIVE_SUMMARY: (
                "Write a compelling executive summary (200-300 words) that captures:\n"
                "- Key investment opportunity\n"
                "- Market potential\n"
                "- Competitive advantages\n"
                "- Financial highlights\n"
                "- Risk factors\n"
                "- Investment recommendation"
            ),
            
            MemoSection.INVESTMENT_THESIS: (
                "Develop a strong investment thesis (300-400 words) explaining:\n"
                "- Why this is an attractive investment opportunity\n"
                "- Market timing and trends\n"
                "- Competitive moat and differentiation\n"
                "- Scalability potential\n"
                "- Expected returns and exit scenarios"
            ),
            
            MemoSection.COMPANY_OVERVIEW: (
                "Provide a comprehensive company overview (250-350 words) covering:\n"
                "- Business model and value proposition\n"
                "- Products/services offered\n"
                "- Target customer segments\n"
                "- Go-to-market strategy\n"
                "- Current stage and milestones"
            ),
            
            MemoSection.MARKET_ANALYSIS: (
                "Analyze the market opportunity (300-400 words) including:\n"
                "- Total addressable market (TAM) size\n"
                "- Market growth trends and drivers\n"
                "- Customer needs and pain points\n"
                "- Market dynamics and regulations\n"
                "- Expansion opportunities"
            ),
            
            MemoSection.TEAM_ASSESSMENT: (
                "Assess the founding team (200-300 words) evaluating:\n"
                "- Founder backgrounds and experience\n"
                "- Domain expertise and track record\n"
                "- Team composition and skills\n"
                "- Leadership capabilities\n"
                "- Execution ability and vision"
            ),
            
            MemoSection.FINANCIAL_ANALYSIS: (
                "Analyze the financial aspects (300-400 words) covering:\n"
                "- Revenue model and monetization\n"
                "- Current financial performance\n"
                "- Growth projections and assumptions\n"
                "- Unit economics and scalability\n"
                "- Funding requirements and use of funds"
            ),
            
            MemoSection.RISK_ASSESSMENT: (
                "Identify and analyze key risks (250-350 words):\n"
                "- Market risks and competition\n"
                "- Execution and operational risks\n"
                "- Technology and product risks\n"
                "- Regulatory and compliance risks\n"
                "- Financial and funding risks\n"
                "- Mitigation strategies"
            ),
            
            MemoSection.COMPETITIVE_LANDSCAPE: (
                "Analyze the competitive landscape (200-300 words):\n"
                "- Direct and indirect competitors\n"
                "- Competitive advantages and positioning\n"
                "- Market share and differentiation\n"
                "- Barriers to entry\n"
                "- Competitive threats and responses"
            ),
            
            MemoSection.RECOMMENDATION: (
                "Provide a clear investment recommendation (150-250 words):\n"
                "- Investment decision (Pass, Hold, Invest, Strong Invest)\n"
                "- Rationale and key factors\n"
                "- Suggested investment amount and structure\n"
                "- Key milestones and metrics to track\n"
                "- Exit timeline and strategy"
            )
        }
        
        section_prompt = section_prompts.get(section, "Analyze the provided information and generate relevant insights.")
        
        return f"""
{base_instruction}

SECTION TO GENERATE: {section.value.replace('_', ' ').title()}

INSTRUCTIONS:
{section_prompt}

STARTUP INFORMATION:
{context}

Generate the {section.value.replace('_', ' ')} section now:
"""
    
    async def _analyze_and_score(self, memo: InvestmentMemo, document_content: DocumentContent):
        """Generate structured analysis and scoring"""
        
        # Create analysis prompt
        analysis_prompt = f"""
Analyze this startup and provide structured scoring based on the memo content:

MEMO CONTENT:
Executive Summary: {memo.executive_summary}
Investment Thesis: {memo.investment_thesis}
Financial Analysis: {memo.financial_analysis}
Risk Assessment: {memo.risk_assessment}

Provide your analysis in this JSON format:
{{
    "overall_score": <0-100 integer>,
    "recommendation_type": "<strong_buy|buy|hold|pass|strong_pass>",
    "risk_level": "<low|medium_low|medium|medium_high|high>",
    "key_strengths": ["strength1", "strength2", "strength3"],
    "key_concerns": ["concern1", "concern2", "concern3"],
    "success_probability": <0.0-1.0 float>
}}

Be objective and data-driven in your analysis.
"""
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, analysis_prompt
            )
            
            if response.parts:
                # Try to parse JSON response
                import re
                json_match = re.search(r'\{.*\}', response.parts[0].text, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                    
                    memo.overall_score = analysis.get('overall_score', 50)
                    memo.recommendation_type = InvestmentRecommendation(
                        analysis.get('recommendation_type', 'hold')
                    )
                    memo.risk_level = RiskLevel(analysis.get('risk_level', 'medium'))
                    memo.key_strengths = analysis.get('key_strengths', [])
                    memo.key_concerns = analysis.get('key_concerns', [])
                    memo.success_probability = analysis.get('success_probability', 0.5)
            
        except Exception as e:
            self.logger.error(f"Failed to generate structured analysis: {e}")
            # Set default values
            memo.overall_score = 50
            memo.success_probability = 0.5
    
    async def _generate_fallback_memo(
        self,
        document_content: DocumentContent,
        processing_id: str,
        memo_sections: Optional[List[MemoSection]] = None
    ) -> InvestmentMemo:
        """Generate memo using template fallback when Gemini is not available"""
        
        start_time = datetime.now()
        sections_to_generate = memo_sections or list(MemoSection)
        
        metadata = MemoMetadata(
            generated_at=start_time,
            processing_id=processing_id,
            company_name=document_content.business_data.company_name,
            sections_included=sections_to_generate,
            confidence_score=0.3  # Lower confidence for fallback
        )
        
        memo = InvestmentMemo(metadata=metadata)
        
        # Generate template-based sections
        if MemoSection.EXECUTIVE_SUMMARY in sections_to_generate:
            memo.executive_summary = self._generate_template_executive_summary(document_content)
        
        if MemoSection.COMPANY_OVERVIEW in sections_to_generate:
            memo.company_overview = self._generate_template_company_overview(document_content)
        
        if MemoSection.FINANCIAL_ANALYSIS in sections_to_generate:
            memo.financial_analysis = self._generate_template_financial_analysis(document_content)
        
        # Set basic scoring
        memo.overall_score = 50  # Neutral score
        memo.success_probability = 0.5
        
        # Update metadata
        end_time = datetime.now()
        memo.metadata.total_words = memo.get_total_words()
        memo.metadata.generation_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return memo
    
    def _generate_template_executive_summary(self, document_content: DocumentContent) -> str:
        """Generate template-based executive summary"""
        
        company = document_content.business_data.company_name or "The Company"
        industry = document_content.business_data.industry or "technology"
        
        summary = f"""
{company} is a {industry} company that addresses market opportunities through innovative solutions.

Key Highlights:
- Business Model: {document_content.business_data.business_model or 'Technology-driven solution'}
- Market Opportunity: {document_content.business_data.target_market or 'Significant addressable market'}
- Team: {len(document_content.team_data.founders)} founder(s) with relevant experience
"""
        
        if document_content.financial_data.revenue_current:
            summary += f"- Current Revenue: ${document_content.financial_data.revenue_current:,.0f}\n"
        
        if document_content.financial_data.funding_amount:
            summary += f"- Funding Sought: ${document_content.financial_data.funding_amount:,.0f}\n"
        
        summary += "\nThis analysis is based on available document content. Full Gemini Pro analysis recommended for comprehensive evaluation."
        
        return summary.strip()
    
    def _generate_template_company_overview(self, document_content: DocumentContent) -> str:
        """Generate template-based company overview"""
        
        company = document_content.business_data.company_name or "The Company"
        
        overview = f"{company} operates in the {document_content.business_data.industry or 'technology'} sector.\n\n"
        
        if document_content.business_data.problem_statement:
            overview += f"Problem Statement: {document_content.business_data.problem_statement}\n\n"
        
        if document_content.business_data.solution_description:
            overview += f"Solution: {document_content.business_data.solution_description}\n\n"
        
        overview += "Note: This is a template-based overview. Enhanced analysis available with Gemini Pro integration."
        
        return overview
    
    def _generate_template_financial_analysis(self, document_content: DocumentContent) -> str:
        """Generate template-based financial analysis"""
        
        analysis = "Financial Analysis:\n\n"
        
        financial = document_content.financial_data
        
        if financial.revenue_current:
            analysis += f"Current Revenue: ${financial.revenue_current:,.0f}\n"
        
        if financial.revenue_projected:
            analysis += f"Projected Revenue: ${financial.revenue_projected:,.0f}\n"
        
        if financial.funding_amount:
            analysis += f"Funding Requirements: ${financial.funding_amount:,.0f}\n"
        
        if financial.funding_stage:
            analysis += f"Funding Stage: {financial.funding_stage}\n"
        
        if not any([financial.revenue_current, financial.funding_amount]):
            analysis += "Limited financial data available from document processing.\n"
        
        analysis += "\nNote: Template-based analysis. Comprehensive financial modeling available with full AI integration."
        
        return analysis
    
    async def generate_custom_section(
        self,
        section_name: str,
        document_content: DocumentContent,
        custom_prompt: str,
        processing_id: str
    ) -> str:
        """Generate a custom memo section with user-defined prompt"""
        
        if not self.model:
            return f"Custom section '{section_name}' requires Gemini Pro integration."
        
        context = self._build_context(document_content)
        
        full_prompt = f"""
You are an expert venture capital analyst. Generate a custom memo section based on the provided startup information.

SECTION: {section_name}
CUSTOM INSTRUCTIONS: {custom_prompt}

STARTUP INFORMATION:
{context}

Generate the custom section now:
"""
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, full_prompt
            )
            
            if response.parts:
                return response.parts[0].text.strip()
            else:
                return f"No content generated for custom section: {section_name}"
                
        except Exception as e:
            self.logger.error(f"Custom section generation failed: {e}")
            return f"Error generating custom section: {str(e)}"
    
    async def get_memo_templates(self) -> Dict[str, List[MemoSection]]:
        """Get available memo templates"""
        
        return {
            "comprehensive": list(MemoSection),
            "executive": [
                MemoSection.EXECUTIVE_SUMMARY,
                MemoSection.INVESTMENT_THESIS,
                MemoSection.FINANCIAL_ANALYSIS,
                MemoSection.RISK_ASSESSMENT,
                MemoSection.RECOMMENDATION
            ],
            "technical": [
                MemoSection.COMPANY_OVERVIEW,
                MemoSection.MARKET_ANALYSIS,
                MemoSection.COMPETITIVE_LANDSCAPE,
                MemoSection.TEAM_ASSESSMENT,
                MemoSection.RECOMMENDATION
            ]
        }