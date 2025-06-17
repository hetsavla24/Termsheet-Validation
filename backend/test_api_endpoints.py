#!/usr/bin/env python3
"""
Test API Endpoints
Quick test to verify trade record endpoints work correctly
"""

import asyncio
import aiohttp
import json

async def test_trade_endpoints():
    """Test the trade record API endpoints"""
    
    base_url = "http://localhost:8000/api/validation"
    
    async with aiohttp.ClientSession() as session:
        print("🔄 Testing trade record API endpoints...")
        
        # Test 1: List trade records
        print("\n1. Testing list trade records...")
        try:
            async with session.get(f"{base_url}/trade-records?skip=0&limit=50&status_filter=active") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ List endpoint working: {len(data)} records found")
                    for record in data[:3]:  # Show first 3
                        print(f"   - {record['trade_id']}: {record['counterparty']}")
                else:
                    print(f"❌ List endpoint failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ List endpoint error: {e}")
        
        # Test 2: Get specific trade record
        print("\n2. Testing get specific trade record...")
        try:
            async with session.get(f"{base_url}/trade-records/TR-2025-0420") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Get endpoint working: {data['trade_id']}")
                elif response.status == 404:
                    print("⚠️  Trade record not found (expected if no sample data)")
                else:
                    print(f"❌ Get endpoint failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ Get endpoint error: {e}")
        
        # Test 3: Test invalid trade ID
        print("\n3. Testing invalid trade ID...")
        try:
            async with session.get(f"{base_url}/trade-records/INVALID-ID") as response:
                if response.status == 404:
                    print("✅ Invalid ID correctly returns 404")
                else:
                    print(f"❌ Expected 404, got: {response.status}")
        except Exception as e:
            print(f"❌ Invalid ID test error: {e}")
        
        print("\n✅ API endpoint tests completed!")

if __name__ == "__main__":
    asyncio.run(test_trade_endpoints()) 