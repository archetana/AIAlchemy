-- AIAlchemy Database Schema for Supabase
-- Run this in Supabase SQL Editor

-- Create enums
CREATE TYPE application_status AS ENUM (
    'new',
    'data_processing',
    'ai_analysis', 
    'manual_review',
    'partner_review',
    'completed'
);

CREATE TYPE funding_stage AS ENUM (
    'pre_seed',
    'seed',
    'series_a',
    'series_b', 
    'series_c',
    'series_d_plus',
    'growth'
);

CREATE TYPE file_status AS ENUM (
    'uploading',
    'processing',
    'completed',
    'failed'
);

-- Industries table
CREATE TABLE industries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) UNIQUE,
    full_name VARCHAR(200),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Startup Applications table
CREATE TABLE startup_applications (
    id SERIAL PRIMARY KEY,
    
    -- Company Information
    company_name VARCHAR(200) NOT NULL,
    website VARCHAR(500),
    contact_email VARCHAR(255) NOT NULL,
    contact_name VARCHAR(200),
    contact_phone VARCHAR(50),
    industry_id INTEGER REFERENCES industries(id),
    
    -- Funding Information
    funding_stage funding_stage,
    funding_amount_requested DECIMAL(15,2),
    current_arr DECIMAL(15,2),
    gross_margin DECIMAL(5,2),
    runway_months INTEGER,
    
    -- Status and Processing
    status application_status DEFAULT 'new',
    ai_score DECIMAL(5,2),
    manual_score DECIMAL(5,2), 
    final_rating VARCHAR(50),
    
    -- Timestamps and Assignment
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    assigned_at TIMESTAMPTZ,
    assigned_analyst_id INTEGER REFERENCES users(id),
    completed_at TIMESTAMPTZ,
    
    -- Processing metadata
    processing_notes TEXT,
    bottleneck_stage VARCHAR(50),
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Founders table
CREATE TABLE founders (
    id SERIAL PRIMARY KEY,
    startup_application_id INTEGER NOT NULL REFERENCES startup_applications(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    title VARCHAR(100),
    linkedin_url VARCHAR(500),
    years_experience INTEGER,
    previous_companies TEXT,
    education TEXT,
    expertise_areas TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Uploaded Files table
CREATE TABLE uploaded_files (
    id SERIAL PRIMARY KEY,
    startup_application_id INTEGER NOT NULL REFERENCES startup_applications(id) ON DELETE CASCADE,
    
    -- File metadata
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    content_type VARCHAR(100),
    file_size BIGINT,
    file_hash VARCHAR(64),
    
    -- Storage information
    file_path TEXT,
    relative_path VARCHAR(500),
    storage_backend VARCHAR(50) DEFAULT 'local',
    
    -- Processing status
    is_processed BOOLEAN DEFAULT false,
    processing_progress INTEGER DEFAULT 0,
    description TEXT,
    metadata_json JSONB,
    is_safe BOOLEAN DEFAULT true,
    
    -- Timestamps
    upload_timestamp TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    last_accessed_at TIMESTAMPTZ
);

-- Financial Metrics table
CREATE TABLE financial_metrics (
    id SERIAL PRIMARY KEY,
    startup_application_id INTEGER NOT NULL REFERENCES startup_applications(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2),
    metric_unit VARCHAR(20),
    metric_period VARCHAR(50),
    data_source VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Investment Memos table
CREATE TABLE investment_memos (
    id SERIAL PRIMARY KEY,
    startup_application_id INTEGER NOT NULL REFERENCES startup_applications(id) ON DELETE CASCADE,
    
    -- Memo content
    executive_summary TEXT,
    market_analysis TEXT,
    business_model_analysis TEXT,
    team_analysis TEXT,
    financial_analysis TEXT,
    risk_assessment TEXT,
    recommendation VARCHAR(50),
    
    -- Metadata
    generated_by VARCHAR(100),
    generation_method VARCHAR(50),
    confidence_score DECIMAL(5,2),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Evaluation History table
CREATE TABLE evaluation_history (
    id SERIAL PRIMARY KEY,
    startup_application_id INTEGER NOT NULL REFERENCES startup_applications(id) ON DELETE CASCADE,
    evaluator_id INTEGER REFERENCES users(id),
    
    -- Evaluation details
    stage VARCHAR(50) NOT NULL,
    score DECIMAL(5,2),
    notes TEXT,
    decision VARCHAR(50),
    
    -- Timestamps
    evaluated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pipeline Metrics table
CREATE TABLE pipeline_metrics (
    id SERIAL PRIMARY KEY,
    
    -- Metrics by stage
    stage VARCHAR(50) NOT NULL,
    applications_count INTEGER DEFAULT 0,
    avg_processing_time_hours DECIMAL(8,2),
    conversion_rate DECIMAL(5,2),
    bottleneck_threshold INTEGER DEFAULT 5,
    
    -- Time period
    date_recorded DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Investment Weights table (for AI scoring)
CREATE TABLE investment_weights (
    id SERIAL PRIMARY KEY,
    criterion VARCHAR(100) NOT NULL,
    weight DECIMAL(5,4) NOT NULL,
    category VARCHAR(50),
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default industries
INSERT INTO industries (name, description) VALUES
('AI/ML', 'Artificial Intelligence and Machine Learning'),
('FinTech', 'Financial Technology'),
('HealthTech', 'Healthcare Technology'),
('EdTech', 'Education Technology'),
('Enterprise SaaS', 'Enterprise Software as a Service'),
('Consumer Apps', 'Consumer Mobile and Web Applications'),
('E-commerce', 'Electronic Commerce'),
('CleanTech', 'Clean Technology and Sustainability'),
('Blockchain', 'Blockchain and Cryptocurrency'),
('IoT', 'Internet of Things');

-- Insert default investment weights
INSERT INTO investment_weights (criterion, weight, category, description) VALUES
('Market Size', 0.20, 'Market', 'Total addressable market opportunity'),
('Team Experience', 0.25, 'Team', 'Founder and team track record'),
('Product Innovation', 0.15, 'Product', 'Uniqueness and technical innovation'),
('Business Model', 0.15, 'Business', 'Revenue model and scalability'),
('Competitive Advantage', 0.10, 'Market', 'Differentiation and moats'),
('Financial Metrics', 0.10, 'Financial', 'Revenue, growth, and unit economics'),
('Execution Capability', 0.05, 'Team', 'Ability to execute and deliver');

-- Create indexes for better performance
CREATE INDEX idx_startup_applications_status ON startup_applications(status);
CREATE INDEX idx_startup_applications_industry_id ON startup_applications(industry_id);
CREATE INDEX idx_startup_applications_created_at ON startup_applications(created_at);
CREATE INDEX idx_uploaded_files_startup_id ON uploaded_files(startup_application_id);
CREATE INDEX idx_founders_startup_id ON founders(startup_application_id);
CREATE INDEX idx_financial_metrics_startup_id ON financial_metrics(startup_application_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_startup_applications_updated_at BEFORE UPDATE ON startup_applications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_investment_memos_updated_at BEFORE UPDATE ON investment_memos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_investment_weights_updated_at BEFORE UPDATE ON investment_weights FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) for better security
ALTER TABLE startup_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE founders ENABLE ROW LEVEL SECURITY; 
ALTER TABLE uploaded_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE investment_memos ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluation_history ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all for now, you can restrict later)
CREATE POLICY "Enable read access for all users" ON startup_applications FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON startup_applications FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON startup_applications FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON startup_applications FOR DELETE USING (true);

-- Similar policies for other tables
CREATE POLICY "Enable all access for founders" ON founders FOR ALL USING (true);
CREATE POLICY "Enable all access for uploaded_files" ON uploaded_files FOR ALL USING (true);
CREATE POLICY "Enable all access for financial_metrics" ON financial_metrics FOR ALL USING (true);
CREATE POLICY "Enable all access for investment_memos" ON investment_memos FOR ALL USING (true);
CREATE POLICY "Enable all access for evaluation_history" ON evaluation_history FOR ALL USING (true);