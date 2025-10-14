-- AIAlchemy - Create Initial Admin User
-- Execute this in Supabase SQL Editor to create the initial admin account

-- Create admin user with proper permissions
INSERT INTO users (email, username, full_name, hashed_password, is_active, is_superuser) VALUES
('admin@aialchemy.com', 'admin', 'System Administrator', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LgnaVxJzjAs.wO/Ne', true, true)
ON CONFLICT (email) DO NOTHING;

-- Verify user was created
SELECT email, username, full_name, is_active, is_superuser, created_at 
FROM users 
WHERE email = 'admin@aialchemy.com';

-- Show total user count
SELECT COUNT(*) as total_users FROM users;