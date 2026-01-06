"""
Pydantic models for monitoring agent
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Literal


class IngestRequest(BaseModel):
    """Data ingestion request model"""
    source_type: Literal["transaction", "application_log", "support_chat", "message", "email", "database", "api_request"]
    source_id: str = Field(..., description="Unique identifier for the source")
    content: str = Field(..., description="Text content to analyze")
    timestamp: datetime = Field(..., description="ISO-8601 timestamp of the event")


class RegulationInfo(BaseModel):
    """Regulation information for violation"""
    framework: str = "PCI-DSS"
    clause: str = "PAN Exposure"
    requirement: str = "PAN must not appear in plaintext in logs, messages, or transactions"


class DetectionInfo(BaseModel):
    """Detection details"""
    detected_by: str = "MonitoringAgent"
    source_type: str
    source_id: str
    matched_pattern: str


class ViolationState(BaseModel):
    """Violation state before detection"""
    before: str


class ViolationMetadata(BaseModel):
    """Violation metadata"""
    severity: str = "Critical"
    tenant_id: str = "visa"


class ViolationObject(BaseModel):
    """Complete violation object"""
    event_type: str = "violation"
    regulation: RegulationInfo
    detection: DetectionInfo
    violation_state: ViolationState
    metadata: ViolationMetadata


class ViolationRecord(BaseModel):
    """Stored violation record"""
    violation_id: str
    evidence_id: str
    source_type: str
    source_id: str
    severity: str
    regulation: str
    description: str
    timestamp: datetime


class ViolationsResponse(BaseModel):
    """Response for listing violations"""
    count: int
    tenant_id: str = "visa"
    violations: List[ViolationRecord]
