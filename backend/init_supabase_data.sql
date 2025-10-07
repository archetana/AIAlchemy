-- AIAlchemy Database Initialization Data
-- This file contains all required initial data for the application to work properly
-- Execute this AFTER running the main supabase_schema.sql

-- =====================================================
-- 1. INDUSTRIES (REQUIRED FOR STARTUP APPLICATIONS)
-- =====================================================

-- Clear existing data and reset sequence
DELETE FROM industries;
ALTER SEQUENCE industries_id_seq RESTART WITH 1;

-- Insert required industries (matching frontend expectations)
INSERT INTO industries (id, name, description) VALUES
(1, 'AI/ML', 'Artificial Intelligence and Machine Learning'),
(2, 'FinTech', 'Financial Technology'),
(3, 'HealthTech', 'Healthcare Technology'),
(4, 'EdTech', 'Education Technology'),
(5, 'E-commerce', 'Electronic Commerce'),
(6, 'Enterprise SaaS', 'Enterprise Software as a Service'),
(7, 'Consumer Apps', 'Consumer Mobile and Web Applications'),
(8, 'CleanTech', 'Clean Technology and Sustainability'),
(9, 'Blockchain', 'Blockchain and Cryptocurrency'),
(10, 'IoT', 'Internet of Things'),
(11, 'Other', 'Other Industries');

-- =====================================================
-- 2. INVESTMENT WEIGHTS (REQUIRED FOR AI SCORING)
-- =====================================================

-- Clear existing data and reset sequence  
DELETE FROM investment_weights;
ALTER SEQUENCE investment_weights_id_seq RESTART WITH 1;

-- Insert AI evaluation criteria and weights
INSERT INTO investment_weights (criterion, weight, category, description) VALUES
('Market Size', 0.20, 'Market', 'Total addressable market opportunity'),
('Team Experience', 0.25, 'Team', 'Founder and team track record'),
('Product Innovation', 0.15, 'Product', 'Uniqueness and technical innovation'),
('Business Model', 0.15, 'Business', 'Revenue model and scalability'),
('Competitive Advantage', 0.10, 'Market', 'Differentiation and moats'),
('Financial Metrics', 0.10, 'Financial', 'Revenue, growth, and unit economics'),
('Execution Capability', 0.05, 'Team', 'Ability to execute and deliver');

-- =====================================================
-- 3. DEFAULT ADMIN USER (OPTIONAL - FOR TESTING)
-- =====================================================

-- Create default admin user (password: 'admin123' - CHANGE IN PRODUCTION!)
-- Password hash for 'admin123' using bcrypt
INSERT INTO users (email, username, full_name, hashed_password, is_active, is_superuser) VALUES
('admin@aialchemy.com', 'admin', 'System Administrator', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LgnaVxJzjAs.wO/Ne', true, true)
ON CONFLICT (email) DO NOTHING;

-- =====================================================
-- 4. SAMPLE TEST DATA (OPTIONAL - FOR DEVELOPMENT)
-- =====================================================

-- Insert sample startup application for testing
INSERT INTO startup_applications (
    company_name,
    website, 
    contact_email,
    contact_name,
    contact_phone,
    industry_id,
    funding_stage,
    funding_amount_requested,
    current_arr,
    gross_margin,
    runway_months,
    status,
    submitted_at
) VALUES (
    'AI Innovation Labs',
    'https://aiinnovationlabs.com',
    'contact@aiinnovationlabs.com', 
    'Sarah Chen',
    '+1 (555) 123-4567',
    1, -- AI/ML industry
    'seed',
    2000000.00,
    500000.00,
    75.0,
    18,
    'new',
    NOW()
) ON CONFLICT DO NOTHING;

-- Insert sample founder for the test startup
INSERT INTO founders (
    startup_application_id,
    name,
    title,
    linkedin_url,
    years_experience,
    previous_companies,
    education,
    expertise_areas
) VALUES (
    (SELECT id FROM startup_applications WHERE company_name = 'AI Innovation Labs' LIMIT 1),
    'Sarah Chen',
    'CEO & Co-Founder',
    'https://linkedin.com/in/sarahchen',
    8,
    'Google, Meta',
    'Stanford University - MS Computer Science',
    'AI/ML, Product Management, Team Leadership'
) ON CONFLICT DO NOTHING;

-- =====================================================
-- 5. PIPELINE METRICS INITIALIZATION
-- =====================================================

-- Insert initial pipeline metrics for dashboard
INSERT INTO pipeline_metrics (stage, applications_count, avg_processing_time_hours, conversion_rate, date_recorded) VALUES
('new', 0, 0.0, 100.0, CURRENT_DATE),
('data_processing', 0, 2.5, 95.0, CURRENT_DATE),
('ai_analysis', 0, 4.0, 85.0, CURRENT_DATE),
('manual_review', 0, 24.0, 75.0, CURRENT_DATE),
('partner_review', 0, 72.0, 60.0, CURRENT_DATE),
('completed', 0, 168.0, 45.0, CURRENT_DATE)
ON CONFLICT DO NOTHING;

-- =====================================================
-- 6. VERIFICATION QUERIES
-- =====================================================

-- Verify all required data is present
SELECT 'Industries Count: ' || COUNT(*) as verification FROM industries;
SELECT 'Investment Weights Count: ' || COUNT(*) as verification FROM investment_weights;  
SELECT 'Users Count: ' || COUNT(*) as verification FROM users;
SELECT 'Sample Applications: ' || COUNT(*) as verification FROM startup_applications;

-- Check industry IDs match frontend expectations  
SELECT id, name FROM industries ORDER BY id;

-- Verify investment weights sum to 1.0
SELECT 'Total Weight: ' || SUM(weight) as verification FROM investment_weights WHERE is_active = true;

-- =====================================================
-- 7. POST-INITIALIZATION NOTES
-- =====================================================

/*
CRITICAL REQUIREMENTS FOR APPLICATION TO WORK:

1. INDUSTRIES TABLE: Must have at least these IDs that frontend expects:
   - ID 1-8: Match the fallback industries in Upload.js
   - Frontend will break if these don't exist

2. INVESTMENT WEIGHTS: Required for AI scoring algorithm:
   - Must sum to 1.0 (100%)
   - Categories: Market, Team, Product, Business, Financial
   
3. ENUMS: Must match backend model definitions:
   - application_status: new, data_processing, ai_analysis, manual_review, partner_review, completed
   - funding_stage: pre_seed, seed, series_a, series_b, series_c, series_d_plus, growth
   - file_status: uploading, processing, completed, failed

4. ADMIN USER: Optional but recommended for initial access
   - Default: admin@aialchemy.com / admin123
   - CHANGE PASSWORD IN PRODUCTION!

5. RLS POLICIES: Already configured to allow all operations
   - Restrict in production based on user roles
*/