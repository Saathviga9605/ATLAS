"""
FastAPI routes for Monitoring & Violation Detection Agent
Endpoints:
- GET /health
- POST /monitor/ingest
- GET /monitor/violations
"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from .models import (
    IngestRequest,
    ViolationObject,
    ViolationMetadata,
    RegulationInfo,
    DetectionInfo,
    ViolationState,
    ViolationsResponse
)
from .detectors import PANDetector, MultiRegulationDetector
from .evidence_client import EvidenceClient
from .store import ViolationStore


# Initialize components
router = APIRouter(prefix="/monitor", tags=["Monitoring Agent"])
pan_detector = PANDetector()
multi_detector = MultiRegulationDetector()
evidence_client = EvidenceClient()
violation_store = ViolationStore(data_dir="data")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Monitoring & Violation Detection Agent",
        "version": "1.0.0",
        "capabilities": ["PCI-DSS PAN Detection"]
    }


@router.post("/ingest")
async def ingest_data(request: IngestRequest):
    """
    Ingest data for real-time violation detection
    
    Detects violations across PCI-DSS, GDPR, and CCPA and creates evidence records
    """
    try:
        # Detect violations across all regulations
        findings = multi_detector.detect_all(request.content)
        
        if not findings:
            # Store compliant record in history
            compliant_record = violation_store.add_compliant_record(
                source_type=request.source_type,
                source_id=request.source_id,
                timestamp=request.timestamp
            )
            
            return {
                "status": "no_violation",
                "message": "No violations detected",
                "source_id": request.source_id,
                "violation_id": compliant_record.violation_id,
                "is_violation": False,
                "risk_severity": "None",
                "autonomy_level": "AUTONOMOUS",
                "explanation": "Content scanned across PCI-DSS, GDPR, and CCPA regulations. No sensitive data exposure or compliance violations detected.",
                "regulation_reference": "Multi-regulation scan: PCI-DSS (PAN), GDPR (PII), CCPA (Personal Information) - All compliant",
                "recommended_action": "No action required. Content is compliant with all scanned regulations.",
                "detected_data": None
            }
        
        # Create violation for the first (most critical) finding
        # Priority: PCI-DSS > GDPR > CCPA
        regulation = None
        details = None
        severity = "HIGH"
        
        if 'PCI-DSS' in findings:
            regulation = 'PCI-DSS'
            details = findings['PCI-DSS']
            severity = details.pop('severity', 'CRITICAL')
        elif 'GDPR' in findings:
            regulation = 'GDPR'
            details = findings['GDPR']
            severity = details.pop('severity', 'HIGH')
        elif 'CCPA' in findings:
            regulation = 'CCPA'
            details = findings['CCPA']
            severity = details.pop('severity', 'HIGH')
        
        # Generate description based on detected data type
        description = _generate_description(regulation, details)
        matched_pattern = str(details)
        
        # Create violation object
        violation = ViolationObject(
            event_type="violation",
            regulation=RegulationInfo(
                framework=regulation,
                clause=_get_clause(regulation, details),
                requirement=_get_requirement(regulation, details)
            ),
            detection=DetectionInfo(
                detected_by="MonitoringAgent",
                source_type=request.source_type,
                source_id=request.source_id,
                matched_pattern=matched_pattern
            ),
            violation_state=ViolationState(
                before=request.content
            ),
            metadata=ViolationMetadata(
                severity=severity,
                tenant_id="visa"
            )
        )
        
        # Capture evidence via API
        evidence_response = await evidence_client.capture_evidence(violation)
        evidence_id = evidence_response["evidence_id"]
        
        # Store violation in JSON file
        violation_record = violation_store.add_violation(
            evidence_id=evidence_id,
            source_type=request.source_type,
            source_id=request.source_id,
            severity=severity,
            regulation=regulation,
            description=description,
            timestamp=request.timestamp
        )
        
        return {
            "status": "violation_detected",
            "violation_id": violation_record.violation_id,
            "evidence_id": evidence_id,
            "severity": severity,
            "message": f"{regulation} violation detected and evidence captured",
            "is_violation": True,
            "risk_severity": severity,
            "autonomy_level": "AUTONOMOUS",
            "explanation": description,
            "regulation_reference": _get_requirement(regulation, details),
            "recommended_action": _get_recommended_action(regulation, details),
            "detected_data": _mask_sensitive_data(matched_pattern)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing data: {str(e)}"
        )


@router.get("/violations", response_model=ViolationsResponse)
async def list_violations():
    """
    List all detected violations
    
    Reads from violations.json file
    """
    try:
        violations = violation_store.list_violations()
        tenant_id = violation_store.get_tenant_id()
        
        return ViolationsResponse(
            count=len(violations),
            tenant_id=tenant_id,
            violations=violations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving violations: {str(e)}"
        )


@router.post("/scan-multi")
async def scan_multi_regulation(request: IngestRequest):
    """
    Scan content across multiple regulations (PCI-DSS, GDPR, CCPA)
    
    Returns all detected violations across all frameworks
    """
    try:
        # Detect violations across all regulations
        findings = multi_detector.detect_all(request.content)
        
        if not findings:
            return {
                "status": "compliant",
                "message": "No violations detected",
                "regulations_scanned": ["PCI-DSS", "GDPR", "CCPA"]
            }
        
        # Create violations for each finding
        violations = []
        
        for regulation, details in findings.items():
            severity = details.pop('severity', 'HIGH')
            
            # Create violation object
            violation = ViolationObject(
                event_type="violation",
                regulation=RegulationInfo(
                    framework=regulation,
                    clause="Data Protection",
                    requirement=f"{regulation} compliance violation"
                ),
                detection=DetectionInfo(
                    detected_by="MultiRegulationAgent",
                    source_type=request.source_type,
                    source_id=request.source_id,
                    matched_pattern=str(details)
                ),
                violation_state=ViolationState(
                    before=request.content
                ),
                metadata=ViolationMetadata(
                    severity=severity,
                    tenant_id="visa"
                )
            )
            
            # Capture evidence
            evidence_response = await evidence_client.capture_evidence(violation)
            evidence_id = evidence_response["evidence_id"]
            
            # Store violation
            violation_record = violation_store.add_violation(
                evidence_id=evidence_id,
                source_type=request.source_type,
                source_id=request.source_id,
                severity=severity,
                regulation=regulation,
                description=f"{regulation} violation: {list(details.keys())}",
                timestamp=request.timestamp
            )
            
            violations.append({
                "violation_id": violation_record.violation_id,
                "regulation": regulation,
                "severity": severity,
                "findings": details
            })
        
        return {
            "status": "violations_detected",
            "count": len(violations),
            "violations": violations,
            "message": f"Detected {len(violations)} violations across {len(findings)} regulations"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in multi-regulation scan: {str(e)}"
        )


def _generate_description(regulation: str, details: dict) -> str:
    """Generate human-readable description based on detected data type"""
    if regulation == 'PCI-DSS':
        if 'pan' in details:
            return "PAN (Primary Account Number) exposed in plaintext"
    elif regulation == 'GDPR':
        if 'emails' in details:
            return f"Email address(es) exposed: {len(details['emails'])} found"
        elif 'phone_numbers' in details:
            return f"Phone number(s) exposed: {len(details['phone_numbers'])} found"
        elif 'ip_addresses' in details:
            return f"IP address(es) exposed: {len(details['ip_addresses'])} found"
    elif regulation == 'CCPA':
        if 'ssn' in details:
            return f"SSN (Social Security Number) exposed: {len(details['ssn'])} found"
        elif 'drivers_license' in details:
            return f"Driver's license number(s) exposed: {len(details['drivers_license'])} found"
    
    return f"{regulation} violation: {list(details.keys())}"


def _get_clause(regulation: str, details: dict) -> str:
    """Get regulation clause based on violation type"""
    if regulation == 'PCI-DSS':
        return "PAN Exposure"
    elif regulation == 'GDPR':
        if 'emails' in details:
            return "Article 5 - Personal Data Protection"
        elif 'phone_numbers' in details:
            return "Article 5 - Personal Data Protection"
        return "Personal Data Protection"
    elif regulation == 'CCPA':
        return "Section 1798.100 - Consumer Privacy Rights"
    return "Data Protection"


def _get_requirement(regulation: str, details: dict) -> str:
    """Get regulation requirement text"""
    if regulation == 'PCI-DSS':
        return "PCI-DSS 3.2.1: PAN must not appear in plaintext in logs, messages, or transactions"
    elif regulation == 'GDPR':
        if 'emails' in details:
            return "GDPR Article 5: Personal data must be processed lawfully, fairly, and in a transparent manner"
        elif 'phone_numbers' in details:
            return "GDPR Article 5: Personal identifiers must be protected and not exposed in plaintext"
        return "GDPR: Personal data must be protected"
    elif regulation == 'CCPA':
        return "CCPA Section 1798.100: Consumers have the right to know what personal information is collected"
    return f"{regulation} compliance requirement"


def _get_recommended_action(regulation: str, details: dict) -> str:
    """Get recommended remediation action"""
    if regulation == 'PCI-DSS':
        return "Immediately mask or remove PAN from the source. Implement tokenization or encryption for card data."
    elif regulation == 'GDPR':
        if 'emails' in details:
            return "Remove or pseudonymize email addresses. Ensure proper consent and data processing agreements."
        elif 'phone_numbers' in details:
            return "Remove or mask phone numbers. Verify legitimate processing basis."
        return "Remove or pseudonymize personal data. Review data processing basis."
    elif regulation == 'CCPA':
        return "Remove or pseudonymize personal information. Ensure consumer disclosure and opt-out mechanisms."
    return "Review and remediate data exposure according to regulation requirements."


def _mask_sensitive_data(data: str) -> str:
    """Mask sensitive data for display"""
    # Simple masking - replace middle characters
    if len(data) > 8:
        return data[:4] + "*" * (len(data) - 8) + data[-4:]
    return "***MASKED***"


@router.get("/stats")
async def get_stats():
    """Get monitoring statistics"""
    try:
        violations = violation_store.list_violations()
        
        # Count by regulation
        by_regulation = {}
        by_severity = {}
        
        for v in violations:
            reg = v.regulation
            sev = v.severity
            
            by_regulation[reg] = by_regulation.get(reg, 0) + 1
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        return {
            "total_violations": len(violations),
            "by_regulation": by_regulation,
            "by_severity": by_severity,
            "regulations_monitored": ["PCI-DSS", "GDPR", "CCPA"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stats: {str(e)}"
        )
