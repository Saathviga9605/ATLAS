"""
Multi-Regulation Violation Detection Engine
Supports PCI-DSS (PAN), GDPR (PII), CCPA (Personal Info)
Deterministic regex-based detection with validation
"""
import re
from typing import Optional, List, Dict, Any


class PANDetector:
    """Detects unmasked PAN (16-digit card numbers) in text"""
    
    # Regex pattern for 16-digit sequences with optional spaces/dashes
    # Matches patterns like: 4111111111111111, 4111-1111-1111-1111, 4111 1111 1111 1111
    PAN_PATTERN = re.compile(r'\b(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4})\b')
    
    # Pattern to identify masked PANs (e.g., **** **** **** 1234)
    MASKED_PATTERN = re.compile(r'[\*]{4}[\s\-]?[\*]{4}[\s\-]?[\*]{4}[\s\-]?\d{4}')
    
    @staticmethod
    def luhn_check(card_number: str) -> bool:
        """
        Validate card number using Luhn algorithm
        Returns True if valid, False otherwise
        """
        # Remove spaces and dashes
        digits = card_number.replace(' ', '').replace('-', '')
        
        if not digits.isdigit() or len(digits) != 16:
            return False
        
        # Luhn algorithm
        total = 0
        reverse_digits = digits[::-1]
        
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:  # Every second digit from right
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        
        return total % 10 == 0
    
    def detect(self, text: str) -> Optional[str]:
        """
        Detect unmasked PAN in text
        
        Args:
            text: Input text to scan
            
        Returns:
            Matched PAN string if found, None otherwise
        """
        # First check if text contains masked PANs - if so, it's intentionally masked
        if self.MASKED_PATTERN.search(text):
            return None
        
        # Search for potential PANs
        matches = self.PAN_PATTERN.findall(text)
        
        for match in matches:
            # Validate with Luhn check
            if self.luhn_check(match):
                return match
        
        return None
    
    def detect_all(self, text: str) -> List[str]:
        """
        Detect all unmasked PANs in text
        
        Args:
            text: Input text to scan
            
        Returns:
            List of matched PAN strings
        """
        if self.MASKED_PATTERN.search(text):
            return []
        
        matches = self.PAN_PATTERN.findall(text)
        valid_pans = []
        
        for match in matches:
            if self.luhn_check(match):
                valid_pans.append(match)
        
        return valid_pans


class GDPRDetector:
    """Detects GDPR-relevant PII (emails, phone numbers, IP addresses)"""
    
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    IP_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    
    def detect(self, text: str) -> Optional[Dict[str, Any]]:
        """Detect GDPR-relevant PII in text"""
        findings = {}
        
        emails = self.EMAIL_PATTERN.findall(text)
        if emails:
            findings['emails'] = emails
        
        phones = self.PHONE_PATTERN.findall(text)
        if phones:
            findings['phone_numbers'] = phones
        
        ips = self.IP_PATTERN.findall(text)
        if ips:
            findings['ip_addresses'] = ips
        
        return findings if findings else None


class CCPADetector:
    """Detects CCPA-relevant personal information"""
    
    SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    DL_PATTERN = re.compile(r'\b[A-Z]{1,2}\d{5,8}\b')  # Driver's license
    
    def detect(self, text: str) -> Optional[Dict[str, Any]]:
        """Detect CCPA-relevant personal information"""
        findings = {}
        
        ssns = self.SSN_PATTERN.findall(text)
        if ssns:
            findings['ssn'] = ssns
        
        dl_numbers = self.DL_PATTERN.findall(text)
        if dl_numbers:
            findings['drivers_license'] = dl_numbers
        
        return findings if findings else None


class MultiRegulationDetector:
    """Unified detector for all regulations"""
    
    def __init__(self):
        self.pan_detector = PANDetector()
        self.gdpr_detector = GDPRDetector()
        self.ccpa_detector = CCPADetector()
    
    def detect_all(self, text: str) -> Dict[str, Any]:
        """
        Detect violations across all regulations
        
        Returns dict with structure:
        {
            'PCI-DSS': { 'pan': '4111...' },
            'GDPR': { 'emails': [...], 'phones': [...] },
            'CCPA': { 'ssn': [...] }
        }
        """
        results = {}
        
        # PCI-DSS (PAN detection)
        pan = self.pan_detector.detect(text)
        if pan:
            results['PCI-DSS'] = {'pan': pan, 'severity': 'CRITICAL'}
        
        # GDPR (PII detection)
        gdpr_findings = self.gdpr_detector.detect(text)
        if gdpr_findings:
            results['GDPR'] = {**gdpr_findings, 'severity': 'HIGH'}
        
        # CCPA (Personal info detection)
        ccpa_findings = self.ccpa_detector.detect(text)
        if ccpa_findings:
            results['CCPA'] = {**ccpa_findings, 'severity': 'HIGH'}
        
        return results
