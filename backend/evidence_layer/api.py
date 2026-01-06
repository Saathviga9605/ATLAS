from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from models.evidence import EvidenceRecord, EventType
from evidence_layer.evidence_service import EvidenceService
from audit_layer.audit_chain_service import AuditChainService

# Initialize services
audit_chain_service = AuditChainService()
evidence_service = EvidenceService(audit_chain_service)

router = APIRouter(prefix="/evidence", tags=["Evidence Layer"])


# Request/Response models
class CaptureEvidenceRequest(BaseModel):
    event_type: EventType
    regulation: Dict[str, Any]
    detection: Dict[str, Any]
    violation_state: Optional[Dict[str, Any]] = None
    remediation: Optional[Dict[str, Any]] = None
    reasoning_chain: Optional[Dict[str, Any]] = None
    linkages: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class CaptureEvidenceResponse(BaseModel):
    evidence_id: str
    message: str


@router.post("/capture", response_model=CaptureEvidenceResponse)
async def capture_evidence(request: CaptureEvidenceRequest):
    """Capture a new evidence record"""
    try:
        evidence = evidence_service.capture_evidence(
            event_type=request.event_type,
            regulation=request.regulation,
            detection=request.detection,
            violation_state=request.violation_state,
            remediation=request.remediation,
            reasoning_chain=request.reasoning_chain,
            linkages=request.linkages,
            metadata=request.metadata
        )
        
        return CaptureEvidenceResponse(
            evidence_id=evidence.evidence_id,
            message="Evidence captured successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{evidence_id}")
async def get_evidence(evidence_id: str):
    """Get evidence by ID"""
    evidence = evidence_service.get_evidence(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    return evidence.model_dump()


@router.get("")
async def list_evidence(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    tenant_id: Optional[str] = Query(None)
):
    """List evidence records, optionally filtered by date range"""
    if start_date and end_date:
        evidence_records = evidence_service.get_evidence_in_range(start_date, end_date, tenant_id)
    else:
        evidence_records = evidence_service.list_all_evidence()
    
    return {
        "count": len(evidence_records),
        "evidence": [e.model_dump() for e in evidence_records]
    }
