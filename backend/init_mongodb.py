import asyncio
from mongodb_config import connect_to_mongo, close_mongo_connection, DATABASE_NAME
from mongodb_models import *

async def init_mongodb():
    """Initialize MongoDB with collections structure only (no sample data)"""
    
    print("🚀 Connecting to MongoDB...")
    await connect_to_mongo()
    
    try:
        print("📋 Setting up MongoDB collections and indexes...")
        
        # Initialize all collections by creating indexes
        # This ensures all collections exist with proper indexes
        collections = [
            User, UserActivity, UploadedFile, ReferenceFile,
            MasterTemplate, ValidationSession, ExtractedTerm,
            ValidationResult, DashboardMetrics, SessionMetrics,
            FileMetrics, SystemAudit, NotificationSettings, ApplicationSettings
        ]
        
        for collection in collections:
            # This will create the collection and indexes if they don't exist
            await collection.find_one()
            print(f"✅ Collection '{collection.Settings.name}' initialized")
        
        print("✅ MongoDB database structure initialized successfully!")
        print("\n📊 Database Status:")
        print("  - All collections created with proper indexes")
        print("  - Database is ready for manual data entry")
        print("  - No sample data was inserted")
        
        print(f"\n🔗 Database: {DATABASE_NAME}")
        print("🏁 Ready to accept data through the API!")
        
    except Exception as e:
        print(f"❌ Error during MongoDB initialization: {e}")
        raise
    finally:
        await close_mongo_connection()

async def reset_mongodb():
    """Reset MongoDB by dropping all collections"""
    print("⚠️  Resetting MongoDB...")
    await connect_to_mongo()
    
    try:
        print("🗑️  Dropping all collections...")
        
        # Drop all collections
        collections = [
            User, UserActivity, UploadedFile, ReferenceFile,
            MasterTemplate, ValidationSession, ExtractedTerm,
            ValidationResult, DashboardMetrics, SessionMetrics,
            FileMetrics, SystemAudit, NotificationSettings, ApplicationSettings
        ]
        
        for collection in collections:
            try:
                await collection.delete_all()
                print(f"  ✅ Cleared collection: {collection.Settings.name}")
            except Exception as e:
                print(f"  ⚠️  Collection {collection.Settings.name} was empty or doesn't exist")
        
        print("✅ All collections cleared!")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
    finally:
        await close_mongo_connection()

async def show_database_status():
    """Show current database status and collection counts"""
    print("📊 Checking MongoDB database status...")
    await connect_to_mongo()
    
    try:
        collections_info = [
            ("Users", User),
            ("User Activities", UserActivity),
            ("Uploaded Files", UploadedFile),
            ("Reference Files", ReferenceFile),
            ("Master Templates", MasterTemplate),
            ("Validation Sessions", ValidationSession),
            ("Extracted Terms", ExtractedTerm),
            ("Validation Results", ValidationResult),
            ("Dashboard Metrics", DashboardMetrics),
            ("Session Metrics", SessionMetrics),
            ("File Metrics", FileMetrics),
            ("System Audit", SystemAudit),
            ("Notification Settings", NotificationSettings),
            ("Application Settings", ApplicationSettings)
        ]
        
        print(f"\n📋 Database: {DATABASE_NAME}")
        print("-" * 50)
        
        total_documents = 0
        for name, collection in collections_info:
            count = await collection.count()
            total_documents += count
            print(f"  {name:<20} | {count:>6} documents")
        
        print("-" * 50)
        print(f"  {'Total':<20} | {total_documents:>6} documents")
        
        if total_documents == 0:
            print("\n✨ Database is empty and ready for manual data entry!")
        else:
            print(f"\n📈 Database contains {total_documents} total documents")
            
    except Exception as e:
        print(f"❌ Error checking database status: {e}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--reset":
            asyncio.run(reset_mongodb())
        elif sys.argv[1] == "--status":
            asyncio.run(show_database_status())
        else:
            print("Usage:")
            print("  python init_mongodb.py          # Initialize empty database structure")
            print("  python init_mongodb.py --reset  # Reset/clear all collections")
            print("  python init_mongodb.py --status # Show database status")
    else:
        asyncio.run(init_mongodb()) 