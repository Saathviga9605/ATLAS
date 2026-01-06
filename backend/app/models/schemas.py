"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Obligation(BaseModel):
    """Structured compliance obligation"""
    obligation_id: str = Field(..., description="Unique identifier")
    regulation: str = Field(..., description="Source regulation (PCI-DSS, GDPR, etc.)")
    section: str = Field(..., description="Specific section or article")
    description: str = Field(..., description="Human-readable obligation description")
    data_types: List[str] = Field(default_factory=list, description="Data types affected (PAN, PII, etc.)")
    applies_to: List[str] = Field(default_factory=list, description="Contexts (logs, chats, transactions)")
    severity: str = Field(..., description="CRITICAL, HIGH, MEDIUM, LOW")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    jurisdiction: str = Field(default="Global", description="Regulatory jurisdiction")
    effective_date: Optional[str] = Field(None, description="When regulation became effective")
    
    class Config:
        json_schema_extra = {
            "example": {
                "obligation_id": "PCI_3_2_1_MASK_PAN",
                "regulation": "PCI-DSS",
                "section": "3.2.1",
                "description": "Mask PAN in logs and customer communications",
                "data_types": ["PAN"],
                "applies_to": ["logs", "chats", "transactions"],
                "severity": "CRITICAL",
                "confidence": 0.92,
                "jurisdiction": "Global",
                "effective_date": "2024-01-01"
            }
        }


class RegulationChunk(BaseModel):
    """Chunked regulation text with metadata"""
    chunk_id: str
    regulation: str
    section: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None


class QueryRequest(BaseModel):
    """RAG query request"""
    question: str = Field(..., description="Natural language compliance question")
    top_k: Optional[int] = Field(5, description="Number of relevant results to retrieve")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Is PAN allowed in application logs?",
                "top_k": 5
            }
        }


class QueryResponse(BaseModel):
    """RAG query response"""
    answer: str = Field(..., description="Natural language answer")
    obligations: List[str] = Field(..., description="Relevant obligation IDs")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Answer confidence")
    sources: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Source chunks")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "No. PCI-DSS 3.2.1 prohibits storage of PAN in logs.",
                "obligations": ["PCI_3_2_1_MASK_PAN"],
                "confidence": 0.94,
                "sources": []
            }
        }


class IngestRequest(BaseModel):
    """Document ingestion request"""
    source: str = Field(..., description="Document source identifier")
    content: str = Field(..., description="Full document content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source": "PCI-DSS-4.0",
                "content": "Requirement 3: Protect stored cardholder data...",
                "metadata": {
                    "regulation": "PCI-DSS",
                    "version": "4.0"
                }
            }
        }


class IngestResponse(BaseModel):
    """Document ingestion response"""
    source: str
    chunks_created: int
    obligations_extracted: int
    status: str
    message: str


class ObligationsResponse(BaseModel):
    """Response for obligations list endpoint"""
    total: int
    obligations: List[Obligation]
