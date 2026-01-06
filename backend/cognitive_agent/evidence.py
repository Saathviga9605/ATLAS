"""
Evidence Generator
Creates audit-ready compliance evidence records
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

from .schemas import Evidence, ReasoningOutput, RemediationResult, SeverityLevel

logger = logging.getLogger(__name__)


class EvidenceGenerator:
    """
    Generates audit-ready evidence for compliance actions
    Critical for enterprise compliance and regulatory audits
    """
    
    def __init__(self):
        """Initialize evidence generator"""
        self.evidence_store: Dict[str, Evidence] = {}
        logger.info("📋 Evidence Generator initialized")
    
    def generate_evidence(
        self,
        violation_id: str,
        reasoning: ReasoningOutput,
        remediation: Optional[RemediationResult] = None
    ) -> Evidence:
        """
        Generate comprehensive evidence record
        
        Args:
            violation_id: Violation identifier
            reasoning: Reasoning output from cognitive agent
            remediation: Remediation result (if action was taken)
            
        Returns:
            Evidence record
        """
        try:
            evidence_id = f"EVID_{uuid.uuid4().hex[:8].upper()}"
            
            # Determine status
            if remediation and remediation.success:
                status = "Resolved"
                action_taken = f"{remediation.action_type}: {remediation.after[:50]}..."
            elif reasoning.autonomy_level.value == "HUMAN_APPROVAL_REQUIRED":
                status = "Escalated"
                action_taken = f"Escalated for approval: {reasoning.recommended_action}"
            else:
                status = "Pending"
                action_taken = f"Recommended: {reasoning.recommended_action}"
            
            # Build remediation details
            remediation_details = None
            if remediation:
                remediation_details = {
                    "action_type": remediation.action_type,
                    "before_sample": remediation.before[:100] + "..." if len(remediation.before) > 100 else remediation.before,
                    "after_sample": remediation.after[:100] + "..." if len(remediation.after) > 100 else remediation.after,
                    "timestamp": remediation.timestamp
                }
            
            evidence = Evidence(
                evidence_id=evidence_id,
                violation_id=violation_id,
                detected_by="ReflexAgent",
                reasoned_by="CognitiveComplianceAgent",
                action_taken=action_taken,
                risk_severity=reasoning.risk_severity,
                regulation_reference=reasoning.regulation_reference,
                timestamp=datetime.utcnow().isoformat() + 'Z',
                status=status,
                remediation_details=remediation_details
            )
            
            # Store evidence
            self.evidence_store[evidence_id] = evidence
            
            logger.info(f"✅ Generated evidence {evidence_id} for {violation_id}")
            
            return evidence
            
        except Exception as e:
            logger.error(f"❌ Evidence generation failed for {violation_id}: {e}")
            raise
    
    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        """Retrieve evidence by ID"""
        return self.evidence_store.get(evidence_id)
    
    def get_all_evidence(self) -> List[Evidence]:
        """Get all evidence records"""
        return list(self.evidence_store.values())
    
    def get_evidence_by_violation(self, violation_id: str) -> List[Evidence]:
        """Get all evidence for a specific violation"""
        return [
            e for e in self.evidence_store.values()
            if e.violation_id == violation_id
        ]
    
    def get_evidence_stats(self) -> Dict[str, Any]:
        """Get evidence statistics for dashboard"""
        total = len(self.evidence_store)
        
        if total == 0:
            return {
                "total_evidence": 0,
                "by_status": {},
                "by_severity": {},
                "resolved_count": 0,
                "pending_count": 0,
                "escalated_count": 0
            }
        
        by_status = {}
        by_severity = {}
        
        for evidence in self.evidence_store.values():
            # Count by status
            status = evidence.status
            by_status[status] = by_status.get(status, 0) + 1
            
            # Count by severity
            severity = evidence.risk_severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "total_evidence": total,
            "by_status": by_status,
            "by_severity": by_severity,
            "resolved_count": by_status.get("Resolved", 0),
            "pending_count": by_status.get("Pending", 0),
            "escalated_count": by_status.get("Escalated", 0)
        }
    
    def export_audit_report(self) -> Dict[str, Any]:
        """
        Export comprehensive audit report
        Enterprise-grade compliance documentation
        """
        return {
            "report_id": f"AUDIT_{uuid.uuid4().hex[:12].upper()}",
            "generated_at": datetime.utcnow().isoformat() + 'Z',
            "statistics": self.get_evidence_stats(),
            "evidence_records": [
                e.model_dump() for e in self.evidence_store.values()
            ],
            "compliance_summary": {
                "critical_violations": len([
                    e for e in self.evidence_store.values()
                    if e.risk_severity == SeverityLevel.CRITICAL
                ]),
                "resolved_rate": self._calculate_resolved_rate(),
                "autonomous_actions": len([
                    e for e in self.evidence_store.values()
                    if e.status == "Resolved"
                ])
            }
        }
    
    def _calculate_resolved_rate(self) -> float:
        """Calculate percentage of resolved violations"""
        total = len(self.evidence_store)
        if total == 0:
            return 0.0
        
        resolved = len([e for e in self.evidence_store.values() if e.status == "Resolved"])
        return round((resolved / total) * 100, 2)
