import asyncio
from datetime import datetime
from mongodb_config import connect_to_mongo, close_mongo_connection
from mongodb_models import User as MongoUser, MasterTemplate as MongoMasterTemplate
from auth import get_password_hash

async def create_sample_data():
    """Create sample user and templates for testing"""
    await connect_to_mongo()
    
    try:
        # Create admin user
        admin_user = MongoUser(
            email="admin@termsheet.com",
            username="admin",
            full_name="System Administrator",
            hashed_password=get_password_hash("Admin123!"),
            is_active=True,
            is_verified=True,
            is_admin=True,
            created_at=datetime.utcnow()
        )
        await admin_user.insert()
        print(f"✅ Created admin user: {admin_user.email}")
        
        # Create sample templates
        template1 = MongoMasterTemplate(
            template_name="Standard Term Sheet Validation",
            description="Standard validation rules for basic term sheets",
            validation_rules=[
                {
                    "field_name": "Company Name",
                    "rule_type": "required",
                    "validation_criteria": {"type": "string", "min_length": 1}
                },
                {
                    "field_name": "Valuation",
                    "rule_type": "numeric",
                    "validation_criteria": {"type": "number", "min": 1000000, "max": 1000000000}
                },
                {
                    "field_name": "Investment Amount",
                    "rule_type": "numeric",
                    "validation_criteria": {"type": "number", "min": 100000, "max": 100000000}
                },
                {
                    "field_name": "Liquidation Preference",
                    "rule_type": "percentage",
                    "validation_criteria": {"type": "percentage", "min": 1.0, "max": 3.0}
                }
            ],
            is_active=True,
            usage_count=0,
            created_by="admin",
            created_at=datetime.utcnow()
        )
        await template1.insert()
        print(f"✅ Created template: {template1.template_name}")
        
        template2 = MongoMasterTemplate(
            template_name="Series A Validation Rules",
            description="Validation rules specific to Series A funding rounds",
            validation_rules=[
                {
                    "field_name": "Company Name",
                    "rule_type": "required",
                    "validation_criteria": {"type": "string", "min_length": 1}
                },
                {
                    "field_name": "Pre-Money Valuation",
                    "rule_type": "numeric",
                    "validation_criteria": {"type": "number", "min": 5000000, "max": 50000000}
                },
                {
                    "field_name": "Investment Amount",
                    "rule_type": "numeric",
                    "validation_criteria": {"type": "number", "min": 1000000, "max": 20000000}
                },
                {
                    "field_name": "Post-Money Valuation",
                    "rule_type": "numeric",
                    "validation_criteria": {"type": "number", "min": 6000000, "max": 70000000}
                },
                {
                    "field_name": "Option Pool",
                    "rule_type": "percentage",
                    "validation_criteria": {"type": "percentage", "min": 10.0, "max": 25.0}
                }
            ],
            is_active=True,
            usage_count=0,
            created_by="admin",
            created_at=datetime.utcnow()
        )
        await template2.insert()
        print(f"✅ Created template: {template2.template_name}")
        
        print("\n✅ Sample data created successfully!")
        print("Admin credentials:")
        print("  Email: admin@termsheet.com")
        print("  Password: Admin123!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_sample_data()) 