"""
Startup Checks for AIAlchemy
Validates configuration and connections at startup
"""

import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class StartupChecker:
    """Performs startup validation checks"""
    
    def __init__(self):
        self.checks_passed = []
        self.checks_failed = []
        self.warnings = []
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all startup validation checks"""
        
        logger.info("🔍 Running startup validation checks...")
        
        # Configuration checks
        await self._check_environment_config()
        await self._check_database_config()
        await self._check_supabase_connection()
        await self._check_ai_model_config()
        
        # Summary
        total_checks = len(self.checks_passed) + len(self.checks_failed)
        success_rate = len(self.checks_passed) / total_checks * 100 if total_checks > 0 else 0
        
        summary = {
            "overall_status": "healthy" if len(self.checks_failed) == 0 else "degraded",
            "total_checks": total_checks,
            "checks_passed": len(self.checks_passed),
            "checks_failed": len(self.checks_failed),
            "warnings": len(self.warnings),
            "success_rate": round(success_rate, 1),
            "passed_checks": self.checks_passed,
            "failed_checks": self.checks_failed,
            "warnings": self.warnings
        }
        
        # Log summary
        if len(self.checks_failed) == 0:
            logger.info(f"✅ All startup checks passed ({len(self.checks_passed)}/{total_checks})")
        else:
            logger.warning(f"⚠️ Some startup checks failed ({len(self.checks_passed)}/{total_checks})")
            for failed_check in self.checks_failed:
                logger.error(f"   ❌ {failed_check}")
        
        return summary
    
    async def _check_environment_config(self):
        """Check environment configuration"""
        try:
            from app.core.config import get_settings
            settings = get_settings()
            
            # Check environment is set
            if settings.environment in ["production", "staging", "development"]:
                self.checks_passed.append("Environment configuration valid")
            else:
                self.checks_failed.append(f"Invalid environment: {settings.environment}")
            
            # Check production requirements
            if settings.environment == "production":
                if not settings.secret_key or settings.secret_key == "development-secret-key":
                    self.checks_failed.append("Production environment requires custom SECRET_KEY")
                else:
                    self.checks_passed.append("Production SECRET_KEY configured")
                
                if settings.debug:
                    self.warnings.append("Debug mode enabled in production")
                else:
                    self.checks_passed.append("Debug mode disabled in production")
        
        except Exception as e:
            self.checks_failed.append(f"Environment config check failed: {e}")
    
    async def _check_database_config(self):
        """Check database configuration"""
        try:
            from app.core.config import get_settings
            from app.services.database_service import db_service
            
            settings = get_settings()
            
            # Check Supabase configuration
            if settings.should_use_supabase:
                if settings.supabase_url and settings.supabase_anon_key:
                    self.checks_passed.append("Supabase credentials configured")
                else:
                    self.checks_failed.append("Supabase selected but credentials missing")
                
                if db_service.use_supabase:
                    self.checks_passed.append("Database service correctly using Supabase")
                else:
                    self.checks_failed.append("Database service NOT using Supabase (configuration mismatch)")
            else:
                if settings.environment == "production":
                    self.warnings.append("Production environment using SQLite instead of Supabase")
                
                if not db_service.use_supabase:
                    self.checks_passed.append("Database service correctly using SQLAlchemy")
                else:
                    self.checks_failed.append("Database service using Supabase but not configured for it")
        
        except Exception as e:
            self.checks_failed.append(f"Database config check failed: {e}")
    
    async def _check_supabase_connection(self):
        """Check Supabase connection if configured"""
        try:
            from app.core.config import get_settings
            settings = get_settings()
            
            if settings.should_use_supabase:
                from app.core.supabase_client import get_supabase_client
                supabase = get_supabase_client()
                
                # Test connection with a simple query
                result = supabase.table('users').select('count').limit(1).execute()
                self.checks_passed.append("Supabase connection successful")
                
                # Check if tables exist
                try:
                    # Test key tables
                    tables_to_check = ['users', 'startup_applications', 'industries']
                    existing_tables = []
                    
                    for table in tables_to_check:
                        try:
                            result = supabase.table(table).select('count').limit(1).execute()
                            existing_tables.append(table)
                        except:
                            pass
                    
                    if len(existing_tables) >= 2:  # At least 2 tables exist
                        self.checks_passed.append(f"Supabase tables exist: {', '.join(existing_tables)}")
                    else:
                        self.warnings.append("Some Supabase tables may not exist - run schema setup")
                
                except Exception as e:
                    self.warnings.append(f"Could not verify Supabase table structure: {e}")
            
            else:
                self.checks_passed.append("Supabase not configured (using SQLAlchemy)")
        
        except Exception as e:
            self.checks_failed.append(f"Supabase connection check failed: {e}")
    
    async def _check_ai_model_config(self):
        """Check AI model configuration"""
        try:
            # Check if model-agnostic service is available
            from app.services.model_agnostic_service import model_service
            
            # Get available models
            available_models = model_service._get_available_models()
            
            if len(available_models) > 1:  # More than just fallback
                self.checks_passed.append(f"AI models available: {len(available_models)} models")
            else:
                self.warnings.append("Only fallback AI model available - consider adding API keys")
            
            # Check for API keys
            api_keys_available = []
            if os.getenv("OPENAI_API_KEY"):
                api_keys_available.append("OpenAI")
            if os.getenv("COHERE_API_KEY"):
                api_keys_available.append("Cohere")
            if os.getenv("ANTHROPIC_API_KEY"):
                api_keys_available.append("Anthropic")
            
            if api_keys_available:
                self.checks_passed.append(f"AI API keys configured: {', '.join(api_keys_available)}")
            else:
                self.warnings.append("No AI API keys configured - using local/fallback models")
        
        except Exception as e:
            self.warnings.append(f"AI model config check failed: {e}")

# Global checker instance
startup_checker = StartupChecker()

async def run_startup_checks() -> Dict[str, Any]:
    """Run all startup checks and return summary"""
    return await startup_checker.run_all_checks()

def force_supabase_mode():
    """Force the application to use Supabase mode"""
    logger.info("🔧 Forcing Supabase mode...")
    
    # Set environment variable
    os.environ["USE_SUPABASE"] = "true"
    
    # Force database service to use Supabase
    try:
        from app.services.database_service import db_service
        from app.core.config import get_settings
        
        settings = get_settings()
        
        if settings.supabase_url and settings.supabase_anon_key:
            db_service.use_supabase = True
            
            # Initialize Supabase client
            from app.core.supabase_client import get_supabase_client
            db_service.supabase = get_supabase_client()
            
            logger.info("✅ Forced Supabase mode activated")
            return True
        else:
            logger.error("❌ Cannot force Supabase mode - credentials missing")
            return False
    
    except Exception as e:
        logger.error(f"❌ Failed to force Supabase mode: {e}")
        return False