"""
Supabase Client Configuration
Provides a singleton Supabase client for database operations
"""

import os
from typing import Optional
from supabase import create_client, Client
from app.core.config import get_settings

class SupabaseManager:
    """Manages Supabase client connection"""
    
    _client: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client"""
        if cls._client is None:
            cls._client = cls._create_client()
        return cls._client
    
    @classmethod
    def _create_client(cls) -> Client:
        """Create Supabase client from configuration"""
        settings = get_settings()
        
        # Get Supabase credentials
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables"
            )
        
        return create_client(supabase_url, supabase_key)
    
    @classmethod
    def test_connection(cls) -> bool:
        """Test Supabase connection"""
        try:
            client = cls.get_client()
            # Try a simple query to test connection
            result = client.table('startup_applications').select('id').limit(1).execute()
            return True
        except Exception as e:
            print(f"Supabase connection test failed: {e}")
            return False

# Convenience function
def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return SupabaseManager.get_client()