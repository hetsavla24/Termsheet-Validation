#!/usr/bin/env python3
"""
Sample Data Population Script
Populates the database with sample trade records that match the reference termsheets
"""

import asyncio
from datetime import datetime, timedelta
from mongodb_config import connect_to_mongo
from mongodb_models import TradeRecord as MongoTradeRecord

async def populate_sample_trade_records():
    """Populate database with sample trade records"""
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Sample trade records based on the reference termsheets
    sample_records = [
        {
            "trade_id": "TR-2025-0420",
            "counterparty": "HSBC Bank plc",
            "notional_amount": 25000000.0,  # Correct amount (termsheet shows discrepancy)
            "settlement_date": datetime(2025, 3, 15),
            "interest_rate": 4.25,  # Correct rate (termsheet shows discrepancy)
            "currency": "USD",
            "payment_terms": "Quarterly",
            "legal_entity": "HSBC Holdings plc London Branch",
            "trade_type": "Interest Rate Swap",
            "maturity_date": datetime(2027, 3, 15),
            "reference_rate": "SOFR + 1.50%",
            "status": "active",
            "created_by": "system"
        },
        {
            "trade_id": "TR-2025-0421",
            "counterparty": "Goldman Sachs",
            "notional_amount": 50000000.0,
            "settlement_date": datetime(2025, 3, 20),
            "interest_rate": 4.50,
            "currency": "USD",
            "payment_terms": "Quarterly",
            "legal_entity": "Goldman Sachs & Co. LLC",
            "trade_type": "Interest Rate Swap",
            "maturity_date": datetime(2027, 3, 20),
            "reference_rate": "SOFR + 1.75%",
            "status": "active",
            "created_by": "system"
        },
        {
            "trade_id": "TR-2025-0422",
            "counterparty": "JP Morgan",
            "notional_amount": 35000000.0,
            "settlement_date": datetime(2025, 3, 25),
            "interest_rate": 4.35,
            "currency": "USD",
            "payment_terms": "Quarterly",
            "legal_entity": "JPMorgan Chase Bank N.A.",
            "trade_type": "Interest Rate Swap",
            "maturity_date": datetime(2027, 3, 25),
            "reference_rate": "SOFR + 1.60%",
            "status": "active",
            "created_by": "system"
        },
        {
            "trade_id": "TR-2025-0423",
            "counterparty": "Deutsche Bank",
            "notional_amount": 40000000.0,
            "settlement_date": datetime(2025, 3, 30),
            "interest_rate": 4.40,
            "currency": "USD",
            "payment_terms": "Quarterly",
            "legal_entity": "Deutsche Bank AG",
            "trade_type": "Interest Rate Swap",
            "maturity_date": datetime(2027, 3, 30),
            "reference_rate": "SOFR + 1.65%",
            "status": "active",
            "created_by": "system"
        }
    ]
    
    # Insert sample records
    for record_data in sample_records:
        try:
            # Check if record already exists
            existing = await MongoTradeRecord.find_one({"trade_id": record_data["trade_id"]})
            if existing:
                print(f"Trade record {record_data['trade_id']} already exists, skipping...")
                continue
            
            # Create new record
            trade_record = MongoTradeRecord(**record_data)
            await trade_record.insert()
            print(f"✅ Created trade record: {record_data['trade_id']} - {record_data['counterparty']}")
            
        except Exception as e:
            print(f"❌ Error creating trade record {record_data['trade_id']}: {e}")
    
    print(f"\n✅ Sample data population completed!")

if __name__ == "__main__":
    asyncio.run(populate_sample_trade_records()) 