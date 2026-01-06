"""
Autonomous Compliance AI for Visa
Agentic AI-Enabled Continuous PCI-DSS Compliance Platform

Main FastAPI Application Entry Point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from pathlib import Path

# Import all agent routers
from monitoring_agent.api import router as monitoring_router
from cognitive_agent.api import router as cognitive_router  
from evidence_layer.api import router as evidence_router
from audit_layer.api import router as audit_router

# Import RAG models and services
from app.models.schemas import (
    QueryRequest,
    QueryResponse,
    IngestRequest,
    IngestResponse,
    Obligation,
    ObligationsResponse
)
from app.services.rag_service import RAGService
from app.services.ingestion_service import IngestionService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instances
rag_service: RAGService = None
ingestion_service: IngestionService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for FastAPI application"""
    global rag_service, ingestion_service
    
    logger.info("🚀 Initializing Autonomous Compliance AI for Visa...")
    logger.info("📦 Tenant: VISA | Regulation: PCI-DSS")
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    (data_dir / "violations.json").touch(exist_ok=True)
    (data_dir / "evidence.json").touch(exist_ok=True)
    
    # Initialize RAG services
    logger.info("📚 Initializing RAG service...")
    rag_service = RAGService()
    ingestion_service = IngestionService(rag_service)
    
    # Load mock regulatory data
    logger.info("📚 Loading regulatory knowledge base...")
    await ingestion_service.ingest_mock_regulations()
    
    logger.info("✅ System ready!")
    
    yield
    
    logger.info("🔴 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Autonomous Compliance AI for Visa",
    description="Agentic AI-powered continuous compliance monitoring with real-time PCI-DSS violation detection, LLM-driven reasoning, and tamper-evident audit trails",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all agent routers
app.include_router(monitoring_router)
app.include_router(cognitive_router)
app.include_router(evidence_router)
app.include_router(audit_router)


@app.get("/")
async def root():
    """Root health check endpoint"""
    return {
        "status": "operational",
        "service": "Autonomous Compliance AI for Visa",
        "version": "1.0.0",
        "tenant": "VISA",
        "regulation_scope": "PCI-DSS",
        "capabilities": [
            "Real-time PAN detection",
            "LLM-driven reasoning (OpenRouter)",
            "Autonomous remediation",
            "Tamper-evident audit trails",
            "Evidence generation",
            "Regulatory knowledge base (RAG)"
        ],
        "endpoints": {
            "monitoring": "/monitor/*",
            "cognitive": "/agent/*",
            "evidence": "/evidence/*",
            "audit": "/audit/*",
            "regulations": "/regulations/*"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Autonomous Compliance AI",
        "modules": {
            "monitoring_agent": "operational",
            "cognitive_agent": "operational",
            "evidence_layer": "operational",
            "audit_layer": "operational",
            "rag_service": "operational" if rag_service else "not_initialized"
        }
    }


# ============= RAG / Regulations Endpoints =============

@app.post("/regulations/query", response_model=QueryResponse)
async def query_regulations(request: QueryRequest):
    """
    Query the regulatory knowledge base using RAG
    
    Example:
        POST /regulations/query
        {
            "question": "Is PAN allowed in application logs?"
        }
    
    Returns:
        {
            "answer": "No. PCI-DSS 3.2.1 prohibits storage of PAN in logs.",
            "obligations": ["PCI_3_2_1_MASK_PAN"],
            "confidence": 0.94
        }
    """
    try:
        logger.info(f"📊 RAG Query: {request.question}")
        
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not initialized")
        
        response = await rag_service.query(request.question, top_k=request.top_k or 5)
        
        logger.info(f"✅ Query completed. Confidence: {response['confidence']:.2f}")
        
        return QueryResponse(**response)
        
    except Exception as e:
        logger.error(f"❌ Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/regulations/obligations", response_model=ObligationsResponse)
async def list_obligations(
    regulation: str = None,
    severity: str = None,
    data_type: str = None
):
    """
    List all regulatory obligations
    
    Query parameters:
        regulation: Filter by regulation (e.g., "PCI-DSS")
        severity: Filter by severity (e.g., "CRITICAL")
        data_type: Filter by data type (e.g., "PAN")
    """
    try:
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not initialized")
        
        obligations = rag_service.get_all_obligations()
        
        # Apply filters
        if regulation:
            obligations = [o for o in obligations if regulation.upper() in o.regulation.upper()]
        
        if severity:
            obligations = [o for o in obligations if severity.upper() == o.severity.upper()]
        
        if data_type:
            obligations = [o for o in obligations if data_type.upper() in o.data_types]
        
        return ObligationsResponse(
            count=len(obligations),
            obligations=obligations
        )
        
    except Exception as e:
        logger.error(f"❌ Error listing obligations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/regulations/stats")
async def get_rag_stats():
    """Get RAG service statistics"""
    try:
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not initialized")
        
        return rag_service.get_statistics()
        
    except Exception as e:
        logger.error(f"❌ Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
