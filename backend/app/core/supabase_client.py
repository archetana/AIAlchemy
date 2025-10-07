"""
Supabase Client Configuration
Provides a singleton Supabase client for database operations
"""

import os
import socket
from typing import Optional
import httpx
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
        """Create Supabase client from configuration with IPv4-only support"""
        settings = get_settings()
        
        # Get Supabase credentials
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables"
            )
        
        # Configure client options to force IPv4 connections
        # This resolves IPv6 connectivity issues by ensuring only IPv4 addresses are used
        
        try:
            # Force IPv4-only DNS resolution for this process
            # Override getaddrinfo to return only IPv4 addresses
            original_getaddrinfo = socket.getaddrinfo
            
            def ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
                return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
            
            # Temporarily override DNS resolution
            socket.getaddrinfo = ipv4_only_getaddrinfo
            
            # Create Supabase client with IPv4-only DNS resolution
            client = create_client(supabase_url, supabase_key)
            
            # Restore original DNS resolution
            socket.getaddrinfo = original_getaddrinfo
            
            # Test the connection to ensure it works
            try:
                # Simple test query (will fail if tables don't exist, but connection works)
                client.table('startup_applications').select('id').limit(1).execute()
                print("✅ Supabase client created with IPv4-only configuration")
            except Exception as test_e:
                if "Could not find the table" in str(test_e):
                    print("✅ Supabase client created successfully (tables not yet created)")
                else:
                    print(f"⚠️  Supabase client created but connection test failed: {test_e}")
            
            return client
            
        except Exception as e:
            print(f"Warning: IPv4-only configuration failed, using default client: {e}")
            # Fallback to default client
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