# MongoDB Setup Guide for Termsheet Validation System

## Overview
This guide will help you set up MongoDB for the Termsheet Validation System without any pre-populated dummy data. You'll have complete control over what data is entered into your system.

## Prerequisites
- MongoDB installed locally OR MongoDB Atlas account (cloud)
- Python dependencies installed (`pip install -r requirements.txt`)

## Step 1: MongoDB Installation Options

### Option A: Local MongoDB Installation
1. **Download MongoDB Community Server**: https://www.mongodb.com/try/download/community
2. **Install MongoDB** following the official documentation
3. **Start MongoDB service**:
   ```bash
   # Windows
   net start MongoDB
   
   # macOS (if installed via Homebrew)
   brew services start mongodb-community
   
   # Linux
   sudo systemctl start mongod
   ```

### Option B: MongoDB Atlas (Cloud - Recommended)
1. **Create free account**: https://www.mongodb.com/cloud/atlas
2. **Create a cluster** (free tier available)
3. **Get connection string** from Atlas dashboard
4. **Whitelist your IP address**
5. **Create database user**

## Step 2: Configuration

### Environment Setup
1. **Copy environment template**:
   ```bash
   cp env_example.txt .env
   ```

2. **Update `.env` file** with your MongoDB details:

#### For Local MongoDB:
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=termsheet_validation
```

#### For MongoDB Atlas:
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=termsheet_validation
```

**Note**: Replace `username`, `password`, and `cluster` with your actual Atlas credentials.

## Step 3: Database Collections Structure

The system will create these collections automatically:

### Core Collections:
- **users** - User accounts and authentication
- **user_activities** - Activity logging and audit trail
- **uploaded_files** - File management and processing
- **reference_files** - Reference templates and documents

### Validation System:
- **master_templates** - Validation rule templates
- **validation_sessions** - Validation job tracking
- **extracted_terms** - Terms extracted from documents
- **validation_results** - Validation outcomes

### Analytics & Settings:
- **dashboard_metrics** - Performance metrics
- **session_metrics** - Session-specific analytics
- **file_metrics** - File processing statistics
- **system_audit** - System-wide audit trail
- **notification_settings** - User notification preferences
- **application_settings** - System configuration

## Step 4: Initialize Database Structure

Run the initialization script to set up empty collections:

```bash
python init_mongodb.py
```

This will:
- ✅ Connect to your MongoDB instance
- ✅ Create all necessary collections
- ✅ Set up proper indexes for performance
- ✅ **NO dummy data will be inserted**

## Step 5: Verify Setup

Check database status:
```bash
python init_mongodb.py --status
```

Expected output for empty database:
```
📊 Checking MongoDB database status...
📋 Database: termsheet_validation
--------------------------------------------------
  Users                |      0 documents
  User Activities      |      0 documents
  Uploaded Files       |      0 documents
  Reference Files      |      0 documents
  Master Templates     |      0 documents
  Validation Sessions  |      0 documents
  Extracted Terms      |      0 documents
  Validation Results   |      0 documents
  Dashboard Metrics    |      0 documents
  Session Metrics      |      0 documents
  File Metrics         |      0 documents
  System Audit         |      0 documents
  Notification Settings|      0 documents
  Application Settings |      0 documents
--------------------------------------------------
  Total                |      0 documents

✨ Database is empty and ready for manual data entry!
```

## Step 6: Start the Application

```bash
uvicorn main:app --reload
```

The application will start with:
- ✅ MongoDB connection established
- ✅ Empty database ready for use
- ✅ All API endpoints available
- ✅ Ready for user registration and data entry

## Step 7: Manual Data Entry

### Create Your First User
Use the registration API endpoint:
```bash
POST http://localhost:8000/api/auth/register
Content-Type: application/json

{
  "email": "your-email@example.com",
  "username": "yourusername",
  "full_name": "Your Full Name",
  "password": "YourSecurePassword123!",
  "confirm_password": "YourSecurePassword123!"
}
```

### Access the API Documentation
Visit: http://localhost:8000/docs

## Useful Commands

### Reset Database (Clear All Data)
```bash
python init_mongodb.py --reset
```

### Check Database Status
```bash
python init_mongodb.py --status
```

### Reinitialize Empty Structure
```bash
python init_mongodb.py
```

## Collection Indexes

Each collection has optimized indexes for performance:

- **Users**: email, username, is_active, role
- **Files**: file_id, user_id, processing_status, upload_timestamp
- **Sessions**: user_id, file_id, status, created_at
- **Metrics**: metric_name, date, period
- **Activities**: user_id, activity_type, timestamp

## Security Notes

1. **Change default settings** in production
2. **Use strong passwords** for database users
3. **Whitelist specific IPs** for Atlas connections
4. **Enable authentication** for local MongoDB
5. **Use TLS/SSL** for production connections

## Troubleshooting

### Connection Issues
- Verify MongoDB is running
- Check connection string format
- Ensure network connectivity
- Verify credentials

### Permission Issues
- Check database user permissions
- Verify IP whitelist (Atlas)
- Check firewall settings

### Performance Issues
- Monitor connection pool
- Check index usage
- Review query patterns

## Next Steps

1. **Start the application**: `uvicorn main:app --reload`
2. **Create your admin user** via the registration API
3. **Upload your first document** through the web interface
4. **Create validation templates** for your specific needs
5. **Begin validating documents** manually

Your MongoDB database is now configured and ready for manual data entry! 🚀 