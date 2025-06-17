"""
Sample Term Sheet Documents Generator
Creates test documents with intentional discrepancies for validation testing
"""

import asyncio
import os
from datetime import datetime, timedelta
from mongodb_config import connect_to_mongo
from mongodb_models import UploadedFile, TradeRecord
import json

# Sample term sheet document content with intentional discrepancies
SAMPLE_TERMSHEETS = [
    {
        "filename": "HSBC_Termsheet_TR-2025-0420.txt",
        "trade_id": "TR-2025-0420",
        "content": """
TERM SHEET - DERIVATIVE TRANSACTION

Trade ID: TR-2025-0420
Date: January 15, 2025

COUNTERPARTY INFORMATION:
Primary Counterparty: HSBC Bank plc
Legal Entity: HSBC Holdings plc London Branch

TRADE DETAILS:
Notional Amount: $30,000,000 USD  [DISCREPANCY: Should be $25M]
Settlement Date: March 15, 2025
Interest Rate: 4.75% per annum  [DISCREPANCY: Should be 4.25%]
Currency: USD
Payment Terms: Quarterly payments in arrears
Reference Rate: SOFR + 1.50%

PRODUCT SPECIFICATIONS:
Trade Type: Interest Rate Swap
Maturity Date: March 15, 2027
Day Count Convention: ACT/360
Business Day Convention: Modified Following

REGULATORY INFORMATION:
MiFID II Classification: Professional Client
FCA Regulated: Yes
SEC Registration: N/A (Non-US Entity)

CONFIRMATION:
This term sheet is subject to final documentation and credit approval.
All terms are indicative and subject to change.

Document Version: 1.2
Last Updated: January 15, 2025
        """,
        "expected_discrepancies": [
            {"field": "notional_amount", "expected": 25000000, "found": 30000000, "severity": "critical"},
            {"field": "interest_rate", "expected": 4.25, "found": 4.75, "severity": "minor"}
        ]
    },
    
    {
        "filename": "Goldman_Termsheet_TR-2025-0421.txt", 
        "trade_id": "TR-2025-0421",
        "content": """
DERIVATIVE TRANSACTION TERM SHEET

Reference: TR-2025-0421
Execution Date: January 16, 2025

PARTIES:
Counterparty: Goldman Sachs International  [DISCREPANCY: Should be Goldman Sachs]
Legal Entity: Goldman Sachs Group Inc.

COMMERCIAL TERMS:
Principal Amount: $50,000,000 USD  [CORRECT]
Value Date: April 1, 2025  [DISCREPANCY: Should be March 20, 2025]
Fixed Rate: 3.85% p.a.
Currency: United States Dollar
Payment Frequency: Semi-annual  [DISCREPANCY: Should be Monthly]
Floating Rate: SOFR

PRODUCT DETAILS:
Transaction Type: Interest Rate Swap
Final Maturity: April 1, 2030
Reset Frequency: Monthly
Calculation Agent: Goldman Sachs

DOCUMENTATION:
Master Agreement: 2002 ISDA Master Agreement
Credit Support: CSA dated March 2024
Governing Law: New York State Law

REGULATORY COMPLIANCE:
Dodd-Frank: Applicable
CFTC Reporting: Required
Trade Repository: DTCC

Prepared by: Goldman Sachs Risk Management
Date: January 16, 2025
        """,
        "expected_discrepancies": [
            {"field": "counterparty", "expected": "Goldman Sachs", "found": "Goldman Sachs International", "severity": "minor"},
            {"field": "settlement_date", "expected": "2025-03-20", "found": "2025-04-01", "severity": "critical"},
            {"field": "payment_terms", "expected": "Monthly", "found": "Semi-annual", "severity": "critical"}
        ]
    },

    {
        "filename": "JPMorgan_Termsheet_TR-2025-0422.txt",
        "trade_id": "TR-2025-0422", 
        "content": """
JP MORGAN CHASE - TRANSACTION CONFIRMATION

Transaction Reference: TR-2025-0422
Trade Date: January 17, 2025

COUNTERPARTY DETAILS:
Institution: JP Morgan Chase Bank N.A.  [CORRECT]
Legal Entity: JPMorgan Chase & Co.

FINANCIAL TERMS:
Notional Principal: EUR 75,000,000  [CORRECT]
Effective Date: February 28, 2025
Rate: 3.20% per annum  [DISCREPANCY: Should be 3.50%]
Currency: EUR  [CORRECT]
Payment Terms: Quarterly payments  [CORRECT]
Base Currency: Euro

SWAP SPECIFICATIONS:
Product: Plain Vanilla Interest Rate Swap
Termination Date: February 28, 2028
Fixed Rate Payer: JP Morgan Chase
Floating Rate Payer: Counterparty
Day Count: 30/360

RISK MANAGEMENT:
Credit Rating: A+ (S&P)
Exposure Limit: EUR 100,000,000
Collateral: EUR 15,000,000
Mark-to-Market: Daily

LEGAL FRAMEWORK:
ISDA Master Agreement: 2002 Version
CSA: Standard Credit Support Annex
Jurisdiction: English Law
Dispute Resolution: London Court of International Arbitration

Status: Pending Final Confirmation
Version: 2.1
        """,
        "expected_discrepancies": [
            {"field": "interest_rate", "expected": 3.50, "found": 3.20, "severity": "minor"}
        ]
    },

    {
        "filename": "Deutsche_Termsheet_TR-2025-0423.txt",
        "trade_id": "TR-2025-0423",
        "content": """
DEUTSCHE BANK AG - DERIVATIVE CONFIRMATION

Contract ID: TR-2025-0423
Issue Date: January 18, 2025

COUNTERPARTY:
Name: Deutsche Bank Aktiengesellschaft  [DISCREPANCY: Should be Deutsche Bank AG]
Entity: Deutsche Bank AG London

TRANSACTION SUMMARY:
Notional Amount: GBP 100,000,000  [CORRECT]
Trade Date: January 18, 2025
Settlement Date: May 15, 2025  [DISCREPANCY: Should be April 10, 2025]
Interest Rate: 4.40% annually  [DISCREPANCY: Should be 4.10%]
Currency: British Pound Sterling  [CORRECT]
Payment Terms: Bi-annual payments  [DISCREPANCY: Should be Quarterly]
Benchmark Rate: SONIA + 200bps

INSTRUMENT DETAILS:
Type: Cross-Currency Interest Rate Swap
Maturity: May 15, 2030
Reset Dates: Quarterly
Payment Dates: Semi-annually
Business Day Rule: Following

CREDIT TERMS:
Credit Rating: AA- (Fitch)
Minimum Transfer Amount: GBP 1,000,000
Threshold: GBP 50,000,000
Independent Amount: GBP 25,000,000

REGULATORY:
MiFID II: Large Financial Counterparty
PRA Supervision: Yes
BaFin Regulated: Yes
EMIR Reporting: Required

Document Control: DB-2025-0118-001
Approval Status: Pending Legal Review
        """,
        "expected_discrepancies": [
            {"field": "counterparty", "expected": "Deutsche Bank AG", "found": "Deutsche Bank Aktiengesellschaft", "severity": "minor"},
            {"field": "settlement_date", "expected": "2025-04-10", "found": "2025-05-15", "severity": "critical"},
            {"field": "interest_rate", "expected": 4.10, "found": 4.40, "severity": "minor"},
            {"field": "payment_terms", "expected": "Quarterly", "found": "Bi-annual", "severity": "critical"}
        ]
    }
]

# Reference validation files
REFERENCE_FILES = [
    {
        "filename": "validation_rules_reference.json",
        "content": {
            "validation_rules": {
                "notional_amount": {
                    "tolerance": 0.05,
                    "critical_threshold": 0.10,
                    "data_type": "numeric"
                },
                "interest_rate": {
                    "tolerance": 0.25,
                    "critical_threshold": 0.50,
                    "data_type": "numeric"
                },
                "settlement_date": {
                    "tolerance": 5,
                    "critical_threshold": 14,
                    "data_type": "date"
                },
                "counterparty": {
                    "exact_match": False,
                    "similarity_threshold": 0.85,
                    "data_type": "string"
                },
                "currency": {
                    "exact_match": True,
                    "data_type": "string"
                },
                "payment_terms": {
                    "allowed_variations": ["Monthly", "Quarterly", "Semi-annual", "Annual"],
                    "data_type": "categorical"
                }
            },
            "risk_scoring": {
                "critical_discrepancy": 25,
                "minor_discrepancy": 10,
                "warning": 5,
                "max_score": 100
            }
        }
    },
    
    {
        "filename": "compliance_reference.json",
        "content": {
            "mifid_ii_requirements": {
                "professional_client": ["suitability_assessment", "best_execution", "product_governance"],
                "retail_client": ["appropriateness_test", "execution_policy", "costs_disclosure"],
                "eligible_counterparty": ["limited_protections", "execution_venue"]
            },
            "fca_regulations": {
                "conduct_rules": ["fair_treatment", "conflict_management", "clear_communication"],
                "prudential_rules": ["capital_requirements", "liquidity_ratios", "risk_management"]
            },
            "sec_requirements": {
                "registration": ["investment_adviser", "broker_dealer", "clearing_agency"],
                "reporting": ["form_adv", "form_bd", "suspicious_activity"]
            }
        }
    }
]

async def create_sample_documents():
    """Create sample term sheet documents and reference files"""
    
    await connect_to_mongo()
    
    # Initialize Beanie
    from beanie import init_beanie
    from motor.motor_asyncio import AsyncIOMotorClient
    
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    database = client.termsheet_db
    await init_beanie(database=database, document_models=[UploadedFile, TradeRecord])
    
    print("Creating sample term sheet documents and reference files...")
    
    # Create uploads directory
    os.makedirs("../uploads/samples", exist_ok=True)
    os.makedirs("../uploads/reference", exist_ok=True)
    
    # Create term sheet documents
    for doc in SAMPLE_TERMSHEETS:
        # Write document to file
        file_path = f"../uploads/samples/{doc['filename']}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(doc['content'])
        
        # Create database record
        try:
            existing = await UploadedFile.find_one({"filename": doc['filename']})
            if existing:
                print(f"Document {doc['filename']} already exists, skipping...")
                continue
                
            uploaded_file = UploadedFile(
                filename=doc['filename'],
                original_filename=doc['filename'],
                file_type="text/plain",
                file_size=len(doc['content']),
                file_path=file_path,
                extracted_text=doc['content'],
                processing_status="completed",
                progress_percentage=100,
                user_id="test_user",
                file_tags=["sample", "test", "validation"]
            )
            
            await uploaded_file.insert()
            print(f"✅ Created document: {doc['filename']}")
            
            # Print expected discrepancies for testing reference
            print(f"   Expected discrepancies for {doc['trade_id']}:")
            for disc in doc['expected_discrepancies']:
                print(f"   - {disc['field']}: Expected {disc['expected']}, Found {disc['found']} ({disc['severity']})")
                
        except Exception as e:
            print(f"❌ Error creating document {doc['filename']}: {e}")
    
    # Create reference files
    for ref_file in REFERENCE_FILES:
        file_path = f"../uploads/reference/{ref_file['filename']}"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(ref_file['content'], f, indent=2)
        
        print(f"✅ Created reference file: {ref_file['filename']}")
    
    print("\n✅ Sample documents and reference files created successfully!")
    print("\nTest Validation Scenarios:")
    print("1. HSBC (TR-2025-0420): Notional amount and interest rate discrepancies")
    print("2. Goldman Sachs (TR-2025-0421): Counterparty name, settlement date, and payment terms discrepancies") 
    print("3. JP Morgan (TR-2025-0422): Minor interest rate discrepancy")
    print("4. Deutsche Bank (TR-2025-0423): Multiple discrepancies including critical ones")
    
    print("\nFiles created in:")
    print("- Sample documents: uploads/samples/")
    print("- Reference files: uploads/reference/")

if __name__ == "__main__":
    asyncio.run(create_sample_documents()) 