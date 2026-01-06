"""
Pydantic schemas for Cognitive Compliance Agent
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    """Risk severity levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class AutonomyLevel(str, Enum):
    """Action autonomy levels"""
    AUTONOMOUS = "AUTONOMOUS"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"


class ViolationType(str, Enum):
    """Types of violations"""
    PAN_DETECTED = "PAN_DETECTED"
    CVV_DETECTED = "CVV_DETECTED"
    PII_EXPOSED = "PII_EXPOSED"
    SSN_DETECTED = "SSN_DETECTED"
    UNENCRYPTED_DATA = "UNENCRYPTED_DATA"
    POLICY_VIOLATION = "POLICY_VIOLATION"


class ViolationInput(BaseModel):
    """Input for cognitive reasoning"""
    violation_id: str = Field(..., description="Unique violation identifier")
    violation_type: ViolationType = Field(..., description="Type of violation")
    content: str = Field(..., description="Content containing the violation")
    source: str = Field(..., description="Source of violation (e.g., support_chat, log_file)")
    regulation_context: str = Field(..., description="Relevant regulation text")
    goal_description: Optional[str] = Field(
        "Ensure PCI-DSS compliance for payment card data protection",
        description="Compliance goal"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "violation_id": "VIOL_123",
                "violation_type": "PAN_DETECTED",
                "content": "Customer card number is 4111 1111 1111 1111",
                "source": "support_chat",
                "regulation_context": "PCI-DSS 3.2.1: PAN must not be stored or transmitted in plaintext.",
                "goal_description": "Protect stored cardholder data"
            }
        }


class ReasoningOutput(BaseModel):
    """Output from cognitive reasoning"""
    violation_id: str
    is_violation: bool
    explanation: str
    regulation_reference: str
    risk_severity: SeverityLevel
    recommended_action: str
    autonomy_level: AutonomyLevel
    reasoning_timestamp: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "violation_id": "VIOL_123",
                "is_violation": True,
                "explanation": "PAN is exposed in plaintext within customer communication, violating PCI-DSS requirements.",
                "regulation_reference": "PCI-DSS 3.2.1",
                "risk_severity": "Critical",
                "recommended_action": "Mask PAN and remove plaintext exposure",
                "autonomy_level": "AUTONOMOUS",
                "reasoning_timestamp": "2026-01-04T17:45:00Z"
            }
        }


class RemediationRequest(BaseModel):
    """Request for remediation action"""
    violation_id: str
    action_type: str = Field(..., description="Type of remediation (mask_pan, redact_pii, etc.)")
    content: str = Field(..., description="Content to remediate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "violation_id": "VIOL_123",
                "action_type": "mask_pan",
                "content": "Customer card number is 4111 1111 1111 1111"
            }
        }


class RemediationResult(BaseModel):
    """Result of remediation action"""
    violation_id: str
    action_type: str
    before: str
    after: str
    success: bool
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "violation_id": "VIOL_123",
                "action_type": "mask_pan",
                "before": "4111 1111 1111 1111",
                "after": "**** **** **** 1111",
                "success": True,
                "timestamp": "2026-01-04T17:45:00Z"
            }
        }


class Evidence(BaseModel):
    """Audit-ready evidence record"""
    evidence_id: str
    violation_id: str
    detected_by: str = Field(default="ReflexAgent", description="Agent that detected the violation")
    reasoned_by: str = Field(default="CognitiveComplianceAgent", description="Agent that reasoned about it")
    action_taken: str
    risk_severity: SeverityLevel
    regulation_reference: str
    timestamp: str
    status: str = Field(..., description="Resolved, Pending, Escalated")
    remediation_details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "evidence_id": "EVID_123",
                "violation_id": "VIOL_123",
                "detected_by": "ReflexAgent",
                "reasoned_by": "CognitiveComplianceAgent",
                "action_taken": "PAN masked",
                "risk_severity": "Critical",
                "regulation_reference": "PCI-DSS 3.2.1",
                "timestamp": "2026-01-04T17:45:00Z",
                "status": "Resolved"
            }
        }


class AgentActivity(BaseModel):
    """Agent activity log entry"""
    activity_id: str
    timestamp: str
    agent_name: str
    action: str
    violation_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "activity_id": "ACT_456",
                "timestamp": "2026-01-04T17:45:00Z",
                "agent_name": "CognitiveComplianceAgent",
                "action": "Reasoned about PAN violation",
                "violation_id": "VIOL_123",
                "details": {"severity": "Critical", "autonomy": "AUTONOMOUS"}
            }
        }
