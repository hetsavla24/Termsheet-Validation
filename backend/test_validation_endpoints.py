#!/usr/bin/env python3
"""
Validation Endpoints Test
========================

Simple test to verify validation endpoints are working.
Tests the core validation functionality without requiring server startup.
"""

import requests
import json
import uuid
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"

# HSBC Test Data
TEST_DATA = {
    "reference_data": {
        "trade_id": "HSBC-TR-2025-0420",
        "counterparty": "HSBC Bank plc",
        "notional_amount": 50000000.00,
        "settlement_date": "2025-01-15",
        "interest_rate": 4.75,
        "currency": "USD",
        "payment_terms": "Quarterly"
    },
    "termsheet_data": {
        "counterparty": "HSBC Bank plc",
        "notional_amount": "52,500,000 USD",
        "settlement_date": "2025-01-20",
        "interest_rate": "4.85%",
        "currency": "USD",
        "payment_terms": "Monthly"
    }
}

def test_server_status():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server Status: {data.get('status', 'unknown')}")
            print(f"   Database: {data.get('database', 'unknown')}")
            print(f"   Endpoints: {len(data.get('endpoints', []))} available")
            return True
        else:
            print(f"❌ Server returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Server connection failed: {str(e)}")
        return False

def test_create_session():
    """Test creating a validation session"""
    try:
        session_data = {
            "trade_type": "Interest Rate Swap",
            "counterparty": "HSBC Bank plc"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/validation/sessions",
            json=session_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            session_id = result.get("session_id")
            print(f"✅ Session Created: {session_id}")
            return session_id
        else:
            print(f"❌ Session creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Session creation error: {str(e)}")
        return None

def test_validation_with_session(session_id):
    """Test validation with a specific session"""
    try:
        validation_request = {
            "termsheet_data": TEST_DATA["termsheet_data"],
            "reference_data": TEST_DATA["reference_data"],
            "validation_type": "comprehensive"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/validation/sessions/{session_id}/validate",
            json=validation_request,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Validation completed")
            print(f"   Status: {result.get('status', 'unknown')}")
            return result
        else:
            print(f"❌ Validation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Validation error: {str(e)}")
        return None

def test_legacy_validation():
    """Test legacy validation endpoint"""
    try:
        session_id = str(uuid.uuid4())
        validation_request = {
            "session_id": session_id,
            "termsheet_data": TEST_DATA["termsheet_data"],
            "reference_data": TEST_DATA["reference_data"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/validation/validate/{session_id}",
            json=validation_request,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Legacy validation completed")
            print(f"   Session: {session_id}")
            return result
        else:
            print(f"❌ Legacy validation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Legacy validation error: {str(e)}")
        return None

def print_validation_summary(result):
    """Print validation results summary"""
    if not result:
        return
        
    print(f"\n📊 VALIDATION RESULTS SUMMARY")
    print("-" * 50)
    
    summary = result.get("summary", {})
    if summary:
        print(f"Fields Validated:     {summary.get('total_fields_validated', 0)}")
        print(f"Passed:              {summary.get('passed_validations', 0)}")
        print(f"Critical Issues:     {summary.get('critical_issues', 0)}")
        print(f"Minor Issues:        {summary.get('minor_issues', 0)}")
        print(f"Risk Score:          {summary.get('total_risk_score', 0)}/100")
        print(f"Status:              {summary.get('overall_status', 'N/A')}")
    
    # Show key discrepancies
    validation_results = result.get("validation_results", [])
    critical_issues = [r for r in validation_results if r.get("discrepancy_type") == "critical"]
    minor_issues = [r for r in validation_results if r.get("discrepancy_type") == "minor"]
    
    if critical_issues:
        print(f"\n🚨 CRITICAL ISSUES:")
        for issue in critical_issues:
            print(f"   • {issue.get('field_name', 'Unknown')}: {issue.get('description', 'N/A')}")
    
    if minor_issues:
        print(f"\n⚠️ MINOR ISSUES:")
        for issue in minor_issues:
            print(f"   • {issue.get('field_name', 'Unknown')}: {issue.get('description', 'N/A')}")

def main():
    """Run all validation tests"""
    
    print("🧪 VALIDATION ENDPOINTS TEST")
    print("="*60)
    print("Testing HSBC termsheet validation flow")
    print("="*60)
    
    # Test 1: Server Status
    print(f"\n🔍 Test 1: Server Status Check")
    print("-" * 30)
    
    if not test_server_status():
        print("\n❌ Server is not running. Start with:")
        print("cd backend && python -m uvicorn main:app --reload --port 8000")
        return
    
    # Test 2: Create Session
    print(f"\n📝 Test 2: Create Validation Session")
    print("-" * 30)
    
    session_id = test_create_session()
    
    # Test 3: Validation with Session
    if session_id:
        print(f"\n🔄 Test 3: Run Validation")
        print("-" * 30)
        
        result = test_validation_with_session(session_id)
        if result:
            print_validation_summary(result)
    
    # Test 4: Legacy Validation
    print(f"\n🔄 Test 4: Legacy Validation Endpoint")
    print("-" * 30)
    
    legacy_result = test_legacy_validation()
    if legacy_result:
        print_validation_summary(legacy_result)
    
    print(f"\n🎉 Validation Tests Completed!")
    print("="*60)

if __name__ == "__main__":
    main() 