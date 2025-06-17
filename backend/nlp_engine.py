"""
Phase 3: NLP Engine for Document Analysis & Validation
Advanced text processing, term extraction, and validation logic
"""

import re
import json
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import time

# Text processing libraries
from fuzzywuzzy import fuzz, process
import dateparser
import pandas as pd

class TermsheetNLPEngine:
    """Advanced NLP engine for termsheet document analysis"""
    
    def __init__(self):
        self.financial_patterns = self._initialize_financial_patterns()
        self.date_patterns = self._initialize_date_patterns()
        self.entity_patterns = self._initialize_entity_patterns()
        
    def _initialize_financial_patterns(self) -> Dict[str, List[str]]:
        """Initialize financial term patterns for extraction"""
        return {
            'valuation': [
                r'pre[\-\s]*money\s+valuation[:\s]*[\$]?([\d,\.]+(?:\s*(?:million|mil|M|billion|bil|B))?)',
                r'post[\-\s]*money\s+valuation[:\s]*[\$]?([\d,\.]+(?:\s*(?:million|mil|M|billion|bil|B))?)',
                r'company\s+valuation[:\s]*[\$]?([\d,\.]+(?:\s*(?:million|mil|M|billion|bil|B))?)',
                r'valuation[:\s]*[\$]?([\d,\.]+(?:\s*(?:million|mil|M|billion|bil|B))?)'
            ],
            'investment_amount': [
                r'investment\s+amount[:\s]*[\$]?([\d,\.]+(?:\s*(?:million|mil|M|billion|bil|B))?)',
                r'funding\s+amount[:\s]*[\$]?([\d,\.]+(?:\s*(?:million|mil|M|billion|bil|B))?)',
                r'raise[:\s]*[\$]?([\d,\.]+(?:\s*(?:million|mil|M|billion|bil|B))?)',
                r'series\s+[A-Z]\s+amount[:\s]*[\$]?([\d,\.]+(?:\s*(?:million|mil|M|billion|bil|B))?)'
            ],
            'equity_percentage': [
                r'equity\s+percentage[:\s]*([\d,\.]+%?)',
                r'ownership[:\s]*([\d,\.]+%?)',
                r'stake[:\s]*([\d,\.]+%?)',
                r'shares[:\s]*([\d,\.]+%?)'
            ],
            'liquidation_preference': [
                r'liquidation\s+preference[:\s]*(\d+(?:\.\d+)?x?)',
                r'liquidity\s+preference[:\s]*(\d+(?:\.\d+)?x?)',
                r'preference[:\s]*(\d+(?:\.\d+)?x?)'
            ],
            'anti_dilution': [
                r'anti[\-\s]*dilution[:\s]*(weighted\s+average|broad\s+based|narrow\s+based|full\s+ratchet|none)',
                r'anti[\-\s]*dilution\s+protection[:\s]*(weighted\s+average|broad\s+based|narrow\s+based|full\s+ratchet|none)'
            ],
            'board_seats': [
                r'board\s+seats[:\s]*(\d+)',
                r'board\s+composition[:\s]*(.+)',
                r'board\s+of\s+directors[:\s]*(.+)'
            ],
            'dividend_rate': [
                r'dividend\s+rate[:\s]*([\d,\.]+%?)',
                r'preferred\s+dividend[:\s]*([\d,\.]+%?)',
                r'dividend[:\s]*([\d,\.]+%?)'
            ]
        }
    
    def _initialize_date_patterns(self) -> List[str]:
        """Initialize date patterns for extraction"""
        return [
            r'(?:closing\s+date|date\s+of\s+closing)[:\s]*([^\n]+)',
            r'(?:expiration\s+date|expiry)[:\s]*([^\n]+)',
            r'(?:effective\s+date)[:\s]*([^\n]+)',
            r'(?:maturity\s+date)[:\s]*([^\n]+)',
            r'(?:due\s+date)[:\s]*([^\n]+)'
        ]
    
    def _initialize_entity_patterns(self) -> Dict[str, List[str]]:
        """Initialize entity patterns for extraction"""
        return {
            'company_name': [
                r'company[:\s]*([A-Z][A-Za-z\s,\.]*(?:Inc|LLC|Corp|Corporation|Ltd|Limited))',
                r'issuer[:\s]*([A-Z][A-Za-z\s,\.]*(?:Inc|LLC|Corp|Corporation|Ltd|Limited))',
            ],
            'investor_name': [
                r'investor[:\s]*([A-Z][A-Za-z\s,\.]*(?:Inc|LLC|Corp|Corporation|Ltd|Limited|Fund|Capital|Ventures|Partners)?)',
                r'purchaser[:\s]*([A-Z][A-Za-z\s,\.]*(?:Inc|LLC|Corp|Corporation|Ltd|Limited|Fund|Capital|Ventures|Partners)?)',
            ],
            'law_firm': [
                r'(?:counsel|attorney|law\s+firm)[:\s]*([A-Z][A-Za-z\s,\.&]*(?:LLP|LLC|PA|PC)?)',
            ]
        }
    
    def extract_financial_terms(self, text: str) -> List[Dict[str, Any]]:
        """Extract financial terms from text using pattern matching"""
        extracted_terms = []
        
        for term_category, patterns in self.financial_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if match.group(1):
                        extracted_terms.append({
                            'term_name': term_category,
                            'extracted_value': match.group(1).strip(),
                            'confidence_score': 0.8,
                            'location_in_text': f"Position {match.start()}-{match.end()}",
                            'extraction_method': 'regex_pattern',
                            'full_match': match.group(0).strip()
                        })
        
        return extracted_terms
    
    def extract_dates(self, text: str) -> List[Dict[str, Any]]:
        """Extract dates from text"""
        extracted_dates = []
        
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                date_str = match.group(1).strip()
                parsed_date = dateparser.parse(date_str)
                
                if parsed_date:
                    extracted_dates.append({
                        'term_name': 'date_field',
                        'extracted_value': parsed_date.strftime('%Y-%m-%d'),
                        'confidence_score': 0.9,
                        'location_in_text': f"Position {match.start()}-{match.end()}",
                        'extraction_method': 'date_parsing',
                        'original_text': date_str
                    })
        
        return extracted_dates
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text"""
        extracted_entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if match.group(1):
                        extracted_entities.append({
                            'term_name': entity_type,
                            'extracted_value': match.group(1).strip(),
                            'confidence_score': 0.7,
                            'location_in_text': f"Position {match.start()}-{match.end()}",
                            'extraction_method': 'entity_recognition'
                        })
        
        return extracted_entities
    
    def analyze_document_structure(self, text: str) -> Dict[str, Any]:
        """Analyze document structure and classify sections"""
        sections = []
        
        # Common termsheet section headers
        section_patterns = [
            r'(?:^|\n)\s*(?:TERMS?\s+OF\s+THE\s+PREFERRED\s+STOCK|TERM\s+SHEET)',
            r'(?:^|\n)\s*(?:COMPANY\s+INFORMATION|ISSUER)',
            r'(?:^|\n)\s*(?:INVESTOR\s+INFORMATION|PURCHASER)',
            r'(?:^|\n)\s*(?:PRICE\s+AND\s+VALUATION|PRICING)',
            r'(?:^|\n)\s*(?:LIQUIDATION\s+PREFERENCE)',
            r'(?:^|\n)\s*(?:ANTI[\-\s]*DILUTION)',
            r'(?:^|\n)\s*(?:BOARD\s+OF\s+DIRECTORS|BOARD\s+COMPOSITION)',
            r'(?:^|\n)\s*(?:INVESTOR\s+RIGHTS|PROTECTIVE\s+PROVISIONS)'
        ]
        
        for i, pattern in enumerate(section_patterns):
            matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
            if matches:
                sections.append({
                    'section_type': f"section_{i+1}",
                    'start_position': matches[0].start(),
                    'header_text': matches[0].group(0).strip()
                })
        
        return {
            'total_sections': len(sections),
            'sections': sections,
            'document_length': len(text),
            'estimated_complexity': 'high' if len(sections) > 6 else 'medium' if len(sections) > 3 else 'low'
        }
    
    def perform_comprehensive_analysis(self, text: str) -> Dict[str, Any]:
        """Perform comprehensive NLP analysis on the document"""
        start_time = time.time()
        
        # Extract all types of terms
        financial_terms = self.extract_financial_terms(text)
        dates = self.extract_dates(text)
        entities = self.extract_entities(text)
        structure = self.analyze_document_structure(text)
        
        # Basic text statistics
        word_count = len(text.split())
        sentence_count = len(re.split(r'[.!?]+', text))
        
        # Detect language (simple heuristic)
        english_words = ['the', 'and', 'or', 'of', 'to', 'in', 'for', 'with', 'by']
        english_score = sum(1 for word in english_words if word.lower() in text.lower()) / len(english_words)
        
        processing_time = time.time() - start_time
        
        return {
            'financial_terms': financial_terms,
            'dates': dates,
            'entities': entities,
            'document_structure': structure,
            'text_statistics': {
                'word_count': word_count,
                'sentence_count': sentence_count,
                'average_sentence_length': word_count / max(sentence_count, 1)
            },
            'language_detection': {
                'primary_language': 'english' if english_score > 0.5 else 'unknown',
                'confidence': english_score
            },
            'processing_time': processing_time,
            'total_extracted_terms': len(financial_terms) + len(dates) + len(entities)
        }

class ValidationEngine:
    """Engine for validating extracted terms against templates"""
    
    def __init__(self):
        self.fuzzy_threshold = 80
        
    def validate_exact_match(self, extracted_value: str, expected_value: str) -> Dict[str, Any]:
        """Validate using exact string matching"""
        is_match = extracted_value.strip().lower() == expected_value.strip().lower()
        return {
            'validation_status': 'valid' if is_match else 'invalid',
            'match_score': 1.0 if is_match else 0.0,
            'validation_method': 'exact_match'
        }
    
    def validate_fuzzy_match(self, extracted_value: str, expected_value: str, threshold: int = None) -> Dict[str, Any]:
        """Validate using fuzzy string matching"""
        threshold = threshold or self.fuzzy_threshold
        score = fuzz.ratio(extracted_value.strip().lower(), expected_value.strip().lower())
        
        return {
            'validation_status': 'valid' if score >= threshold else 'invalid',
            'match_score': score / 100.0,
            'validation_method': 'fuzzy_match'
        }
    
    def validate_range_check(self, extracted_value: str, expected_range: str) -> Dict[str, Any]:
        """Validate numerical values against ranges"""
        try:
            # Extract numeric value
            numeric_value = self._extract_numeric_value(extracted_value)
            if numeric_value is None:
                return {
                    'validation_status': 'invalid',
                    'match_score': 0.0,
                    'validation_method': 'range_check',
                    'notes': 'Could not extract numeric value'
                }
            
            # Parse range (e.g., "1-5", ">=10", "<100")
            if '-' in expected_range:
                min_val, max_val = map(float, expected_range.split('-'))
                is_valid = min_val <= numeric_value <= max_val
            elif expected_range.startswith('>='):
                min_val = float(expected_range[2:])
                is_valid = numeric_value >= min_val
            elif expected_range.startswith('<='):
                max_val = float(expected_range[2:])
                is_valid = numeric_value <= max_val
            elif expected_range.startswith('>'):
                min_val = float(expected_range[1:])
                is_valid = numeric_value > min_val
            elif expected_range.startswith('<'):
                max_val = float(expected_range[1:])
                is_valid = numeric_value < max_val
            else:
                # Single value
                target_value = float(expected_range)
                is_valid = abs(numeric_value - target_value) < 0.01
            
            return {
                'validation_status': 'valid' if is_valid else 'invalid',
                'match_score': 1.0 if is_valid else 0.0,
                'validation_method': 'range_check',
                'extracted_numeric': numeric_value
            }
            
        except Exception as e:
            return {
                'validation_status': 'invalid',
                'match_score': 0.0,
                'validation_method': 'range_check',
                'notes': f'Range validation error: {str(e)}'
            }
    
    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extract numeric value from text"""
        # Remove currency symbols and clean text
        cleaned = re.sub(r'[\$,]', '', text.strip())
        
        # Handle multipliers
        multipliers = {
            'million': 1_000_000, 'mil': 1_000_000, 'M': 1_000_000,
            'billion': 1_000_000_000, 'bil': 1_000_000_000, 'B': 1_000_000_000,
            'thousand': 1_000, 'k': 1_000, 'K': 1_000
        }
        
        for suffix, multiplier in multipliers.items():
            if suffix in cleaned:
                number_part = re.search(r'([\d,\.]+)', cleaned.replace(suffix, ''))
                if number_part:
                    return float(number_part.group(1).replace(',', '')) * multiplier
        
        # Extract simple number
        number_match = re.search(r'([\d,\.]+)', cleaned)
        if number_match:
            return float(number_match.group(1).replace(',', ''))
        
        return None
    
    def validate_term(self, extracted_value: str, validation_rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a term using the appropriate method"""
        validation_type = validation_rule.get('validation_type', 'exact_match')
        
        if validation_type == 'exact_match':
            return self.validate_exact_match(extracted_value, validation_rule['expected_value'])
        elif validation_type == 'fuzzy_match':
            threshold = int(validation_rule.get('tolerance', self.fuzzy_threshold) * 100)
            return self.validate_fuzzy_match(extracted_value, validation_rule['expected_value'], threshold)
        elif validation_type == 'range_check':
            return self.validate_range_check(extracted_value, validation_rule['expected_range'])
        else:
            return {
                'validation_status': 'invalid',
                'match_score': 0.0,
                'validation_method': validation_type,
                'notes': f'Unknown validation type: {validation_type}'
            }

# Initialize engines
nlp_engine = TermsheetNLPEngine()
validation_engine = ValidationEngine()

async def process_document_for_validation(file_path: str, session_id: str):
    """Process document specifically for validation interface"""
    try:
        from mongodb_models import TermSheetData as MongoTermSheetData
        
        # Extract text from document
        extracted_text = extract_text_from_file(file_path)
        
        if not extracted_text:
            return None
        
        # Use NLP to extract specific term sheet fields
        doc = nlp(extracted_text)
        
        # Initialize extraction results
        extracted_data = {
            "trade_id": None,
            "counterparty": None,
            "notional_amount": None,
            "settlement_date": None,
            "interest_rate": None,
            "currency": None,
            "payment_terms": None,
            "legal_entity": None
        }
        
        extraction_confidence = {}
        extraction_source = {}
        
        # Extract Trade ID
        trade_id_patterns = [
            r"(?i)trade\s*id[:\s]+([A-Z0-9\-]+)",
            r"(?i)reference[:\s]+([A-Z0-9\-]+)",
            r"(?i)deal\s*id[:\s]+([A-Z0-9\-]+)"
        ]
        
        for pattern in trade_id_patterns:
            matches = re.findall(pattern, extracted_text)
            if matches:
                extracted_data["trade_id"] = matches[0].strip()
                extraction_confidence["trade_id"] = 0.9
                extraction_source["trade_id"] = f"Pattern match: {pattern[:20]}..."
                break
        
        # Extract Counterparty
        counterparty_patterns = [
            r"(?i)counterparty[:\s]+([A-Za-z\s&\.,]+?)(?:\n|$|[;:])",
            r"(?i)client[:\s]+([A-Za-z\s&\.,]+?)(?:\n|$|[;:])",
            r"(?i)with[:\s]+([A-Z][A-Za-z\s&\.,]+?)(?:\n|$|[;:])"
        ]
        
        for pattern in counterparty_patterns:
            matches = re.findall(pattern, extracted_text)
            if matches:
                counterparty = matches[0].strip()
                if len(counterparty) > 5 and not counterparty.lower() in ['the', 'and', 'for']:
                    extracted_data["counterparty"] = counterparty
                    extraction_confidence["counterparty"] = 0.85
                    extraction_source["counterparty"] = f"Pattern match: {pattern[:20]}..."
                    break
        
        # Extract Notional Amount
        amount_patterns = [
            r"(?i)notional[:\s]+([USD|EUR|GBP]*\s*[\d,\.]+(?:\s*million|m|k)?)",
            r"(?i)principal[:\s]+([USD|EUR|GBP]*\s*[\d,\.]+(?:\s*million|m|k)?)",
            r"(?i)amount[:\s]+([USD|EUR|GBP]*\s*[\d,\.]+(?:\s*million|m|k)?)"
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, extracted_text)
            if matches:
                extracted_data["notional_amount"] = matches[0].strip()
                extraction_confidence["notional_amount"] = 0.9
                extraction_source["notional_amount"] = f"Pattern match: {pattern[:20]}..."
                break
        
        # Extract Settlement Date
        date_patterns = [
            r"(?i)settlement[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
            r"(?i)settlement[:\s]+(\d{1,2}\s+\w+\s+\d{2,4})",
            r"(?i)maturity[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})"
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, extracted_text)
            if matches:
                extracted_data["settlement_date"] = matches[0].strip()
                extraction_confidence["settlement_date"] = 0.8
                extraction_source["settlement_date"] = f"Pattern match: {pattern[:20]}..."
                break
        
        # Extract Interest Rate
        rate_patterns = [
            r"(?i)interest\s+rate[:\s]+([\d\.]+%?)",
            r"(?i)rate[:\s]+([\d\.]+%)",
            r"(?i)coupon[:\s]+([\d\.]+%?)"
        ]
        
        for pattern in rate_patterns:
            matches = re.findall(pattern, extracted_text)
            if matches:
                extracted_data["interest_rate"] = matches[0].strip()
                extraction_confidence["interest_rate"] = 0.85
                extraction_source["interest_rate"] = f"Pattern match: {pattern[:20]}..."
                break
        
        # Extract Currency
        currency_patterns = [
            r"(?i)currency[:\s]+([A-Z]{3})",
            r"(?i)([USD|EUR|GBP|JPY|CHF]{3})",
        ]
        
        for pattern in currency_patterns:
            matches = re.findall(pattern, extracted_text)
            if matches:
                extracted_data["currency"] = matches[0].strip()
                extraction_confidence["currency"] = 0.9
                extraction_source["currency"] = f"Pattern match: {pattern[:20]}..."
                break
        
        # Extract Payment Terms
        payment_patterns = [
            r"(?i)payment[:\s]+([A-Za-z\s]+?)(?:\n|$|[;:])",
            r"(?i)frequency[:\s]+([A-Za-z\s]+?)(?:\n|$|[;:])"
        ]
        
        for pattern in payment_patterns:
            matches = re.findall(pattern, extracted_text)
            if matches:
                payment_terms = matches[0].strip()
                if len(payment_terms) > 3:
                    extracted_data["payment_terms"] = payment_terms
                    extraction_confidence["payment_terms"] = 0.7
                    extraction_source["payment_terms"] = f"Pattern match: {pattern[:20]}..."
                    break
        
        # Extract Legal Entity
        entity_patterns = [
            r"(?i)legal\s+entity[:\s]+([A-Za-z\s&\.,]+?)(?:\n|$|[;:])",
            r"(?i)entity[:\s]+([A-Za-z\s&\.,]+?)(?:\n|$|[;:])"
        ]
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, extracted_text)
            if matches:
                entity = matches[0].strip()
                if len(entity) > 5:
                    extracted_data["legal_entity"] = entity
                    extraction_confidence["legal_entity"] = 0.8
                    extraction_source["legal_entity"] = f"Pattern match: {pattern[:20]}..."
                    break
        
        # Create TermSheetData object
        term_sheet_data = MongoTermSheetData(
            session_id=session_id,
            **extracted_data,
            extraction_confidence=extraction_confidence,
            extraction_source=extraction_source,
            raw_extracted_data={"full_text": extracted_text[:1000]}  # Store first 1000 chars
        )
        
        await term_sheet_data.insert()
        
        # Return response format
        from schemas import TermSheetDataResponse
        return TermSheetDataResponse(
            id=str(term_sheet_data.id),
            session_id=term_sheet_data.session_id,
            trade_id=term_sheet_data.trade_id,
            counterparty=term_sheet_data.counterparty,
            notional_amount=term_sheet_data.notional_amount,
            settlement_date=term_sheet_data.settlement_date,
            interest_rate=term_sheet_data.interest_rate,
            currency=term_sheet_data.currency,
            payment_terms=term_sheet_data.payment_terms,
            legal_entity=term_sheet_data.legal_entity,
            extraction_confidence=term_sheet_data.extraction_confidence,
            extraction_source=term_sheet_data.extraction_source,
            created_at=term_sheet_data.created_at,
            updated_at=term_sheet_data.updated_at
        )
        
    except Exception as e:
        logging.error(f"Error processing document for validation: {e}")
        return None 