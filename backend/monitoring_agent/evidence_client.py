"""
Evidence capture client
Communicates with /evidence/capture API
"""
import httpx
from typing import Dict, Any
from .models import ViolationObject


class EvidenceClient:
    """HTTP client for evidence capture API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.evidence_endpoint = f"{base_url}/evidence/capture"
    
    async def capture_evidence(self, violation: ViolationObject) -> Dict[str, Any]:
        """
        Call POST /evidence/capture with violation data
        
        Args:
            violation: ViolationObject to send
            
        Returns:
            Response dict with evidence_id and message
            
        Raises:
            httpx.HTTPError: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.evidence_endpoint,
                json=violation.model_dump(),
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
