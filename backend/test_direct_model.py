#!/usr/bin/env python3
"""
Test Direct Model Access
Test if the models are properly initialized
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_direct_model_access():
    """Test direct model access to verify initialization"""
    
    print("🔄 Testing direct model access...")
    
    try:
        # Import and connect to MongoDB
        from mongodb_config import connect_to_mongo
        await connect_to_mongo()
        print("✅ MongoDB connection established")
        
        # Import the models
        from mongodb_models import TradeRecord
        print("✅ TradeRecord model imported")
        
        # Test basic query
        print("\n1. Testing TradeRecord query...")
        trade_records = await TradeRecord.find({"status": "active"}).limit(3).to_list()
        print(f"✅ Direct query successful: {len(trade_records)} records")
        for record in trade_records:
            print(f"   - {record.trade_id}: {record.counterparty}")
        
        # Test specific find_one
        print("\n2. Testing specific find_one...")
        if trade_records:
            test_id = trade_records[0].trade_id
            specific_record = await TradeRecord.find_one({"trade_id": test_id})
            if specific_record:
                print(f"✅ find_one successful: {specific_record.trade_id}")
            else:
                print("❌ find_one failed")
        
        print("\n✅ Direct model tests passed!")
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ Direct model test failed: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_direct_model_access())
    if not success:
        sys.exit(1) 