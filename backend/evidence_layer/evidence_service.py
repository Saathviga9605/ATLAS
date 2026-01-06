import hashlib
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from models.evidence import EvidenceRecord, EventType
from audit_layer.audit_chain_service import AuditChainService
import logging

logger = logging.getLogger(__name__)


class EvidenceService:
    """Service for capturing and managing evidence records"""
    
    def __init__(self, audit_chain_service: AuditChainService):
        self.audit_chain_service = audit_chain_service
        self.evidence_store: Dict[str, EvidenceRecord] = {}  # In-memory store
        
        # File-based persistence
        project_root = Path(__file__).parent.parent
        self.storage_path = project_root / "data" / "evidence.json"
        logger.info(f"Evidence storage initialized at: {self.storage_path.absolute()}")
        self._ensure_storage_exists()
        self._load_from_file()
    
    def _ensure_storage_exists(self):
        """Create storage file if it doesn't exist"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            initial_data = {
                "tenant_id": "visa",
                "evidence": []
            }
            with open(self.storage_path, 'w') as f:
                json.dump(initial_data, f, indent=2)
            logger.info(f"Created new evidence storage at: {self.storage_path.absolute()}")
    
    def _load_from_file(self):
        """Load existing evidence from file"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                for evidence_dict in data.get("evidence", []):
                    evidence = EvidenceRecord(**evidence_dict)
                    self.evidence_store[evidence.evidence_id] = evidence
            logger.info(f"Loaded {len(self.evidence_store)} evidence records from file")
        except Exception as e:
            logger.error(f"Error loading evidence from file: {e}")
    
    def _save_to_file(self):
        """Save all evidence to file"""
        try:
            data = {
                "tenant_id": "visa",
                "evidence": [e.model_dump(mode='json') for e in self.evidence_store.values()]
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Saved {len(self.evidence_store)} evidence records to {self.storage_path.absolute()}")
            return True
        except Exception as e:
            logger.error(f"Error saving evidence to file: {e}")
            return False
    
    def generate_evidence_id(self) -> str:
        """Generate unique evidence ID"""
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:6].upper()
        return f"EVID-{timestamp}-{unique_id}"
    
    def capture_evidence(
        self,
        event_type: EventType,
        regulation: Dict[str, Any],
        detection: Dict[str, Any],
        violation_state: Optional[Dict[str, Any]] = None,
        remediation: Optional[Dict[str, Any]] = None,
        reasoning_chain: Optional[Dict[str, Any]] = None,
        linkages: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EvidenceRecord:
        """Capture a new evidence record"""
        evidence_id = self.generate_evidence_id()
        
        evidence = EvidenceRecord(
            evidence_id=evidence_id,
            event_type=event_type,
            regulation=regulation,
            detection=detection,
            violation_state=violation_state,
            remediation=remediation,
            reasoning_chain=reasoning_chain,
            linkages=linkages,
            metadata=metadata,
            timestamp=datetime.utcnow()
        )
        
        # Store evidence in memory
        self.evidence_store[evidence_id] = evidence
        
        # Persist to file
        self._save_to_file()
        
        # Append to audit chain
        self.audit_chain_service.append(evidence)
        
        logger.info(f"Evidence captured: {evidence_id}")
        return evidence
    
    def get_evidence(self, evidence_id: str) -> Optional[EvidenceRecord]:
        """Retrieve evidence by ID"""
        return self.evidence_store.get(evidence_id)
    
    def update_evidence(self, evidence_id: str, updates: Dict[str, Any]) -> Optional[EvidenceRecord]:
        """Update evidence record (e.g., add after_state after remediation)"""
        evidence = self.evidence_store.get(evidence_id)
        if not evidence:
            return None
        
        # Update fields
        evidence_dict = evidence.model_dump()
        evidence_dict.update(updates)
        
        # Create new record with updates
        updated_evidence = EvidenceRecord(**evidence_dict)
        self.evidence_store[evidence_id] = updated_evidence
        
        # Persist to file
        self._save_to_file()
        
        return updated_evidence
    
    def get_evidence_in_range(
        self,
        start_date: datetime,
        end_date: datetime,
        tenant_id: Optional[str] = None
    ) -> List[EvidenceRecord]:
        """Get all evidence records in date range"""
        results = []
        for evidence in self.evidence_store.values():
            if start_date <= evidence.timestamp <= end_date:
                if tenant_id is None or (evidence.metadata and evidence.metadata.get("tenant_id") == tenant_id):
                    results.append(evidence)
        
        return sorted(results, key=lambda e: e.timestamp)
    
    def list_all_evidence(self) -> List[EvidenceRecord]:
        """List all evidence records"""
        return list(self.evidence_store.values())

