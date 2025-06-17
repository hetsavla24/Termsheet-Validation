#!/usr/bin/env python3
"""
Sample Trade Records Setup
Creates sample trade records for testing the enhanced validation interface
"""

import asyncio
from datetime import datetime, timedelta
from mongodb_models import TradeRecord
from mongodb_config import connect_to_mongo

async def create_sample_trade_records():
    """Create sample trade records for testing"""
    
    await connect_to_mongo()
    
    # Initialize the model with Beanie
    from beanie import init_beanie
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    # Get database
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    database = client.termsheet_db
    
    # Initialize beanie with the TradeRecord model
    await init_beanie(database=database, document_models=[TradeRecord])
    
    sample_trades = [
        {
            "trade_id": "TR-2025-0420",
            "counterparty": "HSBC Bank",
            "notional_amount": 25000000.00,
            "settlement_date": datetime(2025, 4, 5),
            "interest_rate": 3.75,
            "currency": "USD",
            "payment_terms": "Quarterly",
            "legal_entity": "Barclays Bank PLC",
            "trade_type": "Standard",
            "reference_rate": "LIBOR",
            "created_by": "system"
        },
        {
            "trade_id": "TR-2025-0421",
            "counterparty": "Goldman Sachs",
            "notional_amount": 50000000.00,
            "settlement_date": datetime(2025, 3, 15),
            "interest_rate": 4.25,
            "currency": "USD",
            "payment_terms": "Semi-Annual",
            "legal_entity": "Barclays Bank PLC",
            "trade_type": "Premium",
            "reference_rate": "SOFR",
            "created_by": "system"
        },
        {
            "trade_id": "TR-2025-0422",
            "counterparty": "JP Morgan Chase",
            "notional_amount": 75000000.00,
            "settlement_date": datetime(2025, 5, 20),
            "interest_rate": 3.95,
            "currency": "EUR",
            "payment_terms": "Annual",
            "legal_entity": "Barclays Bank PLC",
            "trade_type": "Standard",
            "reference_rate": "EURIBOR",
            "created_by": "system"
        },
        {
            "trade_id": "TR-2025-0423",
            "counterparty": "Deutsche Bank AG",
            "notional_amount": 100000000.00,
            "settlement_date": datetime(2025, 6, 10),
            "interest_rate": 4.50,
            "currency": "GBP",
            "payment_terms": "Quarterly",
            "legal_entity": "Barclays Bank PLC",
            "trade_type": "Complex",
            "reference_rate": "SONIA",
            "created_by": "system"
        }
    ]
    
    print("Creating sample trade records...")
    
    for trade_data in sample_trades:
        try:
            # Check if trade already exists
            existing = await TradeRecord.find_one({"trade_id": trade_data["trade_id"]})
            if existing:
                print(f"Trade {trade_data['trade_id']} already exists, skipping...")
                continue
                
            # Create new trade record
            trade = TradeRecord(**trade_data)
            await trade.insert()
            print(f"✅ Created trade record: {trade_data['trade_id']} - {trade_data['counterparty']}")
            
        except Exception as e:
            print(f"❌ Error creating trade {trade_data['trade_id']}: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n✅ Sample trade records setup completed!")
    print("\nAvailable trade records for testing:")
    print("- TR-2025-0420: HSBC Bank ($25M USD)")
    print("- TR-2025-0421: Goldman Sachs ($50M USD)")  
    print("- TR-2025-0422: JP Morgan Chase (€75M EUR)")
    print("- TR-2025-0423: Deutsche Bank AG (£100M GBP)")

if __name__ == "__main__":
    asyncio.run(create_sample_trade_records()) 