from decouple import config
import os

# MongoDB Configuration
MONGODB_URL = config("MONGODB_URL", default="mongodb://localhost:27017")
DATABASE_NAME = config("DATABASE_NAME", default="termsheet_validation")

# Database configuration (for legacy compatibility)
DATABASE_URL = config("DATABASE_URL", default="sqlite:///./termsheet_validation.db")

# JWT Configuration
SECRET_KEY = config("SECRET_KEY", default="your-super-secret-jwt-key-change-this-in-production")
ALGORITHM = config("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)

# Application settings
DEBUG = config("DEBUG", default=True, cast=bool)
HOST = config("HOST", default="127.0.0.1")
PORT = config("PORT", default=8000, cast=int)
ENVIRONMENT = config("ENVIRONMENT", default="development")

# File upload settings
MAX_FILE_SIZE = config("MAX_FILE_SIZE", default=16777216, cast=int)  # 16MB
MAX_FILE_SIZE_MB = config("MAX_FILE_SIZE_MB", default=16, cast=int)
UPLOAD_DIR = config("UPLOAD_DIR", default="./uploads")
UPLOAD_DIRECTORY = config("UPLOAD_DIRECTORY", default="./uploads")

# Create upload directories if they don't exist
for directory in [UPLOAD_DIR, UPLOAD_DIRECTORY, "./uploaded_files"]:
    os.makedirs(directory, exist_ok=True)

# OCR settings
TESSERACT_PATH = config("TESSERACT_PATH", default="tesseract")

# CORS settings
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    FRONTEND_URL,
]

# Email Configuration (optional)
SMTP_SERVER = config("SMTP_SERVER", default="smtp.gmail.com")
SMTP_PORT = config("SMTP_PORT", default=587, cast=int)
SMTP_USERNAME = config("SMTP_USERNAME", default="")
SMTP_PASSWORD = config("SMTP_PASSWORD", default="")

# Redis Configuration (for background tasks)
REDIS_URL = config("REDIS_URL", default="redis://localhost:6379")

# API Configuration
API_V1_STR = "/api"
PROJECT_NAME = "Termsheet Validation System"
VERSION = "3.0.0" 