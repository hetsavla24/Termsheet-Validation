import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional
import asyncio
from datetime import datetime
import logging

# Import centralized configuration
try:
    from config import MONGODB_URL, DATABASE_NAME
except ImportError:
    # Fallback configuration
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "termsheet_validation")

# Set up logging
logger = logging.getLogger(__name__)

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    try:
        logger.info(f"Connecting to MongoDB at: {MONGODB_URL}")
        mongodb.client = AsyncIOMotorClient(MONGODB_URL)
        mongodb.database = mongodb.client[DATABASE_NAME]
        
        # Import all models for Beanie initialization
        from mongodb_models import (
            User, UserActivity, UploadedFile, ReferenceFile, 
            MasterTemplate, ValidationSession, ExtractedTerm, 
            ValidationResult, DashboardMetrics, SessionMetrics,
            FileMetrics, SystemAudit, NotificationSettings, ApplicationSettings,
            TradeRecord, TermSheetData, ValidationDiscrepancy, ValidationDecision
        )
        
        # Initialize Beanie with the models
        await init_beanie(
            database=mongodb.database,
            document_models=[
                User, UserActivity, UploadedFile, ReferenceFile,
                MasterTemplate, ValidationSession, ExtractedTerm,
                ValidationResult, DashboardMetrics, SessionMetrics,
                FileMetrics, SystemAudit, NotificationSettings, ApplicationSettings,
                TradeRecord, TermSheetData, ValidationDiscrepancy, ValidationDecision
            ]
        )
        logger.info("Connected to MongoDB successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        mongodb.client = None
        mongodb.database = None
        return False

async def close_mongo_connection():
    """Close database connection"""
    try:
        if mongodb.client:
            mongodb.client.close()
            logger.info("Disconnected from MongoDB")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")

def get_database():
    """Get database instance"""
    return mongodb.database

# Health check function
async def ping_database():
    """Ping database to check connection"""
    try:
        if not mongodb.client:
            return False
        await mongodb.client.admin.command('ping')
        return True
    except Exception as e:
        logger.error(f"Database ping failed: {e}")
        return False

async def ensure_indexes():
    """Ensure database indexes are created"""
    try:
        if not mongodb.database:
            return False
            
        # Create indexes for better performance
        collections_indexes = {
            "users": [
                [("email", 1)],
                [("username", 1)],
                [("is_active", 1)],
            ],
            "validation_sessions": [
                [("user_id", 1)],
                [("status", 1)],
                [("created_at", -1)],
            ],
            "uploaded_files": [
                [("user_id", 1)],
                [("processing_status", 1)],
                [("upload_timestamp", -1)],
            ]
        }
        
        for collection_name, indexes in collections_indexes.items():
            collection = mongodb.database[collection_name]
            for index in indexes:
                try:
                    await collection.create_index(index)
                except Exception as e:
                    logger.warning(f"Could not create index {index} on {collection_name}: {e}")
        
        logger.info("Database indexes ensured")
        return True
        
    except Exception as e:
        logger.error(f"Error ensuring indexes: {e}")
        return False 