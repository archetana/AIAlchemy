-- Document Extraction Storage Schema for AIAlchemy
-- Add to existing Supabase database for storing document AI results
-- Execute this AFTER running the main supabase_schema.sql

-- =====================================================
-- DOCUMENT EXTRACTION TABLES
-- =====================================================

-- Document extraction results table
CREATE TABLE IF NOT EXISTS document_extractions (
    id SERIAL PRIMARY KEY,
    startup_application_id INTEGER REFERENCES startup_applications(id) ON DELETE CASCADE,
    
    -- File metadata
    original_filename VARCHAR(255) NOT NULL,
    file_url VARCHAR(500),                 -- URL in GCS or local storage
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    
    -- Extraction configuration
    extraction_service VARCHAR(50) NOT NULL CHECK (extraction_service IN ('google_document_ai', 'landing_ai', 'manual')),
    extraction_type VARCHAR(100) NOT NULL, -- 'pitch_deck', 'financial_statement', 'business_plan', 'invoice', etc.
    processor_name VARCHAR(100),           -- Specific AI processor used
    
    -- Processing results
    raw_response JSONB NOT NULL,          -- Full API response from extraction service
    structured_data JSONB,                -- Cleaned, normalized data for application
    extracted_text TEXT,                  -- Plain text content (searchable)
    
    -- Quality metrics
    page_count INTEGER DEFAULT 1,
    processing_cost_cents INTEGER DEFAULT 0,  -- Cost tracking in cents
    processing_time_ms INTEGER,               -- Performance monitoring
    confidence_score DECIMAL(5,2),           -- AI confidence 0-100
    
    -- Status and error handling
    status VARCHAR(50) DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed', 'skipped')),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Audit trail
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_by VARCHAR(100),            -- User or system that initiated processing
    
    -- Constraints
    CONSTRAINT valid_confidence CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100))
);

-- Document extraction fields table (for structured field mapping)
CREATE TABLE IF NOT EXISTS extraction_fields (
    id SERIAL PRIMARY KEY,
    document_extraction_id INTEGER REFERENCES document_extractions(id) ON DELETE CASCADE,
    
    -- Field identification
    field_name VARCHAR(100) NOT NULL,     -- e.g., 'company_name', 'revenue_2023', 'founder_name'
    field_type VARCHAR(50) NOT NULL,      -- 'text', 'number', 'date', 'currency', 'percentage', 'boolean'
    field_category VARCHAR(50),           -- 'company_info', 'financial', 'team', 'product'
    
    -- Extracted values
    raw_value TEXT,                       -- Original extracted text
    normalized_value TEXT,                -- Cleaned/standardized value
    numeric_value DECIMAL(15,2),          -- For calculations (revenue, costs, etc.)
    
    -- Quality metrics
    confidence_score DECIMAL(5,2),        -- Field-specific confidence
    extraction_method VARCHAR(50),        -- 'ai_extraction', 'ocr', 'manual_override'
    
    -- Validation
    is_validated BOOLEAN DEFAULT FALSE,   -- Human validation flag
    validation_notes TEXT,
    
    -- Position information (for debugging)
    page_number INTEGER,
    bounding_box JSONB,                   -- Coordinates where field was found
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_field_confidence CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100))
);

-- Document processing queue for async processing
CREATE TABLE IF NOT EXISTS document_processing_queue (
    id SERIAL PRIMARY KEY,
    startup_application_id INTEGER REFERENCES startup_applications(id) ON DELETE CASCADE,
    
    -- File information
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT,
    document_type VARCHAR(100) NOT NULL,  -- 'pitch_deck', 'financial_docs', etc.
    
    -- Processing configuration
    extraction_service VARCHAR(50) NOT NULL,
    processor_config JSONB DEFAULT '{}',  -- Service-specific configuration
    priority INTEGER DEFAULT 5,          -- 1=high, 10=low priority
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    
    -- Error handling
    error_message TEXT,
    last_error_at TIMESTAMP WITH TIME ZONE,
    
    -- Scheduling
    scheduled_for TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Document extractions indexes
CREATE INDEX IF NOT EXISTS idx_document_extractions_startup_id ON document_extractions(startup_application_id);
CREATE INDEX IF NOT EXISTS idx_document_extractions_status ON document_extractions(status);
CREATE INDEX IF NOT EXISTS idx_document_extractions_service ON document_extractions(extraction_service);
CREATE INDEX IF NOT EXISTS idx_document_extractions_type ON document_extractions(extraction_type);
CREATE INDEX IF NOT EXISTS idx_document_extractions_created ON document_extractions(created_at);

-- Extraction fields indexes
CREATE INDEX IF NOT EXISTS idx_extraction_fields_doc_id ON extraction_fields(document_extraction_id);
CREATE INDEX IF NOT EXISTS idx_extraction_fields_name ON extraction_fields(field_name);
CREATE INDEX IF NOT EXISTS idx_extraction_fields_category ON extraction_fields(field_category);
CREATE INDEX IF NOT EXISTS idx_extraction_fields_validated ON extraction_fields(is_validated);

-- Processing queue indexes
CREATE INDEX IF NOT EXISTS idx_processing_queue_status ON document_processing_queue(status);
CREATE INDEX IF NOT EXISTS idx_processing_queue_priority ON document_processing_queue(priority, scheduled_for);
CREATE INDEX IF NOT EXISTS idx_processing_queue_startup ON document_processing_queue(startup_application_id);

-- Full-text search on extracted text
CREATE INDEX IF NOT EXISTS idx_document_extractions_text_search ON document_extractions USING gin(to_tsvector('english', extracted_text));

-- =====================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =====================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_document_extractions_updated_at BEFORE UPDATE ON document_extractions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_extraction_fields_updated_at BEFORE UPDATE ON extraction_fields FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_processing_queue_updated_at BEFORE UPDATE ON document_processing_queue FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS
ALTER TABLE document_extractions ENABLE ROW LEVEL SECURITY;
ALTER TABLE extraction_fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_processing_queue ENABLE ROW LEVEL SECURITY;

-- Allow all operations for now (restrict later based on user roles)
CREATE POLICY "Allow all operations on document_extractions" ON document_extractions FOR ALL USING (true);
CREATE POLICY "Allow all operations on extraction_fields" ON extraction_fields FOR ALL USING (true);
CREATE POLICY "Allow all operations on document_processing_queue" ON document_processing_queue FOR ALL USING (true);

-- =====================================================
-- HELPER VIEWS
-- =====================================================

-- View for document extraction summary
CREATE OR REPLACE VIEW document_extraction_summary AS
SELECT 
    de.id,
    de.startup_application_id,
    sa.company_name,
    de.original_filename,
    de.extraction_type,
    de.status,
    de.page_count,
    de.processing_cost_cents,
    de.confidence_score,
    de.created_at,
    COUNT(ef.id) as extracted_fields_count,
    AVG(ef.confidence_score) as avg_field_confidence
FROM document_extractions de
LEFT JOIN startup_applications sa ON de.startup_application_id = sa.id
LEFT JOIN extraction_fields ef ON de.id = ef.document_extraction_id
GROUP BY de.id, sa.company_name;

-- View for processing queue status
CREATE OR REPLACE VIEW processing_queue_status AS
SELECT 
    status,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (NOW() - created_at))/60) as avg_wait_minutes
FROM document_processing_queue 
GROUP BY status;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Verify tables were created
SELECT 
    schemaname, 
    tablename, 
    tableowner 
FROM pg_tables 
WHERE tablename IN ('document_extractions', 'extraction_fields', 'document_processing_queue')
ORDER BY tablename;

-- Show table structure
\d document_extractions;
\d extraction_fields;
\d document_processing_queue;

-- =====================================================
-- SAMPLE DATA (OPTIONAL)
-- =====================================================

-- Insert sample document extraction (only if startup applications exist)
DO $$ 
DECLARE
    sample_startup_id INTEGER;
BEGIN
    -- Get a sample startup application ID
    SELECT id INTO sample_startup_id FROM startup_applications LIMIT 1;
    
    IF sample_startup_id IS NOT NULL THEN
        INSERT INTO document_extractions (
            startup_application_id,
            original_filename,
            file_url,
            extraction_service,
            extraction_type,
            raw_response,
            structured_data,
            extracted_text,
            page_count,
            processing_cost_cents,
            confidence_score,
            status
        ) VALUES (
            sample_startup_id,
            'pitch_deck_sample.pdf',
            'https://storage.googleapis.com/bucket/pitch_deck_sample.pdf',
            'landing_ai',
            'pitch_deck',
            '{"parser": "landing_ai", "version": "1.0", "pages": 10}',
            '{"company_name": "AI Innovation Labs", "market_size": "$50B", "funding_request": "$2M"}',
            'AI Innovation Labs - Revolutionizing Healthcare with AI...',
            10,
            300,
            89.5,
            'completed'
        ) ON CONFLICT DO NOTHING;
        
        -- Insert sample extraction fields
        INSERT INTO extraction_fields (
            document_extraction_id,
            field_name,
            field_type, 
            field_category,
            raw_value,
            normalized_value,
            numeric_value,
            confidence_score
        ) VALUES 
        ((SELECT id FROM document_extractions WHERE original_filename = 'pitch_deck_sample.pdf' LIMIT 1),
         'funding_request', 'currency', 'financial', '$2,000,000', '2000000', 2000000.00, 95.0),
        ((SELECT id FROM document_extractions WHERE original_filename = 'pitch_deck_sample.pdf' LIMIT 1),
         'market_size', 'currency', 'market', '$50 Billion', '50000000000', 50000000000.00, 85.0)
        ON CONFLICT DO NOTHING;
    END IF;
END $$;

-- =====================================================
-- FINAL VERIFICATION
-- =====================================================

SELECT 'Document extraction schema setup complete!' as status;
SELECT COUNT(*) as sample_extractions FROM document_extractions;
SELECT COUNT(*) as sample_fields FROM extraction_fields;