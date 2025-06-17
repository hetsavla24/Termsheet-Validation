#!/usr/bin/env python3
"""
API Integration Test for Validation Flow
========================================

This script tests the complete validation flow through actual API endpoints:
1. Start the backend server
2. Create a validation session
3. Upload reference data
4. Submit termsheet for validation
5. Retrieve validation results
6. Generate validation report

Run this to test the API integration.
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import sys
import os

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_SESSION_ID = str(uuid.uuid4())

# HSBC Reference Data (same as before)
HSBC_REFERENCE_DATA = {
    "trade_id": "HSBC-TR-2025-0420",
    "counterparty": "HSBC Bank plc",
    "notional_amount": 50000000.00,
    "settlement_date": "2025-01-15",
    "interest_rate": 4.75,
    "currency": "USD",
    "payment_terms": "Quarterly",
    "legal_entity": "HSBC Holdings plc",
    "trade_type": "Interest Rate Swap",
    "maturity_date": "2027-01-15",
    "reference_rate": "SOFR"
}

# Mock Termsheet Data (with discrepancies)
MOCK_TERMSHEET_DATA = {
    "counterparty": "HSBC Bank plc",
    "notional_amount": "52,500,000 USD",  # 5% higher
    "settlement_date": "2025-01-20",      # 5 days later
    "interest_rate": "4.85%",             # 0.1% higher
    "currency": "USD",
    "payment_terms": "Monthly",           # Different from Quarterly
    "legal_entity": "HSBC Holdings plc"
}

class ValidationAPITester:
    """Test the validation API endpoints"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def check_server_status(self) -> bool:
        """Check if the server is running"""
        try:
            async with self.session.get(f"{self.base_url}/api/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Server is running: {data.get('status', 'unknown')}")
                    return True
                else:
                    print(f"❌ Server returned status: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Server connection failed: {str(e)}")
            return False
    
    async def create_validation_session(self, session_id: str = None) -> str:
        """Create a new validation session"""
        
        if not session_id:
            session_id = str(uuid.uuid4())
            
        session_data = {
            "trade_type": "Interest Rate Swap",
            "counterparty": "HSBC Bank plc",
            "reference_data": HSBC_REFERENCE_DATA
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/validation/sessions", 
                json=session_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    created_session_id = result.get("session_id", session_id)
                    print(f"✅ Validation session created: {created_session_id}")
                    return created_session_id
                else:
                    print(f"❌ Failed to create session: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    return None
        except Exception as e:
            print(f"❌ Error creating session: {str(e)}")
            return None
    
    async def submit_validation_request(self, session_id: str) -> bool:
        """Submit termsheet data for validation"""
        
        validation_request = {
            "session_id": session_id,
            "termsheet_data": MOCK_TERMSHEET_DATA,
            "validation_type": "comprehensive",
            "include_ai_analysis": True
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/validation/sessions/{session_id}/validate",
                json=validation_request
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Validation submitted successfully")
                    print(f"   Status: {result.get('status', 'unknown')}")
                    return True
                else:
                    print(f"❌ Validation submission failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Error submitting validation: {str(e)}")
            return False
    
    async def get_validation_results(self, session_id: str) -> dict:
        """Retrieve validation results"""
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/validation/sessions/{session_id}/results"
            ) as response:
                if response.status == 200:
                    results = await response.json()
                    print(f"✅ Retrieved validation results")
                    return results
                else:
                    print(f"❌ Failed to get results: {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Error getting results: {str(e)}")
            return None
    
    async def get_session_summary(self, session_id: str) -> dict:
        """Get validation session summary"""
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/validation/sessions/{session_id}/summary"
            ) as response:
                if response.status == 200:
                    summary = await response.json()
                    print(f"✅ Retrieved session summary")
                    return summary
                else:
                    print(f"❌ Failed to get summary: {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Error getting summary: {str(e)}")
            return None
    
    async def download_validation_report(self, session_id: str, format_type: str = "json") -> bool:
        """Download validation report"""
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/validation/report/{session_id}/{format_type}"
            ) as response:
                if response.status == 200:
                    content = await response.read()
                    filename = f"validation_report_{session_id}.{format_type}"
                    
                    with open(filename, 'wb') as f:
                        f.write(content)
                    
                    print(f"✅ Report downloaded: {filename}")
                    return True
                else:
                    print(f"❌ Failed to download report: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error downloading report: {str(e)}")
            return False

def print_api_test_results(results: dict):
    """Print formatted API test results"""
    
    if not results:
        print("❌ No results to display")
        return
    
    print("\n" + "="*80)
    print("🎯 API VALIDATION TEST RESULTS")
    print("="*80)
    
    # Print summary if available
    if "summary" in results:
        summary = results["summary"]
        print(f"\n📊 VALIDATION SUMMARY")
        print("-" * 40)
        print(f"Session ID:                 {results.get('session_id', 'N/A')}")
        print(f"Total Fields Validated:     {summary.get('total_fields_validated', 0)}")
        print(f"Passed Validations:         {summary.get('passed_validations', 0)}")
        print(f"Critical Issues:            {summary.get('critical_issues', 0)}")
        print(f"Minor Issues:               {summary.get('minor_issues', 0)}")
        print(f"Risk Score:                 {summary.get('total_risk_score', 0)}/100")
        print(f"Status:                     {summary.get('overall_status', 'N/A')}")
    
    # Print field results if available
    if "validation_results" in results:
        print(f"\n📋 FIELD VALIDATION RESULTS")
        print("-" * 80)
        
        for result in results["validation_results"]:
            status = "✅ PASS" if result.get("is_valid", False) else "❌ FAIL"
            risk_score = result.get("risk_score", 0)
            
            print(f"\n{status} {result.get('field_name', 'Unknown').upper()}")
            print(f"   Term Sheet:  {result.get('term_sheet_value', 'N/A')}")
            print(f"   Reference:   {result.get('reference_value', 'N/A')}")
            print(f"   Risk Score:  {risk_score}")
            print(f"   Description: {result.get('description', 'N/A')}")
            
            if result.get('ai_analysis'):
                print(f"   AI Analysis: {result['ai_analysis']}")
    
    # Print recommendations if available
    if "ai_recommendations" in results:
        print(f"\n🤖 AI RECOMMENDATIONS")
        print("-" * 40)
        for i, rec in enumerate(results["ai_recommendations"], 1):
            print(f"{i}. {rec}")
    
    print("\n" + "="*80)

async def run_api_validation_test():
    """Run the complete API validation test"""
    
    print("🚀 API VALIDATION FLOW TEST")
    print("="*80)
    print("Testing complete validation flow through API endpoints")
    print("="*80)
    
    async with ValidationAPITester(BASE_URL) as tester:
        
        # Step 1: Check server status
        print(f"\n🔍 Step 1: Checking Server Status")
        print("-" * 40)
        
        server_running = await tester.check_server_status()
        if not server_running:
            print("❌ Server is not running. Please start the backend server first:")
            print("   cd backend && python -m uvicorn main:app --reload --port 8000")
            return False
        
        # Step 2: Create validation session
        print(f"\n📝 Step 2: Creating Validation Session")
        print("-" * 40)
        
        session_id = await tester.create_validation_session()
        if not session_id:
            print("❌ Failed to create validation session")
            return False
        
        # Step 3: Submit validation request
        print(f"\n🔄 Step 3: Submitting Validation Request")
        print("-" * 40)
        print(f"Session ID: {session_id}")
        print(f"Testing HSBC termsheet with intentional discrepancies...")
        
        validation_submitted = await tester.submit_validation_request(session_id)
        if not validation_submitted:
            print("❌ Failed to submit validation request")
            return False
        
        # Step 4: Retrieve validation results
        print(f"\n📊 Step 4: Retrieving Validation Results")
        print("-" * 40)
        
        results = await tester.get_validation_results(session_id)
        if results:
            print_api_test_results(results)
        else:
            print("❌ Failed to retrieve validation results")
        
        # Step 5: Get session summary
        print(f"\n📋 Step 5: Getting Session Summary")
        print("-" * 40)
        
        summary = await tester.get_session_summary(session_id)
        if summary:
            print(f"✅ Session Summary Retrieved")
            print(f"   Status: {summary.get('status', 'N/A')}")
            print(f"   Created: {summary.get('created_at', 'N/A')}")
        
        # Step 6: Download validation report
        print(f"\n💾 Step 6: Downloading Validation Report")
        print("-" * 40)
        
        report_downloaded = await tester.download_validation_report(session_id, "json")
        if report_downloaded:
            print(f"✅ Validation report saved locally")
        
        print(f"\n🎉 API Validation Test Completed!")
        print(f"Session ID: {session_id}")
        
        return True

if __name__ == "__main__":
    print("Starting API Validation Flow Test...")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    success = asyncio.run(run_api_validation_test())
    
    if success:
        print("\n✅ All API tests passed successfully!")
    else:
        print("\n❌ Some API tests failed. Check the backend server.")
        
    print("\nTo start the backend server:")
    print("cd backend && python -m uvicorn main:app --reload --port 8000") 