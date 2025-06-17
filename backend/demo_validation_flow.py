#!/usr/bin/env python3
"""
Complete HSBC Termsheet Validation Demo
=======================================

This demonstrates the complete validation flow:
1. Load HSBC reference data
2. Create mock termsheet with discrepancies
3. Run validation engine
4. Show detailed results with AI analysis
5. Generate compliance report

This is a comprehensive test of the validation system.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
import asyncio

# HSBC Reference Data (Based on uploaded file)
HSBC_REFERENCE_DATA = {
    "document_info": {
        "trade_id": "HSBC-TR-2025-0420",
        "document_type": "Interest Rate Swap Term Sheet",
        "bank": "HSBC Bank plc",
        "created_date": "2025-01-10",
        "version": "1.0"
    },
    "trade_details": {
        "counterparty": "HSBC Bank plc",
        "notional_amount": 50000000.00,  # $50M USD
        "currency": "USD",
        "trade_type": "Interest Rate Swap",
        "effective_date": "2025-01-15",
        "maturity_date": "2027-01-15",
        "settlement_date": "2025-01-15"
    },
    "rate_information": {
        "fixed_rate": 4.75,  # 4.75%
        "floating_rate_index": "SOFR",
        "payment_frequency": "Quarterly",
        "day_count_convention": "30/360",
        "business_day_convention": "Modified Following"
    },
    "legal_terms": {
        "governing_law": "English Law",
        "legal_entity": "HSBC Holdings plc",
        "master_agreement": "ISDA 2002",
        "credit_support_annex": "Yes"
    },
    "risk_metrics": {
        "credit_rating": "AA-",
        "market_risk_limit": 75000000.00,
        "counterparty_limit": 100000000.00
    }
}

# Mock Termsheet with Intentional Discrepancies (for testing)
MOCK_TERMSHEET_EXTRACTION = {
    "document_info": {
        "trade_id": "HSBC-TR-2025-0420",  # ✅ Matches
        "document_type": "Interest Rate Swap Term Sheet",  # ✅ Matches
        "bank": "HSBC Bank plc",  # ✅ Matches
        "extraction_confidence": 0.98
    },
    "trade_details": {
        "counterparty": "HSBC Bank plc",  # ✅ Matches
        "notional_amount": 52500000.00,   # ❌ $2.5M higher (5% increase)
        "currency": "USD",                # ✅ Matches
        "trade_type": "Interest Rate Swap",  # ✅ Matches
        "effective_date": "2025-01-15",   # ✅ Matches
        "maturity_date": "2027-01-15",    # ✅ Matches
        "settlement_date": "2025-01-20",  # ❌ 5 days later
        "extraction_confidence": 0.94
    },
    "rate_information": {
        "fixed_rate": 4.85,               # ❌ 0.1% higher
        "floating_rate_index": "SOFR",    # ✅ Matches
        "payment_frequency": "Monthly",   # ❌ Should be Quarterly
        "day_count_convention": "30/360", # ✅ Matches
        "business_day_convention": "Modified Following",  # ✅ Matches
        "extraction_confidence": 0.89
    },
    "legal_terms": {
        "governing_law": "English Law",   # ✅ Matches
        "legal_entity": "HSBC Holdings plc",  # ✅ Matches
        "master_agreement": "ISDA 2002",  # ✅ Matches
        "credit_support_annex": "Yes",    # ✅ Matches
        "extraction_confidence": 0.96
    },
    "extraction_metadata": {
        "processing_time": 2.3,
        "total_confidence": 0.94,
        "pages_processed": 3,
        "extraction_method": "AI-OCR Enhanced"
    }
}

class ComprehensiveValidationEngine:
    """Advanced validation engine with AI analysis"""
    
    def __init__(self):
        self.validation_rules = {
            "notional_amount": {
                "tolerance_percent": 2.0,  # 2% tolerance
                "critical_threshold": 5.0,  # 5% critical
                "data_type": "numeric",
                "importance": "critical"
            },
            "settlement_date": {
                "tolerance_days": 2,
                "critical_threshold": 7,
                "data_type": "date",
                "importance": "high"
            },
            "fixed_rate": {
                "tolerance_percent": 0.05,  # 0.05% tolerance
                "critical_threshold": 0.15,  # 0.15% critical
                "data_type": "numeric",
                "importance": "critical"
            },
            "payment_frequency": {
                "tolerance": 0,
                "data_type": "categorical",
                "importance": "high"
            }
        }
        
        self.risk_scoring = {
            "critical": 25,
            "high": 15,
            "medium": 10,
            "low": 5
        }
    
    async def validate_termsheet(self, reference_data: Dict, extracted_data: Dict) -> Dict[str, Any]:
        """Perform comprehensive termsheet validation"""
        
        print("🔍 STARTING COMPREHENSIVE VALIDATION")
        print("="*80)
        
        session_id = str(uuid.uuid4())
        validation_results = []
        total_risk_score = 0
        
        # Validate Trade Details
        trade_validations = await self._validate_section(
            "trade_details", 
            reference_data["trade_details"], 
            extracted_data["trade_details"]
        )
        validation_results.extend(trade_validations)
        
        # Validate Rate Information
        rate_validations = await self._validate_section(
            "rate_information",
            reference_data["rate_information"],
            extracted_data["rate_information"]
        )
        validation_results.extend(rate_validations)
        
        # Calculate totals
        total_risk_score = sum(r["risk_score"] for r in validation_results)
        critical_count = len([r for r in validation_results if r["severity"] == "critical"])
        high_count = len([r for r in validation_results if r["severity"] == "high"])
        
        # Generate summary
        summary = {
            "session_id": session_id,
            "total_fields_validated": len(validation_results),
            "passed_validations": len([r for r in validation_results if r["is_valid"]]),
            "critical_issues": critical_count,
            "high_issues": high_count,
            "total_risk_score": min(total_risk_score, 100),
            "overall_status": "APPROVED" if critical_count == 0 else "REQUIRES_REVIEW",
            "compliance_level": self._calculate_compliance_level(critical_count, high_count)
        }
        
        # Generate AI recommendations
        ai_recommendations = self._generate_ai_recommendations(validation_results, summary)
        
        return {
            "session_id": session_id,
            "validation_results": validation_results,
            "summary": summary,
            "ai_recommendations": ai_recommendations,
            "compliance_assessment": self._assess_regulatory_compliance(validation_results),
            "processing_metadata": {
                "validation_engine": "Comprehensive AI v3.0",
                "processing_time": 1.2,
                "timestamp": datetime.now().isoformat(),
                "reference_source": "HSBC-TR-2025-0420"
            }
        }
    
    async def _validate_section(self, section_name: str, reference: Dict, extracted: Dict) -> List[Dict]:
        """Validate a specific section"""
        
        results = []
        
        for field_name, ref_value in reference.items():
            if field_name in extracted:
                ext_value = extracted[field_name]
                result = await self._validate_field(f"{section_name}.{field_name}", ref_value, ext_value)
                results.append(result)
        
        return results
    
    async def _validate_field(self, field_path: str, reference_value: Any, extracted_value: Any) -> Dict[str, Any]:
        """Validate individual field with AI analysis"""
        
        field_name = field_path.split('.')[-1]
        rules = self.validation_rules.get(field_name, {})
        
        result = {
            "field_path": field_path,
            "field_name": field_name,
            "reference_value": reference_value,
            "extracted_value": extracted_value,
            "is_valid": True,
            "severity": "low",
            "risk_score": 0,
            "confidence": 0.95,
            "description": "",
            "ai_analysis": "",
            "recommendation": ""
        }
        
        # Numeric validation
        if field_name in ["notional_amount", "fixed_rate"]:
            result.update(await self._validate_numeric_field(field_name, reference_value, extracted_value, rules))
        
        # Date validation
        elif field_name in ["settlement_date", "effective_date", "maturity_date"]:
            result.update(await self._validate_date_field(field_name, reference_value, extracted_value, rules))
        
        # Categorical validation
        elif field_name in ["payment_frequency", "currency", "counterparty"]:
            result.update(await self._validate_categorical_field(field_name, reference_value, extracted_value, rules))
        
        # Default string validation
        else:
            result.update(await self._validate_string_field(field_name, reference_value, extracted_value))
        
        return result
    
    async def _validate_numeric_field(self, field_name: str, ref_val: float, ext_val: float, rules: Dict) -> Dict:
        """Validate numeric fields with tolerance"""
        
        tolerance = rules.get("tolerance_percent", 1.0)
        critical_threshold = rules.get("critical_threshold", 5.0)
        
        if ref_val == 0:
            diff_percent = 100.0 if ext_val != 0 else 0.0
        else:
            diff_percent = abs(ext_val - ref_val) / ref_val * 100
        
        diff_amount = abs(ext_val - ref_val)
        
        if diff_percent <= tolerance:
            return {
                "description": f"{field_name} within tolerance ({diff_percent:.2f}%)",
                "ai_analysis": f"✅ Value variance of {diff_percent:.2f}% is within acceptable {tolerance}% threshold"
            }
        elif diff_percent <= critical_threshold:
            return {
                "is_valid": False,
                "severity": "high",
                "risk_score": self.risk_scoring["high"],
                "description": f"{field_name} high variance: {diff_percent:.2f}% difference",
                "ai_analysis": f"⚠️ Significant variance detected. Difference: ${diff_amount:,.2f} ({diff_percent:.2f}%)",
                "recommendation": f"Verify {field_name} - investigate {diff_percent:.2f}% variance"
            }
        else:
            return {
                "is_valid": False,
                "severity": "critical",
                "risk_score": self.risk_scoring["critical"],
                "description": f"{field_name} critical variance: {diff_percent:.2f}% difference",
                "ai_analysis": f"🚨 CRITICAL: Major variance of {diff_percent:.2f}% exceeds {critical_threshold}% threshold",
                "recommendation": f"URGENT: Review {field_name} - ${diff_amount:,.2f} difference requires immediate attention"
            }
    
    async def _validate_date_field(self, field_name: str, ref_val: str, ext_val: str, rules: Dict) -> Dict:
        """Validate date fields"""
        
        try:
            ref_date = datetime.strptime(ref_val, "%Y-%m-%d")
            ext_date = datetime.strptime(ext_val, "%Y-%m-%d")
            
            diff_days = abs((ext_date - ref_date).days)
            tolerance = rules.get("tolerance_days", 1)
            critical_threshold = rules.get("critical_threshold", 5)
            
            if diff_days <= tolerance:
                return {
                    "description": f"{field_name} within tolerance ({diff_days} days)",
                    "ai_analysis": f"✅ Date variance of {diff_days} days is acceptable"
                }
            elif diff_days <= critical_threshold:
                return {
                    "is_valid": False,
                    "severity": "high",
                    "risk_score": self.risk_scoring["high"],
                    "description": f"{field_name} date variance: {diff_days} days",
                    "ai_analysis": f"⚠️ Date shift of {diff_days} days may impact settlement",
                    "recommendation": f"Verify {field_name} - {diff_days} day variance detected"
                }
            else:
                return {
                    "is_valid": False,
                    "severity": "critical",
                    "risk_score": self.risk_scoring["critical"],
                    "description": f"{field_name} critical date variance: {diff_days} days",
                    "ai_analysis": f"🚨 CRITICAL: {diff_days} day variance exceeds acceptable threshold",
                    "recommendation": f"URGENT: Review {field_name} - major date discrepancy"
                }
                
        except Exception as e:
            return {
                "is_valid": False,
                "severity": "high",
                "risk_score": self.risk_scoring["medium"],
                "description": f"{field_name} date format error",
                "ai_analysis": f"❌ Date parsing error: {str(e)}",
                "recommendation": f"Fix {field_name} date format"
            }
    
    async def _validate_categorical_field(self, field_name: str, ref_val: str, ext_val: str, rules: Dict) -> Dict:
        """Validate categorical fields"""
        
        if str(ref_val).lower().strip() == str(ext_val).lower().strip():
            return {
                "description": f"{field_name} exact match",
                "ai_analysis": "✅ Perfect categorical match"
            }
        else:
            return {
                "is_valid": False,
                "severity": "critical" if rules.get("importance") == "critical" else "high",
                "risk_score": self.risk_scoring["critical"] if rules.get("importance") == "critical" else self.risk_scoring["high"],
                "description": f"{field_name} mismatch: '{ext_val}' vs '{ref_val}'",
                "ai_analysis": f"🚨 Categorical mismatch detected - values must be identical",
                "recommendation": f"Correct {field_name} - should be '{ref_val}'"
            }
    
    async def _validate_string_field(self, field_name: str, ref_val: str, ext_val: str) -> Dict:
        """Default string validation"""
        
        if str(ref_val).strip() == str(ext_val).strip():
            return {
                "description": f"{field_name} matches",
                "ai_analysis": "✅ String match confirmed"
            }
        else:
            return {
                "is_valid": False,
                "severity": "medium",
                "risk_score": self.risk_scoring["medium"],
                "description": f"{field_name} text difference",
                "ai_analysis": f"⚠️ Text variance detected",
                "recommendation": f"Review {field_name} text accuracy"
            }
    
    def _calculate_compliance_level(self, critical_count: int, high_count: int) -> str:
        """Calculate overall compliance level"""
        
        if critical_count > 0:
            return "NON_COMPLIANT"
        elif high_count > 2:
            return "REQUIRES_REVIEW"
        elif high_count > 0:
            return "CONDITIONAL_APPROVAL"
        else:
            return "FULLY_COMPLIANT"
    
    def _generate_ai_recommendations(self, validation_results: List[Dict], summary: Dict) -> List[str]:
        """Generate AI-powered recommendations"""
        
        recommendations = []
        
        critical_issues = [r for r in validation_results if r["severity"] == "critical"]
        high_issues = [r for r in validation_results if r["severity"] == "high"]
        
        if critical_issues:
            recommendations.append("🚨 IMMEDIATE ACTION REQUIRED: Critical discrepancies detected")
            recommendations.append("• Halt processing until critical issues are resolved")
            recommendations.append("• Engage compliance team for risk assessment")
            
            for issue in critical_issues:
                recommendations.append(f"• CRITICAL: {issue['recommendation']}")
        
        if high_issues:
            recommendations.append("⚠️ HIGH PRIORITY: Significant discrepancies require attention")
            
            for issue in high_issues:
                recommendations.append(f"• HIGH: {issue['recommendation']}")
        
        # Risk-based recommendations
        risk_score = summary["total_risk_score"]
        if risk_score > 50:
            recommendations.append("📊 RISK ASSESSMENT: High risk score requires senior review")
        elif risk_score > 25:
            recommendations.append("📊 RISK ASSESSMENT: Medium risk - additional verification recommended")
        
        if not critical_issues and not high_issues:
            recommendations.append("✅ APPROVAL READY: All validations passed successfully")
            recommendations.append("• Trade can proceed with standard processing")
            recommendations.append("• Consider automated approval workflow")
        
        return recommendations
    
    def _assess_regulatory_compliance(self, validation_results: List[Dict]) -> Dict[str, str]:
        """Assess regulatory compliance status"""
        
        critical_count = len([r for r in validation_results if r["severity"] == "critical"])
        high_count = len([r for r in validation_results if r["severity"] == "high"])
        
        return {
            "mifid_ii_compliance": "non_compliant" if critical_count > 0 else "compliant",
            "fca_rules_compliance": "requires_review" if critical_count > 1 or high_count > 3 else "compliant",
            "sec_regulations": "non_compliant" if critical_count > 0 else "compliant",
            "overall_regulatory_status": "compliant" if critical_count == 0 and high_count <= 2 else "requires_review"
        }

def print_comprehensive_report(validation_result: Dict[str, Any]):
    """Print a comprehensive validation report"""
    
    print("\n" + "="*100)
    print("🎯 COMPREHENSIVE TERMSHEET VALIDATION REPORT")
    print("="*100)
    
    # Header Information
    metadata = validation_result["processing_metadata"]
    print(f"Session ID: {validation_result['session_id']}")
    print(f"Reference Source: {metadata['reference_source']}")
    print(f"Validation Engine: {metadata['validation_engine']}")
    print(f"Processing Time: {metadata['processing_time']}s")
    print(f"Timestamp: {metadata['timestamp']}")
    
    # Executive Summary
    summary = validation_result["summary"]
    print(f"\n📊 EXECUTIVE SUMMARY")
    print("-" * 50)
    print(f"Total Fields Validated:     {summary['total_fields_validated']}")
    print(f"Passed Validations:         {summary['passed_validations']}")
    print(f"Critical Issues:            {summary['critical_issues']}")
    print(f"High Priority Issues:       {summary['high_issues']}")
    print(f"Overall Risk Score:         {summary['total_risk_score']}/100")
    print(f"Compliance Level:           {summary['compliance_level']}")
    print(f"Processing Status:          {summary['overall_status']}")
    
    # Regulatory Compliance
    compliance = validation_result["compliance_assessment"]
    print(f"\n🏛️ REGULATORY COMPLIANCE ASSESSMENT")
    print("-" * 50)
    print(f"MiFID II Compliance:        {compliance['mifid_ii_compliance'].upper()}")
    print(f"FCA Rules Compliance:       {compliance['fca_rules_compliance'].upper()}")
    print(f"SEC Regulations:            {compliance['sec_regulations'].upper()}")
    print(f"Overall Status:             {compliance['overall_regulatory_status'].upper()}")
    
    # Detailed Validation Results
    print(f"\n📋 DETAILED VALIDATION RESULTS")
    print("-" * 100)
    
    for result in validation_result["validation_results"]:
        # Status indicator
        if result["is_valid"]:
            status_icon = "✅"
            status_text = "PASS"
        else:
            severity = result["severity"]
            if severity == "critical":
                status_icon = "🚨"
                status_text = "CRITICAL"
            elif severity == "high":
                status_icon = "⚠️"
                status_text = "HIGH"
            else:
                status_icon = "⚠️"
                status_text = "MEDIUM"
        
        print(f"\n{status_icon} {result['field_name'].upper()} - {status_text}")
        print(f"   Reference Value:     {result['reference_value']}")
        print(f"   Extracted Value:     {result['extracted_value']}")
        print(f"   Risk Score:          {result['risk_score']}")
        print(f"   Description:         {result['description']}")
        print(f"   AI Analysis:         {result['ai_analysis']}")
        
        if result['recommendation']:
            print(f"   Recommendation:      {result['recommendation']}")
    
    # AI Recommendations
    print(f"\n🤖 AI-POWERED RECOMMENDATIONS")
    print("-" * 50)
    for i, recommendation in enumerate(validation_result["ai_recommendations"], 1):
        print(f"{i}. {recommendation}")
    
    print("\n" + "="*100)

async def main():
    """Run the comprehensive validation demo"""
    
    print("🚀 COMPREHENSIVE HSBC TERMSHEET VALIDATION DEMO")
    print("="*100)
    print("Demonstrating AI-Powered Trade Validation System")
    print("Reference Trade: HSBC-TR-2025-0420 (Interest Rate Swap)")
    print("="*100)
    
    # Initialize validation engine
    engine = ComprehensiveValidationEngine()
    
    # Show test overview
    print(f"\n📊 VALIDATION TEST OVERVIEW")
    print("-" * 50)
    print(f"Reference Trade ID:         {HSBC_REFERENCE_DATA['document_info']['trade_id']}")
    print(f"Reference Notional:         ${HSBC_REFERENCE_DATA['trade_details']['notional_amount']:,.2f}")
    print(f"Reference Rate:             {HSBC_REFERENCE_DATA['rate_information']['fixed_rate']}%")
    print(f"Reference Settlement:       {HSBC_REFERENCE_DATA['trade_details']['settlement_date']}")
    print(f"Reference Payment Freq:     {HSBC_REFERENCE_DATA['rate_information']['payment_frequency']}")
    
    print(f"\nExtracted from Termsheet:")
    print(f"Extracted Notional:         ${MOCK_TERMSHEET_EXTRACTION['trade_details']['notional_amount']:,.2f}")
    print(f"Extracted Rate:             {MOCK_TERMSHEET_EXTRACTION['rate_information']['fixed_rate']}%")
    print(f"Extracted Settlement:       {MOCK_TERMSHEET_EXTRACTION['trade_details']['settlement_date']}")
    print(f"Extracted Payment Freq:     {MOCK_TERMSHEET_EXTRACTION['rate_information']['payment_frequency']}")
    print(f"Extraction Confidence:      {MOCK_TERMSHEET_EXTRACTION['extraction_metadata']['total_confidence']:.1%}")
    
    # Run comprehensive validation
    print(f"\n🔄 RUNNING COMPREHENSIVE VALIDATION...")
    print("-" * 50)
    
    validation_result = await engine.validate_termsheet(
        HSBC_REFERENCE_DATA,
        MOCK_TERMSHEET_EXTRACTION
    )
    
    # Display comprehensive report
    print_comprehensive_report(validation_result)
    
    # Export results
    output_file = "comprehensive_validation_results.json"
    with open(output_file, 'w') as f:
        json.dump(validation_result, f, indent=2, default=str)
    
    print(f"\n💾 RESULTS EXPORTED")
    print("-" * 50)
    print(f"Detailed results saved to: {output_file}")
    print(f"File size: {len(json.dumps(validation_result, indent=2, default=str))} bytes")
    
    print(f"\n🎉 COMPREHENSIVE VALIDATION DEMO COMPLETED!")
    print("="*100)
    
    return validation_result

if __name__ == "__main__":
    # Run the comprehensive validation demo
    result = asyncio.run(main()) 