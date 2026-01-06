"""
FastAPI Routes for Cognitive Compliance Agent
Exposes reasoning, remediation, and evidence APIs
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging
from datetime import datetime
import uuid

from .schemas import (
    ViolationInput,
    ReasoningOutput,
    RemediationRequest,
    RemediationResult,
    Evidence,
    AgentActivity
)
from .reasoner_openrouter import CognitiveReasoner
from .remediation import RemediationEngine
from .evidence import EvidenceGenerator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/agent", tags=["Cognitive Agent"])

# Initialize services
reasoner = CognitiveReasoner()
remediation_engine = RemediationEngine()
evidence_generator = EvidenceGenerator()

# Activity log
activity_log: List[AgentActivity] = []


def log_activity(action: str, violation_id: str = None, details: Dict[str, Any] = None):
    """Log agent activity"""
    activity = AgentActivity(
        activity_id=f"ACT_{uuid.uuid4().hex[:8].upper()}",
        timestamp=datetime.utcnow().isoformat() + 'Z',
        agent_name="CognitiveComplianceAgent",
        action=action,
        violation_id=violation_id,
        details=details
    )
    activity_log.append(activity)
    logger.info(f"📊 Activity logged: {action}")


@router.post("/reason", response_model=ReasoningOutput)
async def reason_about_violation(violation: ViolationInput):
    """
    Cognitive reasoning endpoint
    
    Receives a detected violation and reasons about it using LLM
    
    Returns:
        - Explanation of why it's a violation
        - Regulation reference
        - Risk severity
        - Recommended action
        - Autonomy level
    """
    try:
        logger.info(f"🧠 Reasoning about violation: {violation.violation_id}")
        
        # Perform cognitive reasoning
        reasoning = await reasoner.reason_about_violation(violation)
        
        # Log activity
        log_activity(
            action=f"Reasoned about {violation.violation_type.value} violation",
            violation_id=violation.violation_id,
            details={
                "severity": reasoning.risk_severity.value,
                "autonomy": reasoning.autonomy_level.value,
                "is_violation": reasoning.is_violation
            }
        )
        
        # Generate evidence (without remediation yet)
        evidence_generator.generate_evidence(
            violation_id=violation.violation_id,
            reasoning=reasoning,
            remediation=None
        )
        
        return reasoning
        
    except Exception as e:
        logger.error(f"❌ Reasoning failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reasoning failed: {str(e)}")


@router.post("/remediate", response_model=RemediationResult)
async def execute_remediation(request: RemediationRequest):
    """
    Execute remediation action
    
    Takes action to fix a compliance violation
    Proves detect → reason → act workflow
    
    Returns:
        - Before/after content
        - Success status
        - Timestamp
    """
    try:
        logger.info(f"🔧 Executing remediation for {request.violation_id}")
        
        # Execute remediation
        result = await remediation_engine.remediate(request)
        
        # Log activity
        log_activity(
            action=f"Executed {request.action_type} remediation",
            violation_id=request.violation_id,
            details={
                "action_type": request.action_type,
                "success": result.success
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Remediation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Remediation failed: {str(e)}")


@router.get("/evidence", response_model=List[Evidence])
async def get_all_evidence():
    """
    Get all audit evidence
    
    Returns comprehensive evidence records for compliance audits
    """
    try:
        evidence_list = evidence_generator.get_all_evidence()
        logger.info(f"📋 Retrieved {len(evidence_list)} evidence records")
        return evidence_list
        
    except Exception as e:
        logger.error(f"❌ Evidence retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evidence retrieval failed: {str(e)}")


@router.get("/evidence/{evidence_id}", response_model=Evidence)
async def get_evidence_by_id(evidence_id: str):
    """Get specific evidence record by ID"""
    try:
        evidence = evidence_generator.get_evidence(evidence_id)
        
        if not evidence:
            raise HTTPException(status_code=404, detail=f"Evidence {evidence_id} not found")
        
        return evidence
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Evidence retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evidence retrieval failed: {str(e)}")


@router.get("/evidence/violation/{violation_id}", response_model=List[Evidence])
async def get_evidence_by_violation(violation_id: str):
    """Get all evidence for a specific violation"""
    try:
        evidence_list = evidence_generator.get_evidence_by_violation(violation_id)
        return evidence_list
        
    except Exception as e:
        logger.error(f"❌ Evidence retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evidence retrieval failed: {str(e)}")


@router.get("/agent-activity", response_model=List[AgentActivity])
async def get_agent_activity(limit: int = 50):
    """
    Get agent activity log
    
    Shows what actions the cognitive agent has taken
    """
    try:
        # Return most recent activities
        recent_activities = activity_log[-limit:] if len(activity_log) > limit else activity_log
        recent_activities.reverse()  # Most recent first
        
        logger.info(f"📊 Retrieved {len(recent_activities)} activity records")
        return recent_activities
        
    except Exception as e:
        logger.error(f"❌ Activity retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Activity retrieval failed: {str(e)}")


@router.get("/stats")
async def get_agent_stats():
    """
    Get agent statistics
    
    Returns:
        - Evidence statistics
        - Activity counts
        - Performance metrics
    """
    try:
        evidence_stats = evidence_generator.get_evidence_stats()
        
        return {
            "total_activities": len(activity_log),
            "evidence_statistics": evidence_stats,
            "supported_actions": remediation_engine.get_supported_actions(),
            "agent_status": "operational"
        }
        
    except Exception as e:
        logger.error(f"❌ Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


@router.get("/audit-report")
async def export_audit_report():
    """
    Export comprehensive audit report
    
    Enterprise-grade compliance documentation
    """
    try:
        report = evidence_generator.export_audit_report()
        logger.info(f"📄 Exported audit report: {report['report_id']}")
        return report
        
    except Exception as e:
        logger.error(f"❌ Audit report export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Audit report export failed: {str(e)}")


@router.post("/workflow")
async def complete_workflow(violation: ViolationInput, auto_remediate: bool = True):
    """
    Complete workflow: Reason → Remediate → Evidence
    
    Demonstrates full detect → reason → act → prove cycle
    """
    try:
        logger.info(f"🔄 Starting complete workflow for {violation.violation_id}")
        
        # Step 1: Reason
        reasoning = await reasoner.reason_about_violation(violation)
        
        # Step 2: Remediate (if autonomous and requested)
        remediation_result = None
        if auto_remediate and reasoning.autonomy_level.value == "AUTONOMOUS" and reasoning.is_violation:
            # Determine remediation action based on violation type
            action_type = "mask_pan" if "PAN" in violation.violation_type.value else "redact_pii"
            
            remediation_request = RemediationRequest(
                violation_id=violation.violation_id,
                action_type=action_type,
                content=violation.content
            )
            
            remediation_result = await remediation_engine.remediate(remediation_request)
        
        # Step 3: Generate evidence
        evidence = evidence_generator.generate_evidence(
            violation_id=violation.violation_id,
            reasoning=reasoning,
            remediation=remediation_result
        )
        
        # Log activity
        log_activity(
            action="Completed full workflow (reason → remediate → evidence)",
            violation_id=violation.violation_id,
            details={
                "reasoning": reasoning.risk_severity.value,
                "remediated": remediation_result is not None,
                "evidence_id": evidence.evidence_id
            }
        )
        
        return {
            "reasoning": reasoning,
            "remediation": remediation_result,
            "evidence": evidence,
            "workflow_status": "completed"
        }
        
    except Exception as e:
        logger.error(f"❌ Workflow failed: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")


@router.get("/activity")
async def get_agent_activity():
    """
    Get recent agent activity
    
    Returns activity log from cognitive agent
    """
    try:
        # Return last 50 activities
        recent_activities = activity_log[-50:] if len(activity_log) > 50 else activity_log
        return {
            "count": len(recent_activities),
            "activities": [act.model_dump() for act in reversed(recent_activities)]
        }
    except Exception as e:
        logger.error(f"❌ Activity retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Activity retrieval failed: {str(e)}")
