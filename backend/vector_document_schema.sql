-- Vector Database Schema for Document Extraction
-- Supabase + pgvector implementation for AIAlchemy
-- Execute this AFTER enabling the vector extension

-- =====================================================
-- 1. ENABLE VECTOR EXTENSION
-- =====================================================
-- Run this in Supabase SQL Editor first:
-- CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================
-- 2. DOCUMENT EMBEDDINGS TABLE
-- =====================================================

-- Main document storage with vector embeddings
CREATE TABLE IF NOT EXISTS document_vectors (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    startup_application_id INTEGER REFERENCES startup_applications(id) ON DELETE CASCADE,
    
    -- Document metadata
    document_type VARCHAR(100) NOT NULL, -- 'pitch_deck', 'financial_statement', 'business_plan'
    original_filename VARCHAR(255) NOT NULL,
    file_url VARCHAR(500),
    page_number INTEGER DEFAULT 1,
    chunk_index INTEGER DEFAULT 0,     -- For splitting large documents
    
    -- Content
    raw_text TEXT NOT NULL,           -- Original extracted text
    cleaned_text TEXT NOT NULL,      -- Processed, cleaned text for embeddings
    
    -- Vector embeddings (1536 dimensions for OpenAI text-embedding-ada-002)
    text_embedding vector(1536),     -- Semantic embedding of the text content
    
    -- Structured data as JSONB for hybrid queries
    structured_data JSONB DEFAULT '{}',
    
    -- Extraction metadata
    extraction_service VARCHAR(50) NOT NULL, -- 'google_document_ai', 'landing_ai'
    extraction_confidence DECIMAL(5,2),      -- AI confidence score
    processing_cost_cents INTEGER DEFAULT 0,
    
    -- Content classification
    content_categories TEXT[],        -- ['financial', 'product', 'team', 'market']
    key_entities JSONB DEFAULT '{}', -- Named entities: companies, people, dates
    
    -- Quality metrics
    token_count INTEGER,             -- Number of tokens in text
    embedding_model VARCHAR(100) DEFAULT 'text-embedding-ada-002',
    
    -- Status and audit
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_confidence CHECK (extraction_confidence IS NULL OR (extraction_confidence >= 0 AND extraction_confidence <= 100))
);

-- =====================================================
-- 3. DOCUMENT CHUNKS TABLE (for large documents)
-- =====================================================

-- Store document chunks separately for better retrieval
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_vector_id UUID REFERENCES document_vectors(id) ON DELETE CASCADE,
    startup_application_id INTEGER REFERENCES startup_applications(id) ON DELETE CASCADE,
    
    -- Chunk information
    chunk_text TEXT NOT NULL,
    chunk_embedding vector(1536),
    chunk_index INTEGER NOT NULL,
    chunk_size INTEGER,              -- Character count
    
    -- Context preservation
    surrounding_context TEXT,        -- Text before/after for better context
    section_title VARCHAR(200),      -- If document has sections
    
    -- Semantic metadata
    content_type VARCHAR(100),       -- 'executive_summary', 'financials', 'team_info'
    importance_score DECIMAL(3,2) DEFAULT 0.5, -- 0-1 ranking of chunk importance
    
    -- Relationships
    related_chunks UUID[],           -- IDs of semantically related chunks
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 4. SEMANTIC SEARCH RESULTS CACHE
-- =====================================================

-- Cache search results for performance
CREATE TABLE IF NOT EXISTS search_cache (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Query information
    query_text TEXT NOT NULL,
    query_embedding vector(1536),
    query_hash VARCHAR(64) UNIQUE,   -- MD5 of normalized query
    
    -- Search parameters
    similarity_threshold DECIMAL(3,2) DEFAULT 0.7,
    max_results INTEGER DEFAULT 10,
    filter_conditions JSONB DEFAULT '{}',
    
    -- Results
    result_document_ids UUID[],
    result_scores DECIMAL(3,2)[],
    total_results INTEGER,
    
    -- Performance tracking
    search_time_ms INTEGER,
    cache_hits INTEGER DEFAULT 0,
    
    -- Expiry
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '1 hour'),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 5. DOCUMENT ANALYSIS RESULTS
-- =====================================================

-- Store AI analysis results about documents
CREATE TABLE IF NOT EXISTS document_analysis (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_vector_id UUID REFERENCES document_vectors(id) ON DELETE CASCADE,
    startup_application_id INTEGER REFERENCES startup_applications(id) ON DELETE CASCADE,
    
    -- Analysis type and results
    analysis_type VARCHAR(100) NOT NULL, -- 'summary', 'risk_assessment', 'competitive_analysis'
    analysis_prompt TEXT,                 -- Original prompt used
    analysis_result JSONB NOT NULL,      -- Structured analysis results
    
    -- Quality metrics
    confidence_score DECIMAL(5,2),
    processing_time_ms INTEGER,
    tokens_used INTEGER,
    
    -- AI model information
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    
    -- Status
    status VARCHAR(50) DEFAULT 'completed' CHECK (status IN ('processing', 'completed', 'failed')),
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 6. INDEXES FOR VECTOR OPERATIONS
-- =====================================================

-- Vector similarity indexes (HNSW for fast similarity search)
CREATE INDEX IF NOT EXISTS idx_document_vectors_embedding 
ON document_vectors USING hnsw (text_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
ON document_chunks USING hnsw (chunk_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_search_cache_embedding 
ON search_cache USING hnsw (query_embedding vector_cosine_ops);

-- Traditional indexes for metadata queries
CREATE INDEX IF NOT EXISTS idx_document_vectors_startup_id ON document_vectors(startup_application_id);
CREATE INDEX IF NOT EXISTS idx_document_vectors_type ON document_vectors(document_type);
CREATE INDEX IF NOT EXISTS idx_document_vectors_categories ON document_vectors USING gin(content_categories);
CREATE INDEX IF NOT EXISTS idx_document_vectors_created ON document_vectors(created_at);

CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_vector_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_startup_id ON document_chunks(startup_application_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_type ON document_chunks(content_type);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_document_vectors_text_search 
ON document_vectors USING gin(to_tsvector('english', cleaned_text));

CREATE INDEX IF NOT EXISTS idx_document_chunks_text_search 
ON document_chunks USING gin(to_tsvector('english', chunk_text));

-- =====================================================
-- 7. VECTOR SEARCH FUNCTIONS
-- =====================================================

-- Function for semantic similarity search
CREATE OR REPLACE FUNCTION search_documents_by_similarity(
    query_embedding vector(1536),
    similarity_threshold decimal DEFAULT 0.7,
    max_results integer DEFAULT 10,
    startup_id integer DEFAULT NULL,
    document_types text[] DEFAULT NULL
)
RETURNS TABLE (
    document_id uuid,
    startup_application_id integer,
    document_type varchar,
    filename varchar,
    similarity_score decimal,
    text_snippet text,
    structured_data jsonb
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dv.id,
        dv.startup_application_id,
        dv.document_type,
        dv.original_filename,
        (1 - (dv.text_embedding <=> query_embedding))::decimal as similarity_score,
        LEFT(dv.cleaned_text, 500) as text_snippet,
        dv.structured_data
    FROM document_vectors dv
    WHERE 
        dv.status = 'active'
        AND (startup_id IS NULL OR dv.startup_application_id = startup_id)
        AND (document_types IS NULL OR dv.document_type = ANY(document_types))
        AND (1 - (dv.text_embedding <=> query_embedding)) >= similarity_threshold
    ORDER BY dv.text_embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function for hybrid search (vector + keyword)
CREATE OR REPLACE FUNCTION hybrid_document_search(
    query_text text,
    query_embedding vector(1536),
    similarity_threshold decimal DEFAULT 0.7,
    max_results integer DEFAULT 10,
    startup_id integer DEFAULT NULL
)
RETURNS TABLE (
    document_id uuid,
    startup_application_id integer,
    document_type varchar,
    filename varchar,
    combined_score decimal,
    similarity_score decimal,
    text_rank decimal,
    text_snippet text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dv.id,
        dv.startup_application_id,
        dv.document_type,
        dv.original_filename,
        -- Combined scoring: 70% semantic similarity + 30% text search
        (0.7 * (1 - (dv.text_embedding <=> query_embedding)) + 0.3 * ts_rank(to_tsvector('english', dv.cleaned_text), plainto_tsquery('english', query_text)))::decimal as combined_score,
        (1 - (dv.text_embedding <=> query_embedding))::decimal as similarity_score,
        ts_rank(to_tsvector('english', dv.cleaned_text), plainto_tsquery('english', query_text))::decimal as text_rank,
        LEFT(dv.cleaned_text, 500) as text_snippet
    FROM document_vectors dv
    WHERE 
        dv.status = 'active'
        AND (startup_id IS NULL OR dv.startup_application_id = startup_id)
        AND (
            (1 - (dv.text_embedding <=> query_embedding)) >= similarity_threshold
            OR to_tsvector('english', dv.cleaned_text) @@ plainto_tsquery('english', query_text)
        )
    ORDER BY combined_score DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 8. TRIGGERS FOR AUTOMATIC UPDATES
-- =====================================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_vector_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_document_vectors_updated_at 
    BEFORE UPDATE ON document_vectors 
    FOR EACH ROW EXECUTE FUNCTION update_vector_updated_at();

CREATE TRIGGER update_document_chunks_updated_at 
    BEFORE UPDATE ON document_chunks 
    FOR EACH ROW EXECUTE FUNCTION update_vector_updated_at();

CREATE TRIGGER update_document_analysis_updated_at 
    BEFORE UPDATE ON document_analysis 
    FOR EACH ROW EXECUTE FUNCTION update_vector_updated_at();

-- =====================================================
-- 9. ROW LEVEL SECURITY
-- =====================================================

-- Enable RLS
ALTER TABLE document_vectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_analysis ENABLE ROW LEVEL SECURITY;

-- Allow all operations for now (restrict later)
CREATE POLICY "Allow all operations on document_vectors" ON document_vectors FOR ALL USING (true);
CREATE POLICY "Allow all operations on document_chunks" ON document_chunks FOR ALL USING (true);
CREATE POLICY "Allow all operations on search_cache" ON search_cache FOR ALL USING (true);
CREATE POLICY "Allow all operations on document_analysis" ON document_analysis FOR ALL USING (true);

-- =====================================================
-- 10. HELPER VIEWS
-- =====================================================

-- Document statistics view
CREATE OR REPLACE VIEW document_vector_stats AS
SELECT 
    dv.startup_application_id,
    sa.company_name,
    COUNT(*) as total_documents,
    COUNT(DISTINCT dv.document_type) as document_types_count,
    SUM(dv.token_count) as total_tokens,
    SUM(dv.processing_cost_cents) as total_cost_cents,
    AVG(dv.extraction_confidence) as avg_confidence,
    MAX(dv.created_at) as latest_document
FROM document_vectors dv
LEFT JOIN startup_applications sa ON dv.startup_application_id = sa.id
WHERE dv.status = 'active'
GROUP BY dv.startup_application_id, sa.company_name;

-- Search performance view
CREATE OR REPLACE VIEW search_performance AS
SELECT 
    DATE(created_at) as search_date,
    COUNT(*) as total_searches,
    AVG(search_time_ms) as avg_search_time_ms,
    SUM(cache_hits) as total_cache_hits,
    AVG(total_results) as avg_results_returned
FROM search_cache
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY search_date DESC;

-- =====================================================
-- 11. CLEANUP FUNCTIONS
-- =====================================================

-- Function to clean up expired cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM search_cache WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to archive old documents
CREATE OR REPLACE FUNCTION archive_old_documents(days_old INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    UPDATE document_vectors 
    SET status = 'archived' 
    WHERE created_at < NOW() - (days_old || ' days')::INTERVAL 
    AND status = 'active';
    
    GET DIAGNOSTICS archived_count = ROW_COUNT;
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 12. VERIFICATION AND SAMPLE DATA
-- =====================================================

-- Verify vector extension is enabled
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Show table structures
\d document_vectors;
\d document_chunks;

-- Sample document vector (only if startup applications exist)
DO $$ 
DECLARE
    sample_startup_id INTEGER;
    sample_doc_id UUID;
BEGIN
    -- Get a sample startup application ID
    SELECT id INTO sample_startup_id FROM startup_applications LIMIT 1;
    
    IF sample_startup_id IS NOT NULL THEN
        -- Insert sample document vector
        INSERT INTO document_vectors (
            startup_application_id,
            document_type,
            original_filename,
            raw_text,
            cleaned_text,
            text_embedding,
            structured_data,
            extraction_service,
            extraction_confidence,
            content_categories,
            key_entities
        ) VALUES (
            sample_startup_id,
            'pitch_deck',
            'ai_startup_pitch.pdf',
            'AI Innovation Labs: Revolutionizing Healthcare with Machine Learning...',
            'ai innovation labs revolutionizing healthcare machine learning artificial intelligence medical diagnosis',
            '[0.1, 0.2, 0.3]'::vector, -- Placeholder embedding (normally would be 1536 dimensions)
            '{"company_name": "AI Innovation Labs", "industry": "Healthcare AI", "funding_stage": "Series A"}',
            'landing_ai',
            92.5,
            ARRAY['healthcare', 'ai', 'machine-learning'],
            '{"companies": ["AI Innovation Labs"], "people": ["Dr. Sarah Chen"], "technologies": ["machine learning", "AI"]}'
        ) 
        RETURNING id INTO sample_doc_id;
        
        -- Insert sample chunk
        INSERT INTO document_chunks (
            document_vector_id,
            startup_application_id,
            chunk_text,
            chunk_embedding,
            chunk_index,
            content_type,
            importance_score
        ) VALUES (
            sample_doc_id,
            sample_startup_id,
            'Our AI platform reduces medical diagnosis time by 60% through advanced machine learning algorithms.',
            '[0.1, 0.2, 0.3]'::vector, -- Placeholder embedding
            1,
            'value_proposition',
            0.9
        );
    END IF;
END $$;

-- Final verification
SELECT 'Vector database schema setup complete!' as status;
SELECT COUNT(*) as total_document_vectors FROM document_vectors;
SELECT COUNT(*) as total_chunks FROM document_chunks;

-- Show available functions
SELECT proname as function_name 
FROM pg_proc 
WHERE proname IN ('search_documents_by_similarity', 'hybrid_document_search', 'cleanup_expired_cache');

-- =====================================================
-- USAGE EXAMPLES
-- =====================================================

/*
-- Example 1: Semantic search for documents about funding
SELECT * FROM search_documents_by_similarity(
    '[your_query_embedding_here]'::vector,
    0.7,  -- similarity threshold
    5,    -- max results
    123,  -- specific startup_id (optional)
    ARRAY['pitch_deck', 'financial_statement'] -- document types (optional)
);

-- Example 2: Hybrid search combining semantic and keyword search
SELECT * FROM hybrid_document_search(
    'artificial intelligence machine learning',  -- query text
    '[your_query_embedding_here]'::vector,      -- query embedding
    0.6,  -- similarity threshold
    10,   -- max results
    NULL  -- all startups
);

-- Example 3: Find similar companies based on document content
SELECT 
    dv1.startup_application_id as startup1,
    dv2.startup_application_id as startup2,
    (1 - (dv1.text_embedding <=> dv2.text_embedding)) as similarity
FROM document_vectors dv1
JOIN document_vectors dv2 ON dv1.startup_application_id != dv2.startup_application_id
WHERE dv1.document_type = 'pitch_deck' 
AND dv2.document_type = 'pitch_deck'
AND (1 - (dv1.text_embedding <=> dv2.text_embedding)) > 0.8
ORDER BY similarity DESC
LIMIT 10;
*/