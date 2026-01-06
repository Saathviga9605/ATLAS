from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import Response
from datetime import datetime
from typing import Optional

from audit_layer.audit_chain_service import AuditChainService
from evidence_layer.evidence_service import EvidenceService
from evidence_layer.explanation_service import ExplanationService
from audit_layer.audit_bundle_service import AuditBundleService

# Initialize services
audit_chain_service = AuditChainService()
explanation_service = ExplanationService()
evidence_service = EvidenceService(audit_chain_service)
audit_bundle_service = AuditBundleService(audit_chain_service, explanation_service)

router = APIRouter(prefix="/audit", tags=["Audit Layer"])


@router.get("/trail")
async def get_audit_trail(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """Get audit trail (hash chain)"""
    if start_date and end_date:
        chain_nodes = audit_chain_service.get_chain_in_range(start_date, end_date)
    else:
        chain_nodes = audit_chain_service.get_all_nodes()
    
    return {
        "count": len(chain_nodes),
        "chain": [node.model_dump() for node in chain_nodes]
    }


@router.get("/verify")
async def verify_audit_trail():
    """Verify audit trail integrity"""
    verification = audit_chain_service.verify_chain()
    return verification


@router.get("/explanation/{evidence_id}")
async def get_explanation(evidence_id: str):
    """Get explanation for evidence record"""
    evidence = evidence_service.get_evidence(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    explanation = explanation_service.generate_explanation(evidence)
    return explanation.model_dump()


@router.post("/generate-bundle")
async def generate_audit_bundle(
    tenant_id: str = Query(..., description="Tenant identifier"),
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date")
):
    """Generate audit bundle ZIP file"""
    # Get evidence in range
    evidence_records = evidence_service.get_evidence_in_range(start_date, end_date, tenant_id)
    
    if not evidence_records:
        raise HTTPException(status_code=404, detail="No evidence found in date range")
    
    # Generate bundle
    bundle_bytes = audit_bundle_service.generate_bundle(
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
        evidence_records=evidence_records
    )
    
    filename = f"audit_bundle_{tenant_id}_{start_date.date()}_{end_date.date()}.zip"
    
    return Response(
        content=bundle_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
