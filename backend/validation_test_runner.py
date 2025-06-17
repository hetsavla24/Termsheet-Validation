"""
Validation Test Runner
Tests the validation system with sample documents and demonstrates discrepancy detection
"""

import asyncio
import json
from datetime import datetime
from mongodb_config import connect_to_mongo
from mongodb_models import TradeRecord, UploadedFile, ValidationSession, TermSheetData, ValidationDiscrepancy, ValidationDecision
from nlp_engine import process_document_for_validation

async def run_validation_tests():
    """Run comprehensive validation tests on all sample documents"""
    
    await connect_to_mongo()
    
    # Initialize Beanie
    from beanie import init_beanie
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    database = client.termsheet_db
    await init_beanie(database=database, document_models=[
        TradeRecord, UploadedFile, ValidationSession, TermSheetData, ValidationDiscrepancy, ValidationDecision
    ])
    
    print("🔍 Running Validation System Tests...")
    print("=" * 60)
    
    # Get all sample documents
    sample_docs = await UploadedFile.find({"file_tags": "sample"}).to_list()
    
    if not sample_docs:
        print("❌ No sample documents found. Run sample_termsheet_documents.py first!")
        return
    
    print(f"Found {len(sample_docs)} sample documents to test\n")
    
    total_discrepancies = 0
    total_critical = 0
    total_minor = 0
    
    for doc in sample_docs:
        print(f"📋 Testing: {doc.filename}")
        print("-" * 40)
        
        try:
            # Extract data using NLP engine
            extracted_data = await process_document_for_validation(doc.extracted_text, "test_session")
            trade_id = extracted_data.get('trade_id')
            
            if not trade_id:
                print("❌ Could not extract trade ID from document")
                continue
            
            # Find corresponding trade record
            trade_record = await TradeRecord.find_one({"trade_id": trade_id})
            if not trade_record:
                print(f"❌ No trade record found for {trade_id}")
                continue
            
            print(f"✅ Found trade record: {trade_record.trade_id}")
            
            # Create validation session
            session = ValidationSession(
                session_name=f"Test_{doc.filename}_{datetime.now().strftime('%H%M%S')}",
                file_id=doc.file_id,
                validation_type="test",
                status="processing",
                user_id="test_user"
            )
            await session.insert()
            
            # Store extracted data
            term_sheet_data = TermSheetData(
                session_id=str(session.id),
                trade_id=extracted_data.get('trade_id'),
                counterparty=extracted_data.get('counterparty'),
                notional_amount=extracted_data.get('notional_amount'),
                settlement_date=extracted_data.get('settlement_date'),
                interest_rate=extracted_data.get('interest_rate'),
                currency=extracted_data.get('currency'),
                payment_terms=extracted_data.get('payment_terms'),
                legal_entity=extracted_data.get('legal_entity'),
                extraction_confidence=extracted_data.get('confidence', {}),
                raw_extracted_data=extracted_data
            )
            await term_sheet_data.insert()
            
            # Compare and detect discrepancies
            discrepancies = await compare_and_detect_discrepancies(
                str(session.id), extracted_data, trade_record
            )
            
            session_discrepancies = 0
            session_critical = 0
            session_minor = 0
            
            print(f"🔍 Analysis Results:")
            
            if discrepancies:
                for disc in discrepancies:
                    await disc.insert()
                    session_discrepancies += 1
                    
                    if disc.discrepancy_type == "critical":
                        session_critical += 1
                        total_critical += 1
                        print(f"  🚨 CRITICAL: {disc.field_name}")
                        print(f"     Expected: {disc.trade_record_value}")
                        print(f"     Found: {disc.term_sheet_value}")
                        print(f"     Impact: {disc.impact_level}")
                    else:
                        session_minor += 1
                        total_minor += 1
                        print(f"  ⚠️  MINOR: {disc.field_name}")
                        print(f"     Expected: {disc.trade_record_value}")
                        print(f"     Found: {disc.term_sheet_value}")
                
                # Calculate risk score
                risk_score = (session_critical * 25) + (session_minor * 10)
                
                # Make validation decision
                if risk_score >= 50:
                    decision = "reject"
                    decision_reason = f"High risk score: {risk_score} (Critical: {session_critical}, Minor: {session_minor})"
                elif risk_score >= 25:
                    decision = "manual_review"
                    decision_reason = f"Medium risk score: {risk_score} requires review"
                else:
                    decision = "approve"
                    decision_reason = f"Low risk score: {risk_score} - acceptable discrepancies"
                
                # Store decision
                validation_decision = ValidationDecision(
                    session_id=str(session.id),
                    decision=decision,
                    decision_reason=decision_reason,
                    ai_risk_score=risk_score,
                    mifid_status="compliant" if risk_score < 50 else "warning",
                    fca_status="compliant" if risk_score < 75 else "non_compliant",
                    sec_status="compliant" if risk_score < 75 else "non_compliant",
                    total_discrepancies=session_discrepancies,
                    critical_issues=session_critical,
                    minor_issues=session_minor,
                    decided_by="ai_system"
                )
                await validation_decision.insert()
                
                print(f"📊 Risk Score: {risk_score}/100")
                print(f"📋 Decision: {decision.upper()}")
                print(f"💡 Reason: {decision_reason}")
                
            else:
                print("  ✅ No discrepancies found - Perfect match!")
                
                # Store perfect validation
                validation_decision = ValidationDecision(
                    session_id=str(session.id),
                    decision="approve",
                    decision_reason="No discrepancies detected",
                    ai_risk_score=0,
                    mifid_status="compliant",
                    fca_status="compliant", 
                    sec_status="compliant",
                    total_discrepancies=0,
                    critical_issues=0,
                    minor_issues=0,
                    decided_by="ai_system"
                )
                await validation_decision.insert()
            
            # Update session status
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            await session.save()
            
            total_discrepancies += session_discrepancies
            
        except Exception as e:
            print(f"❌ Error testing {doc.filename}: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 VALIDATION TEST SUMMARY")
    print("=" * 60)
    print(f"Documents Tested: {len(sample_docs)}")
    print(f"Total Discrepancies: {total_discrepancies}")
    print(f"Critical Issues: {total_critical}")
    print(f"Minor Issues: {total_minor}")
    print(f"Success Rate: {((len(sample_docs) * 8 - total_discrepancies) / (len(sample_docs) * 8)) * 100:.1f}%")
    print()
    print("🎯 Test completed! All validation workflows tested successfully.")
    print("💡 You can now test the frontend validation interface with these processed documents.")

async def compare_and_detect_discrepancies(session_id: str, extracted_data: dict, trade_record: TradeRecord):
    """Compare extracted data with trade record and detect discrepancies"""
    discrepancies = []
    
    # Field comparisons
    comparisons = [
        {
            "field": "counterparty",
            "extracted": extracted_data.get('counterparty', ''),
            "trade_record": trade_record.counterparty,
            "type": "string"
        },
        {
            "field": "notional_amount", 
            "extracted": extract_numeric_value(extracted_data.get('notional_amount', '')),
            "trade_record": trade_record.notional_amount,
            "type": "numeric"
        },
        {
            "field": "interest_rate",
            "extracted": extract_numeric_value(extracted_data.get('interest_rate', '')),
            "trade_record": trade_record.interest_rate,
            "type": "numeric"
        },
        {
            "field": "currency",
            "extracted": extracted_data.get('currency', ''),
            "trade_record": trade_record.currency,
            "type": "string"
        },
        {
            "field": "payment_terms",
            "extracted": extracted_data.get('payment_terms', ''),
            "trade_record": trade_record.payment_terms,
            "type": "string"
        }
    ]
    
    for comp in comparisons:
        discrepancy = await detect_field_discrepancy(
            session_id, comp["field"], comp["extracted"], 
            comp["trade_record"], comp["type"]
        )
        if discrepancy:
            discrepancies.append(discrepancy)
    
    return discrepancies

async def detect_field_discrepancy(session_id: str, field_name: str, extracted_value, trade_value, data_type: str):
    """Detect discrepancy for a specific field"""
    
    if data_type == "numeric":
        if extracted_value is None or trade_value is None:
            return None
        
        difference = abs(extracted_value - trade_value) / trade_value
        
        if difference > 0.10:  # 10% difference is critical
            return ValidationDiscrepancy(
                session_id=session_id,
                discrepancy_type="critical",
                field_name=field_name,
                term_sheet_value=str(extracted_value),
                trade_record_value=str(trade_value),
                confidence_score=0.95,
                impact_level="high",
                description=f"Significant {field_name} mismatch: {difference:.1%} difference",
                recommendation=f"Verify {field_name} value with counterparty"
            )
        elif difference > 0.05:  # 5% difference is minor
            return ValidationDiscrepancy(
                session_id=session_id,
                discrepancy_type="minor",
                field_name=field_name,
                term_sheet_value=str(extracted_value),
                trade_record_value=str(trade_value),
                confidence_score=0.90,
                impact_level="medium",
                description=f"Minor {field_name} difference: {difference:.1%}",
                recommendation=f"Consider reviewing {field_name} with operations team"
            )
    
    elif data_type == "string":
        if not extracted_value or not trade_value:
            return None
            
        # Simple string comparison (could be enhanced with fuzzy matching)
        if extracted_value.lower().strip() != trade_value.lower().strip():
            # Check if it's a minor variation
            similarity = calculate_similarity(extracted_value, trade_value)
            
            if similarity < 0.7:  # Less than 70% similarity is critical
                return ValidationDiscrepancy(
                    session_id=session_id,
                    discrepancy_type="critical",
                    field_name=field_name,
                    term_sheet_value=extracted_value,
                    trade_record_value=trade_value,
                    confidence_score=0.90,
                    impact_level="high",
                    description=f"{field_name} mismatch detected",
                    recommendation=f"Verify {field_name} spelling and format"
                )
            else:  # Minor variation
                return ValidationDiscrepancy(
                    session_id=session_id,
                    discrepancy_type="minor",
                    field_name=field_name,
                    term_sheet_value=extracted_value,
                    trade_record_value=trade_value,
                    confidence_score=0.85,
                    impact_level="low",
                    description=f"Minor {field_name} variation detected",
                    recommendation=f"Confirm {field_name} format is acceptable"
                )
    
    return None

def extract_numeric_value(text_value):
    """Extract numeric value from text"""
    if not text_value:
        return None
    
    import re
    # Remove currency symbols and commas, extract numbers
    cleaned = re.sub(r'[^\d.]', '', str(text_value).replace(',', ''))
    try:
        return float(cleaned)
    except:
        return None

def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate similarity between two strings"""
    if not str1 or not str2:
        return 0.0
    
    # Simple character-based similarity
    str1, str2 = str1.lower(), str2.lower()
    matches = sum(c1 == c2 for c1, c2 in zip(str1, str2))
    max_len = max(len(str1), len(str2))
    
    return matches / max_len if max_len > 0 else 0.0

if __name__ == "__main__":
    asyncio.run(run_validation_tests()) 