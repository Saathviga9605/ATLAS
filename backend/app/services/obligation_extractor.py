"""
Obligation Extractor
Uses LLM prompting (or rule-based) to extract structured obligations
"""

import logging
import re
from typing import List, Dict, Any
from datetime import datetime

from app.models.schemas import Obligation

logger = logging.getLogger(__name__)


class ObligationExtractor:
    """
    Extracts structured compliance obligations from regulatory text
    
    For MVP: Uses rule-based extraction (can be replaced with LLM)
    """
    
    # Obligation extraction prompts (for LLM-based approach)
    EXTRACTION_PROMPT = """
You are a compliance expert analyzing regulatory text.

Extract compliance obligations from the following text.
For each obligation, provide:
1. A unique ID (format: {REGULATION}_{SECTION}_{ACTION})
2. A clear description of what must be done
3. Data types affected (PAN, PII, SSN, CVV, etc.)
4. Where it applies (logs, chats, transactions, databases, etc.)
5. Severity (CRITICAL, HIGH, MEDIUM, LOW)

Text:
{text}

Regulation: {regulation}
Section: {section}

Output as JSON array of obligations.
"""
    
    def __init__(self):
        """Initialize obligation extractor"""
        logger.info("🔧 Obligation extractor initialized")
        
        # Rule-based patterns for MVP
        self.patterns = {
            'prohibition': [
                r'must not (be )?(store|transmit|display|log|send)',
                r'shall not (be )?(store|transmit|display|log|send)',
                r'prohibit(ed)? (from )?(storing|transmitting|displaying|logging|sending)',
                r'cannot (be )?(store|transmit|display|log|send)',
                r'do not (store|transmit|display|log|send)',
            ],
            'requirement': [
                r'must (be )?(masked|encrypted|protected|secured|hashed)',
                r'shall (be )?(masked|encrypted|protected|secured|hashed)',
                r'require(s|d)? (that )?(.*?)(masked|encrypted|protected|secured)',
                r'ensure (that )?',
            ],
            'data_types': {
                'PAN': r'\b(PAN|Primary Account Number|card number|payment card)\b',
                'CVV': r'\b(CVV|CVV2|CVC|Card Verification)\b',
                'PII': r'\b(PII|Personally Identifiable Information|personal data)\b',
                'SSN': r'\b(SSN|Social Security Number)\b',
                'PASSWORD': r'\b(password|passphrase|credential)\b',
            },
            'applies_to': {
                'logs': r'\b(log|logging|log file)\b',
                'chats': r'\b(chat|message|communication|conversation|support)\b',
                'transactions': r'\b(transaction|payment|processing)\b',
                'storage': r'\b(store|storage|database|repository)\b',
                'transmission': r'\b(transmit|transmission|transfer|send)\b',
                'display': r'\b(display|show|render|view)\b',
            }
        }
    
    async def extract_obligations(
        self,
        text: str,
        regulation: str,
        section: str,
        metadata: Dict[str, Any]
    ) -> List[Obligation]:
        """
        Extract obligations from regulatory text
        
        For MVP: Uses rule-based extraction
        Can be replaced with LLM API call
        """
        obligations = []
        
        # Detect prohibition type obligations
        prohibitions = self._extract_prohibitions(text, regulation, section, metadata)
        obligations.extend(prohibitions)
        
        # Detect requirement type obligations
        requirements = self._extract_requirements(text, regulation, section, metadata)
        obligations.extend(requirements)
        
        return obligations
    
    def _extract_prohibitions(
        self,
        text: str,
        regulation: str,
        section: str,
        metadata: Dict[str, Any]
    ) -> List[Obligation]:
        """Extract prohibition-type obligations"""
        obligations = []
        text_lower = text.lower()
        
        # Check if text contains prohibition patterns
        is_prohibition = any(
            re.search(pattern, text_lower)
            for pattern in self.patterns['prohibition']
        )
        
        if not is_prohibition:
            return obligations
        
        # Extract data types
        data_types = self._extract_data_types(text)
        
        # Extract contexts
        applies_to = self._extract_contexts(text)
        
        # Determine severity
        severity = self._determine_severity(text, data_types)
        
        if data_types and applies_to:
            # Create obligation for each data type + context combination
            for data_type in data_types[:2]:  # Limit to prevent explosion
                action = "PROHIBIT"
                obligation_id = f"{regulation.replace('-', '_')}_{section.replace('.', '_')}_{action}_{data_type}"
                
                # Create description
                description = self._generate_description(
                    action_type="prohibition",
                    data_types=[data_type],
                    applies_to=applies_to,
                    text=text
                )
                
                obligation = Obligation(
                    obligation_id=obligation_id,
                    regulation=regulation,
                    section=section,
                    description=description,
                    data_types=[data_type],
                    applies_to=applies_to,
                    severity=severity,
                    confidence=0.85,  # Rule-based confidence
                    jurisdiction=metadata.get('jurisdiction', 'Global'),
                    effective_date=metadata.get('effective_date')
                )
                
                obligations.append(obligation)
        
        return obligations
    
    def _extract_requirements(
        self,
        text: str,
        regulation: str,
        section: str,
        metadata: Dict[str, Any]
    ) -> List[Obligation]:
        """Extract requirement-type obligations"""
        obligations = []
        text_lower = text.lower()
        
        # Check for requirement patterns
        is_requirement = any(
            re.search(pattern, text_lower)
            for pattern in self.patterns['requirement']
        )
        
        if not is_requirement:
            return obligations
        
        # Extract data types
        data_types = self._extract_data_types(text)
        
        # Extract contexts
        applies_to = self._extract_contexts(text)
        
        # Determine severity
        severity = self._determine_severity(text, data_types)
        
        if data_types:
            # Determine action from text
            action = "PROTECT"
            if 'mask' in text_lower:
                action = "MASK"
            elif 'encrypt' in text_lower:
                action = "ENCRYPT"
            elif 'hash' in text_lower:
                action = "HASH"
            elif 'secure' in text_lower:
                action = "SECURE"
            
            obligation_id = f"{regulation.replace('-', '_')}_{section.replace('.', '_')}_{action}_{data_types[0]}"
            
            description = self._generate_description(
                action_type="requirement",
                data_types=data_types[:2],
                applies_to=applies_to,
                text=text,
                action=action
            )
            
            obligation = Obligation(
                obligation_id=obligation_id,
                regulation=regulation,
                section=section,
                description=description,
                data_types=data_types,
                applies_to=applies_to if applies_to else ["all_contexts"],
                severity=severity,
                confidence=0.82,
                jurisdiction=metadata.get('jurisdiction', 'Global'),
                effective_date=metadata.get('effective_date')
            )
            
            obligations.append(obligation)
        
        return obligations
    
    def _extract_data_types(self, text: str) -> List[str]:
        """Extract mentioned data types"""
        data_types = []
        
        for data_type, pattern in self.patterns['data_types'].items():
            if re.search(pattern, text, re.IGNORECASE):
                data_types.append(data_type)
        
        return data_types
    
    def _extract_contexts(self, text: str) -> List[str]:
        """Extract application contexts"""
        contexts = []
        
        for context, pattern in self.patterns['applies_to'].items():
            if re.search(pattern, text, re.IGNORECASE):
                contexts.append(context)
        
        return contexts
    
    def _determine_severity(self, text: str, data_types: List[str]) -> str:
        """Determine obligation severity"""
        text_lower = text.lower()
        
        # CRITICAL: PAN, CVV in logs/transmission
        if any(dt in ['PAN', 'CVV'] for dt in data_types):
            return 'CRITICAL'
        
        # HIGH: PII exposure, passwords
        if any(dt in ['PII', 'SSN', 'PASSWORD'] for dt in data_types):
            return 'HIGH'
        
        # Check for severity keywords
        if any(word in text_lower for word in ['critical', 'must', 'shall', 'required']):
            return 'HIGH'
        
        if any(word in text_lower for word in ['should', 'recommend']):
            return 'MEDIUM'
        
        return 'MEDIUM'
    
    def _generate_description(
        self,
        action_type: str,
        data_types: List[str],
        applies_to: List[str],
        text: str,
        action: str = None
    ) -> str:
        """Generate human-readable obligation description"""
        
        data_str = ", ".join(data_types) if data_types else "sensitive data"
        context_str = ", ".join(applies_to) if applies_to else "all contexts"
        
        if action_type == "prohibition":
            # Extract first sentence or limit length
            first_sentence = text.split('.')[0][:150]
            return f"{data_str} must not be stored or transmitted in {context_str}. {first_sentence}."
        
        elif action_type == "requirement":
            action_verb = action.lower() if action else "protect"
            return f"{data_str} must be {action_verb}ed in {context_str}. {text.split('.')[0][:150]}."
        
        return text[:200]
    
    async def extract_with_llm(
        self,
        text: str,
        regulation: str,
        section: str
    ) -> List[Obligation]:
        """
        LLM-based extraction (placeholder for future enhancement)
        
        For production: Call Claude/GPT API with extraction prompt
        """
        # Placeholder for LLM integration
        # This would call Anthropic Claude or OpenAI GPT
        
        prompt = self.EXTRACTION_PROMPT.format(
            text=text,
            regulation=regulation,
            section=section
        )
        
        # TODO: Implement LLM API call
        # response = await claude_api.complete(prompt)
        # obligations = parse_llm_response(response)
        
        logger.warning("LLM extraction not implemented - using rule-based fallback")
        return []
