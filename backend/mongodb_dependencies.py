from mongodb_config import get_database
from mongodb_models import User as MongoUser
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from auth import verify_token_mongo
import logging
from bson import ObjectId
from datetime import datetime

# Mock user class for testing/development when database is unavailable
class MockUser:
    """Mock user for testing when database is not available"""
    def __init__(self):
        self.id = ObjectId()
        self.username = "devuser"
        self.email = "dev@example.com"
        self.full_name = "Development User"
        self.hashed_password = "dev_password_hash"
        self.is_active = True
        self.is_verified = True
        self.is_admin = False
        self.last_login = None
        self.login_count = 0
        self.profile_picture = None
        self.department = None
        self.role = "user"
        self.created_at = datetime.utcnow()
        self.updated_at = None
    
    async def save(self):
        """Mock save method for compatibility"""
        pass

# Security scheme
security = HTTPBearer(auto_error=False)  # Don't auto-error for missing tokens

async def get_mongo_db():
    """Get MongoDB database instance"""
    return get_database()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> MongoUser:
    """Get current authenticated user from MongoDB"""
    try:
        # Check if credentials exist
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify token and get user email
        token_data = verify_token_mongo(credentials.credentials)
        
        if not token_data or not token_data.email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Find user in MongoDB
        user = await MongoUser.find_one({"email": token_data.email})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> MongoUser:
    """Get current authenticated user from MongoDB - Optional for development"""
    try:
        if not credentials or not credentials.credentials:
            # Try to get default user from database
            try:
                default_user = await MongoUser.find_one({"email": "dev@example.com"})
                if not default_user:
                    # Create a default development user
                    default_user = MongoUser(
                        username="devuser",
                        email="dev@example.com",
                        full_name="Development User",
                        hashed_password="dev_password_hash",
                        is_active=True,
                        is_verified=True
                    )
                    await default_user.insert()
                return default_user
            except Exception:
                # If database is not available, create a mock user for testing
                return MockUser()
        
        return await get_current_user(credentials)
        
    except HTTPException:
        # If authentication fails, try database fallback
        try:
            default_user = await MongoUser.find_one({"email": "dev@example.com"})
            if not default_user:
                default_user = MongoUser(
                    username="devuser",
                    email="dev@example.com", 
                    full_name="Development User",
                    hashed_password="dev_password_hash",
                    is_active=True,
                    is_verified=True
                )
                await default_user.insert()
            return default_user
        except Exception:
            # Create mock user if database unavailable
            return MockUser()
    except Exception as e:
        logging.error(f"Error getting current user (optional): {e}")
        # Create mock user as final fallback
        try:
            default_user = await MongoUser.find_one({"email": "dev@example.com"})
            if not default_user:
                default_user = MongoUser(
                    username="devuser",
                    email="dev@example.com",
                    full_name="Development User", 
                    hashed_password="dev_password_hash",
                    is_active=True,
                    is_verified=True
                )
                await default_user.insert()
            return default_user
        except Exception:
            return MockUser()

async def get_current_active_user(current_user: MongoUser = Depends(get_current_user)) -> MongoUser:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user 

async def get_current_active_user_optional(current_user: MongoUser = Depends(get_current_user_optional)) -> MongoUser:
    """Get current active user - Optional for development"""
    if not current_user.is_active:
        # For development, allow inactive users
        current_user.is_active = True
        await current_user.save()
    return current_user