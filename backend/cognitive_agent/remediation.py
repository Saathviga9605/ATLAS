"""
Remediation Engine
Executes autonomous compliance remediation actions
"""

import logging
import re
from datetime import datetime
from typing import Dict, Any, Tuple

from .schemas import RemediationRequest, RemediationResult

logger = logging.getLogger(__name__)


class RemediationEngine:
    """
    Executes remediation actions for compliance violations
    Proves detect → reason → act workflow
    """
    
    def __init__(self):
        """Initialize remediation engine"""
        logger.info("🔧 Remediation Engine initialized")
        
        # PAN patterns (same as frontend compliance agent)
        self.pan_patterns = [
            r'\b4[0-9]{12}(?:[0-9]{3})?\b',  # VISA
            r'\b(?:5[1-5][0-9]{14}|2(?:2[2-9]|[3-6][0-9]|7[01])[0-9]{12})\b',  # MasterCard
            r'\b3[47][0-9]{13}\b',  # AMEX
            r'\b6(?:011|5[0-9]{2})[0-9]{12}\b',  # Discover
            r'\b[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}\b',  # Generic
        ]
        
        # PII patterns
        self.pii_patterns = {
            'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'PHONE': r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            'CVV': r'\b\d{3,4}\b',  # Simple pattern, context-dependent
        }
    
    async def remediate(self, request: RemediationRequest) -> RemediationResult:
        """
        Execute remediation action
        
        Args:
            request: Remediation request
            
        Returns:
            Remediation result with before/after
        """
        try:
            action_type = request.action_type.lower()
            content = request.content
            
            if action_type == "mask_pan":
                after = self._mask_pan(content)
            elif action_type == "redact_pii":
                after = self._redact_pii(content)
            elif action_type == "mask_ssn":
                after = self._mask_ssn(content)
            elif action_type == "mask_email":
                after = self._mask_email(content)
            elif action_type == "remove_cvv":
                after = self._remove_cvv(content)
            else:
                logger.warning(f"Unknown remediation action: {action_type}")
                after = "[REDACTED]"
            
            result = RemediationResult(
                violation_id=request.violation_id,
                action_type=request.action_type,
                before=content,
                after=after,
                success=True,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            )
            
            logger.info(f"✅ Remediated {request.violation_id} using {action_type}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Remediation failed for {request.violation_id}: {e}")
            raise
    
    def _mask_pan(self, text: str) -> str:
        """Mask Primary Account Numbers (credit cards)"""
        result = text
        
        for pattern in self.pan_patterns:
            matches = re.finditer(pattern, result)
            for match in matches:
                pan = match.group()
                # Clean the PAN (remove spaces and hyphens)
                clean_pan = pan.replace(' ', '').replace('-', '')
                
                # Validate with Luhn algorithm
                if self._luhn_check(clean_pan):
                    # Mask: show last 4 digits
                    masked = '**** **** **** ' + clean_pan[-4:]
                    result = result.replace(pan, masked)
        
        return result
    
    def _mask_ssn(self, text: str) -> str:
        """Mask Social Security Numbers"""
        pattern = self.pii_patterns['SSN']
        
        def mask_ssn_match(match):
            ssn = match.group()
            # Show last 4 digits
            return '***-**-' + ssn[-4:]
        
        return re.sub(pattern, mask_ssn_match, text)
    
    def _mask_email(self, text: str) -> str:
        """Partially mask email addresses"""
        pattern = self.pii_patterns['EMAIL']
        
        def mask_email_match(match):
            email = match.group()
            name, domain = email.split('@')
            # Show first 2 characters of name
            masked_name = name[:2] + '***' if len(name) > 2 else '***'
            return f"{masked_name}@{domain}"
        
        return re.sub(pattern, mask_email_match, text)
    
    def _remove_cvv(self, text: str) -> str:
        """Remove CVV completely (cannot be stored per PCI-DSS)"""
        # This is context-dependent and simplified for demo
        # In production, would need more sophisticated detection
        result = text
        
        # Remove patterns like "CVV 123" or "CVV: 123"
        cvv_context_pattern = r'\b(?:CVV|CVV2|CVC|security\s+code)[\s:]*\d{3,4}\b'
        result = re.sub(cvv_context_pattern, '[CVV REMOVED - PCI-DSS 3.3]', result, flags=re.IGNORECASE)
        
        return result
    
    def _redact_pii(self, text: str) -> str:
        """Redact all PII patterns"""
        result = text
        
        # Mask SSN
        result = self._mask_ssn(result)
        
        # Mask emails
        result = self._mask_email(result)
        
        # Mask phones
        phone_pattern = self.pii_patterns['PHONE']
        result = re.sub(phone_pattern, lambda m: '***-***-' + m.group()[-4:], result)
        
        # Mask PANs
        result = self._mask_pan(result)
        
        return result
    
    def _luhn_check(self, card_number: str) -> bool:
        """
        Validate credit card using Luhn algorithm
        Reduces false positives
        """
        try:
            digits = [int(d) for d in card_number if d.isdigit()]
            
            checksum = 0
            is_even = False
            
            for digit in reversed(digits):
                if is_even:
                    digit *= 2
                    if digit > 9:
                        digit -= 9
                checksum += digit
                is_even = not is_even
            
            return checksum % 10 == 0
        except:
            return False
    
    def get_supported_actions(self) -> list:
        """Get list of supported remediation actions"""
        return [
            "mask_pan",
            "mask_ssn",
            "mask_email",
            "remove_cvv",
            "redact_pii"
        ]
