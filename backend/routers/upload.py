from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from typing import List, Optional
import uuid
import os
import shutil
import time
import asyncio
from datetime import datetime
import mimetypes
from bson import ObjectId
import logging

# Internal imports
from mongodb_models import (
    User as MongoUser, 
    UploadedFile as MongoUploadedFile,
    UserActivity as MongoUserActivity
)
from mongodb_dependencies import get_current_active_user, get_current_active_user_optional
from schemas import (
    FileResponse, 
    FileListResponse,
    SuccessResponse
)

router = APIRouter(prefix="/upload", tags=["file-upload"])

# Configure file upload settings
UPLOAD_DIR = "uploaded_files"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv", ".pdf"}

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(None),
    category: str = Form("general"),
    current_user: MongoUser = Depends(get_current_active_user_optional)
):
    """Upload a file"""
    try:
        # Validate file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Create file record in MongoDB
        db_file = MongoUploadedFile(
            filename=file.filename,
            original_filename=file.filename,
            file_type=file_extension.lower(),
            file_size=len(file_content),
            file_path=file_path,
            upload_timestamp=datetime.utcnow(),
            processing_status="pending",
            progress_percentage=0,
            extracted_text=None,
            processing_time=None,
            error_message=None,
            file_hash=None,
            download_count=0,
            last_accessed=None,
            file_tags=None,
            is_reference=False,
            user_id=str(current_user.id)
        )
        
        await db_file.insert()
        
        # Start basic file processing
        try:
            # Update status to processing
            db_file.processing_status = "processing"
            db_file.progress_percentage = 50
            await db_file.save()
            
            # Basic processing: just mark as completed for now
            # In a real system, this would extract text, validate structure, etc.
            processing_start = time.time()
            
            # Simulate some processing time
            await asyncio.sleep(1)
            
            # For now, just mark as completed
            processing_time = time.time() - processing_start
            db_file.processing_status = "completed"
            db_file.progress_percentage = 100
            db_file.processing_time = processing_time
            
            # Add some mock extracted text based on file type
            if file_extension.lower() in ['.pdf', '.docx', '.doc']:
                db_file.extracted_text = f"Sample extracted text from {file.filename}"
            
            await db_file.save()
            
        except Exception as processing_error:
            logging.error(f"Error processing file: {processing_error}")
            # Mark as failed if processing fails
            db_file.processing_status = "failed"
            db_file.error_message = str(processing_error)
            await db_file.save()
        
        # Log user activity
        activity = MongoUserActivity(
            user_id=str(current_user.id),
            activity_type="file_upload",
            description=f"Uploaded file: {file.filename}",
            metadata={
                "file_id": str(db_file.id),
                "filename": file.filename,
                "file_size": len(file_content),
                "category": category
            },
            timestamp=datetime.utcnow()
        )
        await activity.insert()
        
        return FileResponse(
            id=str(db_file.id),
            filename=db_file.filename,
            original_filename=db_file.original_filename,
            file_size=db_file.file_size,
            file_extension=db_file.file_type,
            content_type=db_file.file_type,
            description="",
            category="general",
            user_id=str(db_file.user_id),
            uploaded_by=current_user.username,
            upload_date=db_file.upload_timestamp,
            is_processed=False,
            processing_status=db_file.processing_status,
            validation_report=None,
            created_at=db_file.upload_timestamp,
            updated_at=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        # Clean up file if it was created
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during file upload"
        )

@router.get("/", response_model=FileListResponse)
async def get_user_files(
    skip: int = 0,
    limit: int = 20,
    category: str = None,
    current_user: MongoUser = Depends(get_current_active_user_optional)
):
    """Get user's uploaded files"""
    try:
        # Build query
        query = {"user_id": str(current_user.id)}  # Convert ObjectId to string
        if category:
            query["category"] = category
        
        # Get files with pagination
        files = await MongoUploadedFile.find(query).skip(skip).limit(limit).to_list()
        total_count = await MongoUploadedFile.find(query).count()
        
        file_responses = []
        for file in files:
            file_responses.append(FileResponse(
                id=str(file.id),
                filename=file.filename,
                original_filename=file.original_filename,
                file_size=file.file_size,
                file_extension=file.file_type,
                content_type=file.file_type,
                description="",
                category="general",
                user_id=str(file.user_id),
                uploaded_by="",
                upload_date=file.upload_timestamp,
                is_processed=file.processing_status == "completed",
                processing_status=file.processing_status,
                validation_report=None,
                created_at=file.upload_timestamp,
                updated_at=None
            ))
        
        return FileListResponse(
            files=file_responses,
            total_count=total_count,
            page_size=limit,
            current_page=skip // limit + 1 if limit > 0 else 1
        )
        
    except Exception as e:
        logging.error(f"Error getting user files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching files"
        )

@router.get("/{file_id}", response_model=FileResponse)
async def get_file_details(
    file_id: str,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Get details of a specific file"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(file_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file ID format"
            )
        
        # Find file
        file = await MongoUploadedFile.find_one(
            MongoUploadedFile.id == ObjectId(file_id),
            MongoUploadedFile.user_id == str(current_user.id)  # Convert ObjectId to string
        )
        
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return FileResponse(
            id=str(file.id),
            filename=file.filename,
            original_filename=file.original_filename,
            file_size=file.file_size,
            file_extension=file.file_type,
            content_type=file.file_type,
            description="",
            category="general",
            user_id=str(file.user_id),
            uploaded_by="",
            upload_date=file.upload_timestamp,
            is_processed=file.processing_status == "completed",
            processing_status=file.processing_status,
            validation_report=None,
            created_at=file.upload_timestamp,
            updated_at=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting file details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching file details"
        )

@router.delete("/{file_id}", response_model=SuccessResponse)
async def delete_file(
    file_id: str,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Delete a file"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(file_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file ID format"
            )
        
        # Find file
        file = await MongoUploadedFile.find_one(
            MongoUploadedFile.id == ObjectId(file_id),
            MongoUploadedFile.user_id == str(current_user.id)  # Convert ObjectId to string
        )
        
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Delete physical file
        if os.path.exists(file.file_path):
            os.remove(file.file_path)
        
        # Delete from database
        await file.delete()
        
        # Log user activity
        activity = MongoUserActivity(
            user_id=str(current_user.id),
            activity_type="file_delete",
            description=f"Deleted file: {file.filename}",
            metadata={
                "file_id": str(file.id),
                "filename": file.filename
            },
            timestamp=datetime.utcnow()
        )
        await activity.insert()
        
        return SuccessResponse(
            message="File deleted successfully",
            data={"file_id": file_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting file"
        )

@router.post("/{file_id}/process", response_model=FileResponse)
async def process_file(
    file_id: str,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Manually trigger file processing"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(file_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file ID format"
            )
        
        # Find file
        file = await MongoUploadedFile.find_one(
            MongoUploadedFile.id == ObjectId(file_id),
            MongoUploadedFile.user_id == str(current_user.id)
        )
        
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Check if file can be processed
        if file.processing_status in ["completed", "processing"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File is already {file.processing_status}"
            )
        
        # Start processing
        file.processing_status = "processing"
        file.progress_percentage = 0
        file.error_message = None
        await file.save()
        
        try:
            # Simulate processing
            processing_start = time.time()
            
            # Update progress
            file.progress_percentage = 50
            await file.save()
            
            await asyncio.sleep(1)  # Simulate processing time
            
            # Complete processing
            processing_time = time.time() - processing_start
            file.processing_status = "completed"
            file.progress_percentage = 100
            file.processing_time = processing_time
            
            # Add mock extracted text
            if file.file_type in ['pdf', 'docx', 'doc']:
                file.extracted_text = f"Sample extracted text from {file.filename}"
            
            await file.save()
            
        except Exception as processing_error:
            logging.error(f"Error processing file {file_id}: {processing_error}")
            file.processing_status = "failed"
            file.error_message = str(processing_error)
            await file.save()
        
        # Return updated file info
        return FileResponse(
            id=str(file.id),
            filename=file.filename,
            original_filename=file.original_filename,
            file_size=file.file_size,
            file_extension=file.file_type,
            content_type=file.file_type,
            description="",
            category="general",
            user_id=str(file.user_id),
            uploaded_by="",
            upload_date=file.upload_timestamp,
            is_processed=file.processing_status == "completed",
            processing_status=file.processing_status,
            validation_report=None,
            created_at=file.upload_timestamp,
            updated_at=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error processing file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing file"
        )

@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Download a file"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(file_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file ID format"
            )
        
        # Find file
        file = await MongoUploadedFile.find_one(
            MongoUploadedFile.id == ObjectId(file_id),
            MongoUploadedFile.user_id == str(current_user.id)
        )
        
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Check if file exists on disk
        if not os.path.exists(file.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk"
            )
        
        # Update download count and last accessed
        file.download_count = (file.download_count or 0) + 1
        file.last_accessed = datetime.utcnow()
        await file.save()
        
        # Log user activity
        activity = MongoUserActivity(
            user_id=str(current_user.id),
            activity_type="file_download",
            description=f"Downloaded file: {file.filename}",
            metadata={
                "file_id": str(file.id),
                "filename": file.filename
            },
            timestamp=datetime.utcnow()
        )
        await activity.insert()
        
        # Return file
        return FileResponse(
            path=file.file_path,
            filename=file.original_filename,
            media_type=mimetypes.guess_type(file.file_path)[0] or 'application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while downloading file"
        ) 