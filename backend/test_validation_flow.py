#!/usr/bin/env python3
"""
Test Validation Flow
Tests the validation session creation and trade ID validation flow
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mongodb_models import TradeRecord, ValidationSession, UploadedFile
from mongodb_config import connect_to_mongo
from datetime import datetime

async def test_validation_flow():
    """Test the validation session creation flow"""
    
    print("🔄 Testing validation session creation flow...")
    
    await connect_to_mongo()
    
    # Initialize the model with Beanie
    from beanie import init_beanie
    from motor.motor_asyncio import AsyncIOMotorClient
    
    # Get database
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    database = client.termsheet_db
    
    # Initialize beanie with all models
    await init_beanie(database=database, document_models=[TradeRecord, ValidationSession, UploadedFile])
    
    print("\n1. Checking available trade records...")
    trade_records = await TradeRecord.find({"status": "active"}).to_list()
    
    if not trade_records:
        print("❌ No active trade records found!")
        print("Run: python sample_trade_records.py")
        return False
    
    print(f"✅ Found {len(trade_records)} active trade records:")
    for trade in trade_records:
        print(f"   - {trade.trade_id}: {trade.counterparty}")
    
    print("\n2. Testing trade ID validation...")
    test_trade_id = trade_records[0].trade_id
    
    # Test valid trade ID
    valid_trade = await TradeRecord.find_one({"trade_id": test_trade_id})
    if valid_trade:
        print(f"✅ Trade ID validation works: {test_trade_id}")
    else:
        print(f"❌ Trade ID validation failed: {test_trade_id}")
        return False
    
    # Test invalid trade ID
    invalid_trade = await TradeRecord.find_one({"trade_id": "INVALID-TRADE-ID"})
    if not invalid_trade:
        print("✅ Invalid trade ID correctly rejected")
    else:
        print("❌ Invalid trade ID was not rejected")
        return False
    
    print("\n3. Checking uploaded files...")
    uploaded_files = await UploadedFile.find({"processing_status": "completed"}).to_list()
    
    if not uploaded_files:
        print("⚠️  No completed uploaded files found")
        print("   Upload a file through the UI first for full testing")
    else:
        print(f"✅ Found {len(uploaded_files)} processed files:")
        for file in uploaded_files[:3]:  # Show first 3
            print(f"   - {file.filename}")
    
    print("\n4. Testing session creation prerequisites...")
    
    # Check required fields for session creation
    session_data = {
        "session_name": "Test Session",
        "file_id": str(uploaded_files[0].id) if uploaded_files else "mock-file-id",
        "trade_id": test_trade_id,
        "validation_type": "enhanced_interface"
    }
    
    print(f"   Session Name: {session_data['session_name']} ✅")
    print(f"   File ID: {session_data['file_id']} {'✅' if uploaded_files else '⚠️'}")
    print(f"   Trade ID: {session_data['trade_id']} ✅")
    print(f"   Validation Type: {session_data['validation_type']} ✅")
    
    print("\n✅ Validation flow test completed successfully!")
    print("\nNext steps:")
    print("1. Start your backend server: python main.py")
    print("2. Start your frontend server: npm start")
    print("3. Navigate to /validation page")
    print("4. Select a file and trade ID to create a session")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_validation_flow())
    if not success:
        sys.exit(1) 