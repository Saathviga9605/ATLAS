"""
Cognitive Reasoning Engine
LLM-driven compliance reasoning via OpenRouter (model-agnostic)
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from .schemas import ViolationInput, ReasoningOutput, SeverityLevel, AutonomyLevel

logger = logging.getLogger(__name__)


class CognitiveReasoner:
    """
    LLM-powered reasoning engine for compliance violations
    Uses OpenRouter API for model-agnostic LLM access
    Supports Claude, GPT, and other frontier models
    """
    
    def __init__(self, openrouter_api_key: str = None):
        """Initialize cognitive reasoner with OpenRouter"""
        self.api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4")
        
        # Load prompt template
        prompt_path = Path(__file__).parent / "prompts" / "reasoning.txt"
        if prompt_path.exists():
            with open(prompt_path, 'r') as f:
                self.prompt_template = f.read()
        else:
            self.prompt_template = self._get_default_prompt()
        
        logger.info(f"🧠 Cognitive Reasoner initialized (OpenRouter: {self.model})")
    
    async def reason_about_violation(self, violation: ViolationInput) -> ReasoningOutput:
        """
        Reason about a compliance violation using LLM via OpenRouter
        
        Args:
            violation: Violation input data
            
        Returns:
            Structured reasoning output
        """
        try:
            # Format prompt with violation data
            prompt = self.prompt_template.format(
                violation_id=violation.violation_id,
                violation_type=violation.violation_type.value,
                content=violation.content,
                source=violation.source,
                regulation_context=violation.regulation_context or "PCI-DSS: Protect cardholder data",
                goal_description=violation.goal_description or "Prevent PAN exposure"
            )
            
            # Call LLM via OpenRouter
            response = await self._call_openrouter(prompt)
            
            # Parse JSON response
            reasoning_data = self._parse_llm_response(response)
            
            # Add timestamp
            reasoning_data['reasoning_timestamp'] = datetime.utcnow().isoformat() + 'Z'
            
            # Validate and return
            output = ReasoningOutput(**reasoning_data)
            
            logger.info(f"✅ Reasoned about {violation.violation_id}: {output.risk_severity} - {output.autonomy_level}")
            
            return output
            
        except Exception as e:
            logger.error(f"❌ Reasoning failed for {violation.violation_id}: {e}")
            # Fallback to rule-based reasoning
            return self._fallback_reasoning(violation)
    
    async def _call_openrouter(self, prompt: str) -> str:
        """
        Call OpenRouter API for LLM inference
        
        For MVP: Mock implementation
        In production: Use httpx to call OpenRouter
        """
        # For MVP/demo, use rule-based mock response
        # In production, uncomment:
        """
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://visa-compliance.ai",
                    "X-Title": "Visa Compliance AI"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1024,
                    "temperature": 0.3
                }
            )
            
            return response.json()["choices"][0]["message"]["content"]
        """
        
        # Mock response for demo
        return self._mock_llm_response(prompt)
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response"""
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            raise
    
    def _mock_llm_response(self, prompt: str) -> str:
        """Generate mock LLM response for demo"""
        # Intelligent rule-based mock based on prompt content
        if "PAN" in prompt.upper() or "4111" in prompt:
            return json.dumps({
                "is_violation": True,
                "explanation": "PCI-DSS prohibits storage of Primary Account Numbers (PAN) in plaintext. The detected pattern matches a valid credit card number format, exposing sensitive cardholder data. This violates PCI-DSS Requirement 3.2.1 which mandates secure cryptographic storage of PAN.",
                "risk_severity": "Critical",
                "recommended_action": "Immediately mask the PAN using a secure tokenization or encryption method. Replace the first 12 digits with asterisks, preserving only the last 4 digits for reference.",
                "autonomy_level": "AUTONOMOUS",
                "confidence_score": 0.95,
                "regulation_references": [
                    "PCI-DSS 3.2.1: Mask PAN when displayed",
                    "PCI-DSS 3.4: Render PAN unreadable"
                ]
            })
        elif "SSN" in prompt.upper() or "SOCIAL SECURITY" in prompt.upper():
            return json.dumps({
                "is_violation": True,
                "explanation": "The content contains a Social Security Number, which is classified as Personally Identifiable Information (PII) under GDPR and must be protected from unauthorized access and storage.",
                "risk_severity": "High",
                "recommended_action": "Redact the SSN and implement access controls. Only authorized personnel should have access to unmasked SSNs.",
                "autonomy_level": "REQUIRES_APPROVAL",
                "confidence_score": 0.92,
                "regulation_references": [
                    "GDPR Article 5: Principles of data processing",
                    "GDPR Article 32: Security of processing"
                ]
            })
        else:
            return json.dumps({
                "is_violation": False,
                "explanation": "No clear compliance violation detected in the provided content. The data appears to be within acceptable parameters for PCI-DSS and PII protection standards.",
                "risk_severity": "Low",
                "recommended_action": "Continue monitoring. No immediate action required.",
                "autonomy_level": "NO_ACTION",
                "confidence_score": 0.78,
                "regulation_references": []
            })
    
    def _fallback_reasoning(self, violation: ViolationInput) -> ReasoningOutput:
        """Fallback rule-based reasoning when LLM fails"""
        logger.warning(f"Using fallback reasoning for {violation.violation_id}")
        
        # Simple rule-based logic
        is_pan = "PAN" in violation.violation_type.value
        
        return ReasoningOutput(
            is_violation=True,
            explanation=f"Detected {violation.violation_type.value} violation. Fallback reasoning applied due to LLM unavailability.",
            risk_severity=SeverityLevel.CRITICAL if is_pan else SeverityLevel.HIGH,
            recommended_action="Mask sensitive data immediately",
            autonomy_level=AutonomyLevel.AUTONOMOUS,
            confidence_score=0.85,
            regulation_references=["PCI-DSS 3.2.1"],
            reasoning_timestamp=datetime.utcnow().isoformat() + 'Z'
        )
    
    def _get_default_prompt(self) -> str:
        """Default prompt template if file not found"""
        return """You are a compliance reasoning AI specialized in PCI-DSS and PII protection.

Analyze this compliance violation:

Violation ID: {violation_id}
Type: {violation_type}
Content: {content}
Source: {source}
Regulation Context: {regulation_context}
Goal: {goal_description}

Provide a structured JSON response with:
- is_violation (boolean)
- explanation (string): Why this is/isn't a violation
- risk_severity (Critical/High/Medium/Low)
- recommended_action (string): What should be done
- autonomy_level (AUTONOMOUS/REQUIRES_APPROVAL/NO_ACTION)
- confidence_score (0-1)
- regulation_references (list of strings)

Output only valid JSON, no markdown."""
