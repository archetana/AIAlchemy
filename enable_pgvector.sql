-- Enable pgvector extension for AIAlchemy
-- Run this in Supabase SQL Editor

-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify the extension is enabled
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Test vector functionality
SELECT '[1,2,3]'::vector;

-- Success message
SELECT 'pgvector extension enabled successfully!' as status;