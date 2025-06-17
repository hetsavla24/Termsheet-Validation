from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import configurations
try:
    from config import DEBUG, CORS_ORIGINS, PROJECT_NAME, VERSION, API_V1_STR
except ImportError:
    DEBUG = True
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ]
    PROJECT_NAME = "Termsheet Validation System"
    VERSION = "3.0.0"
    API_V1_STR = "/api"

# Import MongoDB configuration
try:
    from mongodb_config import connect_to_mongo, close_mongo_connection, ping_database, ensure_indexes
    HAS_MONGODB = True
except ImportError as e:
    logger.error(f"MongoDB configuration error: {e}")
    HAS_MONGODB = False
    async def connect_to_mongo():
        return False
    async def close_mongo_connection():
        pass
    async def ping_database():
        return False
    async def ensure_indexes():
        return False

# Import routers with error handling
try:
    from routers import auth, upload, validation
    HAS_ROUTERS = True
    logger.info("Successfully imported all routers")
except ImportError as e:
    logger.error(f"Router import error: {e}")
    HAS_ROUTERS = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting Termsheet Validation System...")
    
    if HAS_MONGODB:
        try:
            connection_success = await connect_to_mongo()
            if connection_success and await ping_database():
                logger.info("✅ Database connection established successfully!")
                # Ensure indexes are created
                await ensure_indexes()
                logger.info("✅ Database indexes ensured!")
            else:
                logger.warning("⚠️ Database connection failed!")
        except Exception as e:
            logger.error(f"Database startup error: {e}")
    else:
        logger.warning("⚠️ MongoDB not configured, running without database")
    
    # Create upload directories
    try:
        directories = ["uploads", "uploaded_files", "uploads/reference", "uploads/samples"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        logger.info("✅ Upload directories created")
    except Exception as e:
        logger.error(f"Directory creation error: {e}")
    
    yield
    
    # Shutdown
    logger.info("📋 Shutting down Termsheet Validation System...")
    if HAS_MONGODB:
        try:
            await close_mongo_connection()
        except Exception as e:
            logger.error(f"Database shutdown error: {e}")

# Initialize FastAPI app
app = FastAPI(
    title=PROJECT_NAME,
    description="Advanced termsheet processing with document analysis & validation using MongoDB",
    version=VERSION,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware with comprehensive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + ["*"] if DEBUG else CORS_ORIGINS,  # Allow all origins in debug mode
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers with error handling
if HAS_ROUTERS:
    try:
        app.include_router(auth.router, prefix=API_V1_STR)
        logger.info("✅ Auth router included")
    except Exception as e:
        logger.error(f"Auth router error: {e}")
    
    try:
        app.include_router(upload.router, prefix=API_V1_STR)
        logger.info("✅ Upload router included")
    except Exception as e:
        logger.error(f"Upload router error: {e}")
    
    try:
        app.include_router(validation.router, prefix=API_V1_STR)
        logger.info("✅ Validation router included")
    except Exception as e:
        logger.error(f"Validation router error: {e}")
else:
    logger.error("❌ No routers available")

# Serve uploaded files (for development)
if DEBUG:
    try:
        app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
        app.mount("/uploaded_files", StaticFiles(directory="uploaded_files"), name="uploaded_files")
        logger.info("✅ Static file serving enabled")
    except Exception as e:
        logger.error(f"Static files error: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"{PROJECT_NAME} API", 
        "version": VERSION,
        "status": "running",
        "database": "MongoDB" if HAS_MONGODB else "Disabled",
        "debug_mode": DEBUG,
        "routers_loaded": HAS_ROUTERS
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "connected" if HAS_MONGODB and await ping_database() else "disconnected"
    return {
        "status": "healthy", 
        "version": VERSION,
        "database": db_status,
        "database_type": "MongoDB" if HAS_MONGODB else "None",
        "debug_mode": DEBUG
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint for frontend"""
    return {
        "api_status": "active",
        "authentication": "optional" if DEBUG else "required",
        "database": "connected" if HAS_MONGODB and await ping_database() else "disconnected",
        "endpoints": {
            "auth": {
                "base": f"{API_V1_STR}/auth/",
                "routes": [
                    "POST /register",
                    "POST /login", 
                    "GET /me",
                    "PUT /me",
                    "POST /logout"
                ]
            },
            "upload": {
                "base": f"{API_V1_STR}/upload/",
                "routes": [
                    "POST /",
                    "GET /",
                    "GET /{file_id}",
                    "DELETE /{file_id}",
                    "POST /{file_id}/process",
                    "GET /{file_id}/download"
                ]
            },
            "validation": {
                "base": f"{API_V1_STR}/validation/",
                "routes": [
                    "GET /status",
                    "POST /sessions",
                    "GET /sessions",
                    "GET /sessions/{session_id}",
                    "POST /sessions/{session_id}/start-validation",
                    "GET /sessions/{session_id}/interface-data",
                    "POST /sessions/{session_id}/decision",
                    "POST /validate/{session_id}",
                    "GET /results/{session_id}",
                    "GET /report/{session_id}/{format}",
                    "POST /trade-records",
                    "GET /trade-records",
                    "GET /trade-records/{trade_id}",
                    "GET /templates",
                    "POST /templates"
                ]
            }
        }
    }

# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return {
        "detail": exc.detail,
        "status_code": exc.status_code,
        "path": str(request.url.path) if hasattr(request, 'url') else "unknown"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global Exception: {type(exc).__name__} - {str(exc)}")
    return {
        "detail": "Internal server error",
        "error_type": type(exc).__name__,
        "path": str(request.url.path) if hasattr(request, 'url') else "unknown"
    }

# Handle CORS preflight requests
@app.options("/{path:path}")
async def handle_options(path: str):
    """Handle CORS preflight requests"""
    return {"message": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        log_level="info"
    ) 