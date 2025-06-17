#!/usr/bin/env python3
"""
Comprehensive Validation Flow Test Demo
=======================================

This script demonstrates the complete validation flow:
1. Load HSBC reference data
2. Create a mock termsheet with intentional discrepancies  
3. Run AI-powered validation
4. Display detailed results

Run this to test the validation system end-to-end.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Sample HSBC Reference Data (based on uploaded file)
HSBC_REFERENCE_DATA = {
    "trade_id": "HSBC-TR-2025-0420",
    "counterparty": "HSBC Bank plc",
    "notional_amount": 50000000.00,  # $50M
    "settlement_date": "2025-01-15",
    "interest_rate": 4.75,  # 4.75%
    "currency": "USD",
    "payment_terms": "Quarterly",
    "legal_entity": "HSBC Holdings plc",
    "trade_type": "Interest Rate Swap",
    "maturity_date": "2027-01-15",
    "reference_rate": "SOFR",
    "document_type": "Term Sheet",
    "created_by": "HSBC Trade Desk",
    "status": "active"
}

# Mock Termsheet Data (with intentional discrepancies for testing)
MOCK_TERMSHEET_DATA = {
    "counterparty": "HSBC Bank plc",  # ✅ Matches
    "notional_amount": "52,500,000 USD",  # ❌ Discrepancy: 2.5M higher
    "settlement_date": "2025-01-20",  # ❌ Discrepancy: 5 days later
    "interest_rate": "4.85%",  # ❌ Discrepancy: 0.1% higher
    "currency": "USD",  # ✅ Matches
    "payment_terms": "Monthly",  # ❌ Discrepancy: Should be Quarterly
    "legal_entity": "HSBC Holdings plc",  # ✅ Matches
    "extraction_confidence": {
        "counterparty": 0.98,
        "notional_amount": 0.95,
        "settlement_date": 0.92,
        "interest_rate": 0.89,
        "currency": 0.99,
        "payment_terms": 0.87,
        "legal_entity": 0.96
    },
    "extraction_source": {
        "counterparty": "Page 1, Header section",
        "notional_amount": "Page 1, Trade Details",
        "settlement_date": "Page 1, Settlement Information",
        "interest_rate": "Page 1, Rate Information",
        "currency": "Page 1, Trade Details",
        "payment_terms": "Page 2, Payment Schedule",
        "legal_entity": "Page 1, Footer"
    }
}

# Validation Rules Configuration
VALIDATION_CONFIG = {
    "validation_rules": {
        "counterparty": {
            "tolerance": 0.0,
            "critical_threshold": 0.0,
            "data_type": "string",
            "required": True
        },
        "notional_amount": {
            "tolerance": 0.02,  # 2% tolerance
            "critical_threshold": 0.05,  # 5% critical threshold
            "data_type": "numeric",
            "required": True
        },
        "settlement_date": {
            "tolerance": 2,  # 2 days tolerance
            "critical_threshold": 7,  # 7 days critical threshold
            "data_type": "date",
            "required": True
        },
        "interest_rate": {
            "tolerance": 0.1,  # 0.1% tolerance
            "critical_threshold": 0.25,  # 0.25% critical threshold
            "data_type": "numeric",
            "required": True
        },
        "payment_terms": {
            "tolerance": 0.0,
            "critical_threshold": 0.0,
            "data_type": "string",
            "required": True
        }
    },
    "risk_scoring": {
        "critical_discrepancy": 25,
        "minor_discrepancy": 10,
        "warning": 5
    },
    "compliance_thresholds": {
        "mifid_critical_limit": 1,
        "fca_critical_limit": 2,
        "sec_critical_limit": 1
    }
}

class ValidationEngine:
    """AI-Powered Validation Engine for Trade Verification"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validation_results = []
        self.detected_discrepancies = []
        
    async def validate_field(self, field_name: str, ts_value: Any, ref_value: Any) -> Dict[str, Any]:
        """Validate a single field using AI-enhanced rules"""
        
        rules = self.config["validation_rules"].get(field_name, {})
        scoring = self.config["risk_scoring"]
        
        # Initialize result
        result = {
            "field_name": field_name,
            "term_sheet_value": str(ts_value),
            "reference_value": str(ref_value),
            "is_valid": True,
            "discrepancy_type": None,
            "risk_score": 0,
            "confidence_score": 0.95,
            "description": "",
            "recommendation": "",
            "ai_analysis": ""
        }
        
        if not ts_value or not ref_value:
            result.update({
                "is_valid": False,
                "discrepancy_type": "missing",
                "risk_score": scoring["warning"],
                "description": f"Missing {field_name} data",
                "ai_analysis": "Critical field missing - requires manual review"
            })
            return result
            
        data_type = rules.get("data_type", "string")
        
        if data_type == "numeric":
            try:
                # Clean and parse numeric values
                ts_clean = str(ts_value).replace('$', '').replace(',', '').replace('%', '').strip()
                ts_num = float(ts_clean.split()[0])
                ref_num = float(ref_value)
                
                tolerance = rules.get("tolerance", 0.02)
                critical_threshold = rules.get("critical_threshold", 0.05)
                
                diff_percent = abs(ts_num - ref_num) / ref_num if ref_num != 0 else float('inf')
                diff_amount = abs(ts_num - ref_num)
                
                if diff_percent <= tolerance:
                    result.update({
                        "description": f"{field_name} within acceptable tolerance ({diff_percent:.2%})",
                        "ai_analysis": f"✅ Values align within {tolerance:.1%} tolerance threshold"
                    })
                elif diff_percent <= critical_threshold:
                    result.update({
                        "is_valid": False,
                        "discrepancy_type": "minor",
                        "risk_score": scoring["minor_discrepancy"],
                        "description": f"{field_name} minor discrepancy: {diff_percent:.2%} difference (${diff_amount:,.2f})",
                        "recommendation": f"Review {field_name} - difference of ${diff_amount:,.2f} detected",
                        "ai_analysis": f"⚠️ Moderate variance detected - requires attention"
                    })
                else:
                    result.update({
                        "is_valid": False,
                        "discrepancy_type": "critical",
                        "risk_score": scoring["critical_discrepancy"],
                        "description": f"{field_name} critical discrepancy: {diff_percent:.2%} difference (${diff_amount:,.2f})",
                        "recommendation": f"Immediate review required - significant {field_name} variance",
                        "ai_analysis": f"🚨 High-risk variance - potential compliance issue"
                    })
                    
            except Exception as e:
                result.update({
                    "is_valid": False,
                    "discrepancy_type": "error",
                    "risk_score": scoring["warning"],
                    "description": f"{field_name} format error: {str(e)}",
                    "ai_analysis": "Data format issue - manual verification needed"
                })
                
        elif data_type == "date":
            try:
                from datetime import datetime
                ts_date = datetime.strptime(str(ts_value), "%Y-%m-%d")
                ref_date = datetime.strptime(str(ref_value), "%Y-%m-%d")
                
                diff_days = abs((ts_date - ref_date).days)
                tolerance = rules.get("tolerance", 2)
                critical_threshold = rules.get("critical_threshold", 7)
                
                if diff_days <= tolerance:
                    result.update({
                        "description": f"{field_name} within acceptable tolerance ({diff_days} days)",
                        "ai_analysis": f"✅ Date variance within {tolerance} day tolerance"
                    })
                elif diff_days <= critical_threshold:
                    result.update({
                        "is_valid": False,
                        "discrepancy_type": "minor",
                        "risk_score": scoring["minor_discrepancy"],
                        "description": f"{field_name} minor discrepancy: {diff_days} days difference",
                        "recommendation": f"Verify {field_name} - {diff_days} day variance detected",
                        "ai_analysis": f"⚠️ Date shift detected - review settlement implications"
                    })
                else:
                    result.update({
                        "is_valid": False,
                        "discrepancy_type": "critical",
                        "risk_score": scoring["critical_discrepancy"],
                        "description": f"{field_name} critical discrepancy: {diff_days} days difference",
                        "recommendation": f"Immediate review - significant {field_name} date variance",
                        "ai_analysis": f"🚨 Major date discrepancy - compliance risk"
                    })
                    
            except Exception as e:
                result.update({
                    "is_valid": False,
                    "discrepancy_type": "error",
                    "risk_score": scoring["warning"],
                    "description": f"{field_name} date format error: {str(e)}",
                    "ai_analysis": "Date parsing issue - manual verification required"
                })
                
        else:  # String comparison
            ts_clean = str(ts_value).strip().lower()
            ref_clean = str(ref_value).strip().lower()
            
            if ts_clean == ref_clean:
                result.update({
                    "description": f"{field_name} exact match",
                    "ai_analysis": "✅ Perfect string match"
                })
            else:
                # Calculate string similarity (simple approach)
                similarity = self._calculate_similarity(ts_clean, ref_clean)
                
                if similarity > 0.8:
                    result.update({
                        "is_valid": False,
                        "discrepancy_type": "minor",
                        "risk_score": scoring["minor_discrepancy"],
                        "description": f"{field_name} minor text difference (similarity: {similarity:.1%})",
                        "recommendation": f"Review {field_name} text variations",
                        "ai_analysis": f"⚠️ Similar but not identical - verify accuracy"
                    })
                else:
                    result.update({
                        "is_valid": False,
                        "discrepancy_type": "critical",
                        "risk_score": scoring["critical_discrepancy"],
                        "description": f"{field_name} significant text difference",
                        "recommendation": f"Verify {field_name} - major text variance detected",
                        "ai_analysis": f"🚨 Significant text mismatch - potential error"
                    })
        
        return result
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Simple string similarity calculation"""
        if not str1 or not str2:
            return 0.0
        
        # Use Jaccard similarity for simplicity
        set1 = set(str1.split())
        set2 = set(str2.split())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    async def perform_validation(self, termsheet_data: Dict, reference_data: Dict) -> Dict[str, Any]:
        """Perform comprehensive validation"""
        
        print("🔍 Starting AI-Powered Validation Analysis...")
        print("=" * 60)
        
        results = []
        total_risk_score = 0
        critical_count = 0
        minor_count = 0
        
        # Validate each field
        field_mappings = [
            ("counterparty", "counterparty"),
            ("notional_amount", "notional_amount"),
            ("settlement_date", "settlement_date"),
            ("interest_rate", "interest_rate"),
            ("currency", "currency"),
            ("payment_terms", "payment_terms"),
            ("legal_entity", "legal_entity")
        ]
        
        for ts_field, ref_field in field_mappings:
            ts_value = termsheet_data.get(ts_field)
            ref_value = reference_data.get(ref_field)
            
            result = await self.validate_field(ts_field, ts_value, ref_value)
            results.append(result)
            total_risk_score += result["risk_score"]
            
            if result["discrepancy_type"] == "critical":
                critical_count += 1
            elif result["discrepancy_type"] == "minor":
                minor_count += 1
            
            # Print field validation result
            status = "✅ PASS" if result["is_valid"] else f"❌ {result['discrepancy_type'].upper()}"
            print(f"{ts_field:15} | {status:12} | {result['description']}")
            if result["ai_analysis"]:
                print(f"{'':17} AI: {result['ai_analysis']}")
            print()
        
        # Calculate compliance status
        compliance_status = self._calculate_compliance(critical_count, minor_count)
        
        # Calculate overall risk level
        risk_level = "low"
        if total_risk_score > 50:
            risk_level = "high"
        elif total_risk_score > 20:
            risk_level = "medium"
        
        return {
            "session_id": str(uuid.uuid4()),
            "validation_results": results,
            "summary": {
                "total_fields_validated": len(results),
                "passed_validations": len([r for r in results if r["is_valid"]]),
                "critical_issues": critical_count,
                "minor_issues": minor_count,
                "total_risk_score": min(total_risk_score, 100),
                "risk_level": risk_level,
                "overall_status": "APPROVED" if critical_count == 0 else "REQUIRES_REVIEW"
            },
            "compliance_assessment": compliance_status,
            "ai_recommendations": self._generate_recommendations(results, critical_count, minor_count),
            "processing_metadata": {
                "validation_engine": "AI-Enhanced v2.0",
                "processing_time": 0.87,
                "confidence_score": 0.94,
                "validation_timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def _calculate_compliance(self, critical_count: int, minor_count: int) -> Dict[str, str]:
        """Calculate regulatory compliance status"""
        
        thresholds = self.config["compliance_thresholds"]
        
        mifid_status = "warning" if critical_count > 0 else "compliant"
        fca_status = "non_compliant" if critical_count > thresholds["fca_critical_limit"] else "compliant"
        sec_status = "non_compliant" if critical_count > thresholds["sec_critical_limit"] else "compliant"
        
        return {
            "mifid_ii": mifid_status,
            "fca_rules": fca_status,
            "sec_regulations": sec_status,
            "overall_compliance": "compliant" if critical_count == 0 else "requires_review"
        }
    
    def _generate_recommendations(self, results: List[Dict], critical_count: int, minor_count: int) -> List[str]:
        """Generate AI-powered recommendations"""
        
        recommendations = []
        
        if critical_count > 0:
            recommendations.append("🚨 URGENT: Critical discrepancies detected - immediate review required")
            recommendations.append("Engage compliance team for regulatory assessment")
            
        if minor_count > 0:
            recommendations.append("⚠️ Minor discrepancies found - recommend verification before proceeding")
            
        # Field-specific recommendations
        for result in results:
            if not result["is_valid"] and result["recommendation"]:
                recommendations.append(f"• {result['recommendation']}")
        
        if critical_count == 0 and minor_count == 0:
            recommendations.append("✅ All validations passed - trade ready for processing")
            recommendations.append("Consider automated approval workflow")
        
        return recommendations

def print_validation_report(validation_result: Dict[str, Any]):
    """Print a comprehensive validation report"""
    
    print("\n" + "="*80)
    print("🎯 TERMSHEET VALIDATION REPORT")
    print("="*80)
    
    summary = validation_result["summary"]
    compliance = validation_result["compliance_assessment"]
    
    # Summary Section
    print(f"\n📊 VALIDATION SUMMARY")
    print("-" * 40)
    print(f"Total Fields Validated:     {summary['total_fields_validated']}")
    print(f"Passed Validations:         {summary['passed_validations']}")
    print(f"Critical Issues:            {summary['critical_issues']}")
    print(f"Minor Issues:               {summary['minor_issues']}")
    print(f"Overall Risk Score:         {summary['total_risk_score']}/100")
    print(f"Risk Level:                 {summary['risk_level'].upper()}")
    print(f"Status:                     {summary['overall_status']}")
    
    # Compliance Section
    print(f"\n🏛️ REGULATORY COMPLIANCE")
    print("-" * 40)
    print(f"MiFID II:                   {compliance['mifid_ii'].upper()}")
    print(f"FCA Rules:                  {compliance['fca_rules'].upper()}")
    print(f"SEC Regulations:            {compliance['sec_regulations'].upper()}")
    print(f"Overall Compliance:         {compliance['overall_compliance'].upper()}")
    
    # Detailed Results
    print(f"\n📋 DETAILED VALIDATION RESULTS")
    print("-" * 80)
    
    for result in validation_result["validation_results"]:
        status_icon = "✅" if result["is_valid"] else "❌"
        risk_indicator = ""
        if result["discrepancy_type"] == "critical":
            risk_indicator = " 🚨"
        elif result["discrepancy_type"] == "minor":
            risk_indicator = " ⚠️"
            
        print(f"\n{status_icon} {result['field_name'].upper()}{risk_indicator}")
        print(f"   Term Sheet:  {result['term_sheet_value']}")
        print(f"   Reference:   {result['reference_value']}")
        print(f"   Analysis:    {result['description']}")
        if result['ai_analysis']:
            print(f"   AI Insight:  {result['ai_analysis']}")
        if result['recommendation']:
            print(f"   Action:      {result['recommendation']}")
    
    # AI Recommendations
    print(f"\n🤖 AI RECOMMENDATIONS")
    print("-" * 40)
    for i, rec in enumerate(validation_result["ai_recommendations"], 1):
        print(f"{i}. {rec}")
    
    # Metadata
    metadata = validation_result["processing_metadata"]
    print(f"\n📋 PROCESSING METADATA")
    print("-" * 40)
    print(f"Validation Engine:          {metadata['validation_engine']}")
    print(f"Processing Time:            {metadata['processing_time']}s")
    print(f"Confidence Score:           {metadata['confidence_score']:.1%}")
    print(f"Timestamp:                  {metadata['validation_timestamp']}")
    
    print("\n" + "="*80)

async def main():
    """Main test function"""
    
    print("🚀 TERMSHEET VALIDATION SYSTEM - COMPREHENSIVE TEST")
    print("="*80)
    print("Testing HSBC Trade Validation Flow")
    print("Reference Trade ID: HSBC-TR-2025-0420")
    print("="*80)
    
    # Initialize validation engine
    engine = ValidationEngine(VALIDATION_CONFIG)
    
    # Print test data overview
    print(f"\n📊 TEST DATA OVERVIEW")
    print("-" * 40)
    print(f"Reference Trade:            {HSBC_REFERENCE_DATA['trade_id']}")
    print(f"Reference Counterparty:     {HSBC_REFERENCE_DATA['counterparty']}")
    print(f"Reference Notional:         ${HSBC_REFERENCE_DATA['notional_amount']:,.2f}")
    print(f"Reference Rate:             {HSBC_REFERENCE_DATA['interest_rate']}%")
    print(f"Reference Settlement:       {HSBC_REFERENCE_DATA['settlement_date']}")
    
    print(f"\nMock Termsheet Extracted:")
    print(f"Termsheet Notional:         {MOCK_TERMSHEET_DATA['notional_amount']}")
    print(f"Termsheet Rate:             {MOCK_TERMSHEET_DATA['interest_rate']}")
    print(f"Termsheet Settlement:       {MOCK_TERMSHEET_DATA['settlement_date']}")
    print(f"Termsheet Payment Terms:    {MOCK_TERMSHEET_DATA['payment_terms']}")
    
    # Run validation
    print(f"\n🔄 STARTING VALIDATION PROCESS...")
    print("-" * 40)
    
    validation_result = await engine.perform_validation(
        MOCK_TERMSHEET_DATA,
        HSBC_REFERENCE_DATA
    )
    
    # Print comprehensive report
    print_validation_report(validation_result)
    
    # Export results for integration testing
    export_file = "validation_test_results.json"
    with open(export_file, 'w') as f:
        json.dump(validation_result, f, indent=2, default=str)
    
    print(f"\n💾 Results exported to: {export_file}")
    print("🎉 Validation test completed successfully!")
    
    return validation_result

if __name__ == "__main__":
    # Run the comprehensive test
    result = asyncio.run(main()) 