"""
Cognitive Reasoning Engine
LLM-driven compliance reasoning using Claude Sonnet
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
    Uses Claude Sonnet 4.5 for intelligent decision-making
    """
    
    def __init__(self, anthropic_api_key: str = None):
        """Initialize cognitive reasoner"""
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        
        # Load prompt template
        prompt_path = Path(__file__).parent / "prompts" / "compliance_reasoning.txt"
        with open(prompt_path, 'r') as f:
            self.prompt_template = f.read()
        
        logger.info("🧠 Cognitive Reasoner initialized")
    
    async def reason_about_violation(self, violation: ViolationInput) -> ReasoningOutput:
        """
        Reason about a compliance violation using Claude
        
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
                regulation_context=violation.regulation_context,
                goal_description=violation.goal_description
            )
            
            # Call Claude API
            response = await self._call_claude(prompt)
            
            # Parse JSON response
            reasoning_data = self._parse_claude_response(response)
            
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
    
    async def _call_claude(self, prompt: str) -> str:
        """
        Call Claude API
        
        For MVP: Mock implementation
        In production: Use anthropic SDK
        """
        # For MVP/demo, use rule-based mock response
        # In production, uncomment:
        """
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
        """
        
        # Mock response for demo
        return self._mock_claude_response(prompt)
    
    def _mock_claude_response(self, prompt: str) -> str:
        """
        Mock Claude response for demo purposes
        Simulates LLM reasoning
        """
        # Extract violation details from prompt
        if "PAN" in prompt or "card number" in prompt.lower():
            return json.dumps({
                "is_violation": True,
                "explanation": "The detected content contains a Primary Account Number (PAN) exposed in plaintext within customer communication, which is explicitly prohibited by PCI-DSS. This poses a critical risk of unauthorized access to payment card data.",
                "regulation_reference": "PCI-DSS 3.2.1, 4.2",
                "risk_severity": "Critical",
                "recommended_action": "Immediately mask the PAN in the communication. Replace plaintext card number with masked format (showing only last 4 digits). Remove the original content from all records and logs. Alert security team for incident review.",
                "autonomy_level": "AUTONOMOUS"
            })
        
        elif "CVV" in prompt or "cvv" in prompt.lower():
            return json.dumps({
                "is_violation": True,
                "explanation": "Card Verification Value (CVV) detected in plaintext. PCI-DSS explicitly prohibits storage of CVV/CVV2/CVC after transaction authorization under any circumstances.",
                "regulation_reference": "PCI-DSS 3.3",
                "risk_severity": "Critical",
                "recommended_action": "Immediately delete the CVV data. This cannot be masked or encrypted - it must be permanently removed. Escalate to security team.",
                "autonomy_level": "HUMAN_APPROVAL_REQUIRED"
            })
        
        elif "SSN" in prompt or "social security" in prompt.lower():
            return json.dumps({
                "is_violation": True,
                "explanation": "Social Security Number (SSN) detected in plaintext, violating data privacy requirements and GDPR Article 32 (if applicable). This constitutes Personally Identifiable Information (PII) that requires protection.",
                "regulation_reference": "GDPR Article 32, Internal Policy - PII Protection",
                "risk_severity": "High",
                "recommended_action": "Mask the SSN showing only last 4 digits. Implement encryption for storage. Review access logs to determine exposure scope.",
                "autonomy_level": "AUTONOMOUS"
            })
        
        elif "email" in prompt.lower() or "@" in prompt:
            return json.dumps({
                "is_violation": True,
                "explanation": "Email address detected in unprotected context. While not as severe as payment data, this constitutes PII under GDPR and requires appropriate handling.",
                "regulation_reference": "GDPR Article 5(1)(f), Article 32",
                "risk_severity": "Medium",
                "recommended_action": "Partially mask email address (show first 2 characters and domain). Ensure proper access controls are in place.",
                "autonomy_level": "AUTONOMOUS"
            })
        
        else:
            return json.dumps({
                "is_violation": False,
                "explanation": "No compliance violations detected in the provided content based on available regulatory context.",
                "regulation_reference": "N/A",
                "risk_severity": "Low",
                "recommended_action": "Continue monitoring. No action required at this time.",
                "autonomy_level": "AUTONOMOUS"
            })
    
    def _parse_claude_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate Claude's JSON response"""
        try:
            # Extract JSON from response
            # Claude might wrap it in markdown
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            
            data = json.loads(response)
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response: {e}")
            raise ValueError(f"Invalid JSON response from Claude: {response}")
    
    def _fallback_reasoning(self, violation: ViolationInput) -> ReasoningOutput:
        """
        Fallback rule-based reasoning if LLM fails
        """
        logger.warning(f"Using fallback reasoning for {violation.violation_id}")
        
        # Simple rule-based logic
        is_violation = True
        severity = SeverityLevel.HIGH
        autonomy = AutonomyLevel.AUTONOMOUS
        
        if violation.violation_type.value == "PAN_DETECTED":
            severity = SeverityLevel.CRITICAL
            explanation = "PAN detected in plaintext - PCI-DSS violation"
            regulation_ref = "PCI-DSS 3.2.1"
            action = "Mask PAN immediately"
        elif violation.violation_type.value == "CVV_DETECTED":
            severity = SeverityLevel.CRITICAL
            autonomy = AutonomyLevel.HUMAN_APPROVAL_REQUIRED
            explanation = "CVV storage prohibited by PCI-DSS"
            regulation_ref = "PCI-DSS 3.3"
            action = "Delete CVV data immediately"
        else:
            explanation = "Potential compliance violation detected"
            regulation_ref = "General Policy"
            action = "Review and remediate"
        
        return ReasoningOutput(
            violation_id=violation.violation_id,
            is_violation=is_violation,
            explanation=explanation,
            regulation_reference=regulation_ref,
            risk_severity=severity,
            recommended_action=action,
            autonomy_level=autonomy,
            reasoning_timestamp=datetime.utcnow().isoformat() + 'Z'
        )
