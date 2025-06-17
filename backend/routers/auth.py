from fastapi import APIRouter, Depends, HTTPException, status
from mongodb_models import User as MongoUser
from mongodb_dependencies import get_current_user, get_current_active_user
from schemas import UserCreate, UserLogin, UserResponse, Token, SuccessResponse, UserUpdate
from auth import (
    get_password_hash, 
    authenticate_user_mongo, 
    create_user_tokens_mongo
)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user_email = await MongoUser.find_one(MongoUser.email == user_data.email)
        existing_user_username = await MongoUser.find_one(MongoUser.username == user_data.username)
        
        if existing_user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if existing_user_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = MongoUser(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False
        )
        
        await db_user.insert()
        
        return UserResponse(
            id=str(db_user.id),
            email=db_user.email,
            username=db_user.username,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            is_verified=db_user.is_verified,
            is_admin=db_user.is_admin,
            last_login=db_user.last_login,
            login_count=db_user.login_count,
            profile_picture=db_user.profile_picture,
            department=db_user.department,
            role=db_user.role,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """Authenticate user and return access token"""
    user = await authenticate_user_mongo(user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Create access token
    token_data = create_user_tokens_mongo(user)
    
    return Token(
        access_token=token_data["access_token"],
        token_type=token_data["token_type"],
        expires_in=token_data["expires_in"],
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_admin=user.is_admin,
            last_login=user.last_login,
            login_count=user.login_count,
            profile_picture=user.profile_picture,
            department=user.department,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: MongoUser = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_admin=current_user.is_admin,
        last_login=current_user.last_login,
        login_count=current_user.login_count,
        profile_picture=current_user.profile_picture,
        department=current_user.department,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Update current user information"""
    try:
        # Check if username is being updated and if it's already taken
        if user_update.username and user_update.username != current_user.username:
            existing_user = await MongoUser.find_one(
                MongoUser.username == user_update.username
            )
            
            if existing_user and str(existing_user.id) != str(current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Update user fields
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        await current_user.save()
        
        return UserResponse(
            id=str(current_user.id),
            email=current_user.email,
            username=current_user.username,
            full_name=current_user.full_name,
            is_active=current_user.is_active,
            is_verified=current_user.is_verified,
            is_admin=current_user.is_admin,
            last_login=current_user.last_login,
            login_count=current_user.login_count,
            profile_picture=current_user.profile_picture,
            department=current_user.department,
            role=current_user.role,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during update"
        )

@router.post("/logout", response_model=SuccessResponse)
async def logout_user(current_user: MongoUser = Depends(get_current_active_user)):
    """Logout user (client should remove token)"""
    return SuccessResponse(
        message="Logged out successfully"
    ) 