#!/usr/bin/env python3
"""
Termsheet Validation System - Startup Script
Handles server initialization, dependency checks, and database setup.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
import subprocess
import importlib.util

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    logger.info(f"✅ Python version: {sys.version}")
    return True

def check_required_packages():
    """Check if all required packages are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'motor', 'beanie', 'pymongo',
        'passlib', 'python-jose', 'python-multipart', 'aiofiles',
        'python-decouple', 'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ Missing packages: {', '.join(missing_packages)}")
        logger.info("Install missing packages with: pip install -r requirements.txt")
        return False
    
    logger.info("✅ All required packages are installed")
    return True

def check_environment_variables():
    """Check and set up environment variables"""
    required_vars = {
        'MONGODB_URL': 'mongodb://localhost:27017',
        'DATABASE_NAME': 'termsheet_validation',
        'SECRET_KEY': 'your-super-secret-jwt-key-change-this-in-production-2024',
        'DEBUG': 'True',
        'ENVIRONMENT': 'development'
    }
    
    missing_vars = []
    for var, default in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(var)
            os.environ[var] = default
            logger.info(f"⚠️ Set {var} to default: {default}")
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.info("Consider creating a .env file with your configuration")
    else:
        logger.info("✅ Environment variables configured")
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        'uploads',
        'uploaded_files',
        'uploads/reference',
        'uploads/samples',
        'logs'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✅ Created directory: {directory}")
        except Exception as e:
            logger.error(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

async def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        from mongodb_config import connect_to_mongo, ping_database, close_mongo_connection
        
        logger.info("Testing MongoDB connection...")
        connection_success = await connect_to_mongo()
        
        if connection_success:
            ping_success = await ping_database()
            if ping_success:
                logger.info("✅ MongoDB connection successful")
                await close_mongo_connection()
                return True
            else:
                logger.error("❌ MongoDB ping failed")
                return False
        else:
            logger.error("❌ MongoDB connection failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ MongoDB connection error: {e}")
        return False

async def initialize_database():
    """Initialize database with default data"""
    try:
        from mongodb_config import connect_to_mongo, ensure_indexes
        from mongodb_models import User, ApplicationSettings
        from auth import get_password_hash
        
        logger.info("Initializing database...")
        await connect_to_mongo()
        
        # Ensure indexes
        await ensure_indexes()
        logger.info("✅ Database indexes ensured")
        
        # Create default admin user if it doesn't exist
        admin_user = await User.find_one(User.email == "admin@termsheet.com")
        if not admin_user:
            admin_user = User(
                email="admin@termsheet.com",
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_verified=True,
                is_admin=True,
                role="admin"
            )
            await admin_user.insert()
            logger.info("✅ Created default admin user (admin@termsheet.com / admin123)")
        
        # Create default application settings
        settings = await ApplicationSettings.find_one(ApplicationSettings.setting_key == "system_config")
        if not settings:
            settings = ApplicationSettings(
                setting_key="system_config",
                setting_value={
                    "max_file_size_mb": 16,
                    "allowed_file_types": [".pdf", ".xlsx", ".xls", ".csv"],
                    "session_timeout_minutes": 30,
                    "auto_cleanup_days": 30
                },
                description="System configuration settings",
                is_system=True
            )
            await settings.insert()
            logger.info("✅ Created default application settings")
        
        logger.info("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        return False

def check_mongodb_service():
    """Check if MongoDB service is running"""
    try:
        # Try to connect to MongoDB
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        client.server_info()
        logger.info("✅ MongoDB service is running")
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB service check failed: {e}")
        logger.info("Make sure MongoDB is installed and running:")
        logger.info("  - Install: https://docs.mongodb.com/manual/installation/")
        logger.info("  - Start: sudo systemctl start mongod (Linux) or brew services start mongodb-community (Mac)")
        return False

def display_startup_info():
    """Display startup information"""
    logger.info("=" * 60)
    logger.info("🚀 TERMSHEET VALIDATION SYSTEM STARTUP")
    logger.info("=" * 60)
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Working Directory: {os.getcwd()}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Debug Mode: {os.getenv('DEBUG', 'True')}")
    logger.info(f"MongoDB URL: {os.getenv('MONGODB_URL', 'not set')}")
    logger.info("=" * 60)

def display_completion_info():
    """Display completion information"""
    logger.info("=" * 60)
    logger.info("✅ STARTUP COMPLETE")
    logger.info("=" * 60)
    logger.info("Server endpoints:")
    logger.info("  - Health Check: http://localhost:8000/health")
    logger.info("  - API Documentation: http://localhost:8000/docs")
    logger.info("  - API Status: http://localhost:8000/api/status")
    logger.info("")
    logger.info("Frontend URLs:")
    logger.info("  - Application: http://localhost:3000")
    logger.info("  - Login: http://localhost:3000/login")
    logger.info("")
    logger.info("Default admin credentials:")
    logger.info("  - Email: admin@termsheet.com")
    logger.info("  - Password: admin123")
    logger.info("=" * 60)

async def main():
    """Main startup function"""
    display_startup_info()
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_required_packages():
        sys.exit(1)
    
    if not check_environment_variables():
        sys.exit(1)
    
    if not create_directories():
        sys.exit(1)
    
    if not check_mongodb_service():
        logger.warning("⚠️ MongoDB service is not running. Server will start but database features will be limited.")
    
    # Test database connection
    db_success = await test_mongodb_connection()
    if db_success:
        # Initialize database
        await initialize_database()
    else:
        logger.warning("⚠️ Database initialization skipped due to connection failure")
    
    display_completion_info()
    
    # Start the server
    try:
        import uvicorn
        logger.info("🚀 Starting FastAPI server...")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=os.getenv('DEBUG', 'True').lower() == 'true',
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 