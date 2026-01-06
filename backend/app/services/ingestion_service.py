"""
Regulatory Document Ingestion Service
Handles parsing, chunking, and obligation extraction
"""

import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

from app.models.schemas import Obligation, RegulationChunk
from app.services.rag_service import RAGService
from app.services.obligation_extractor import ObligationExtractor

logger = logging.getLogger(__name__)


class IngestionService:
    """
    Ingests regulatory documents, chunks them, and extracts obligations
    """
    
    def __init__(self, rag_service: RAGService):
        """Initialize ingestion service"""
        self.rag_service = rag_service
        self.extractor = ObligationExtractor()
        logger.info("🔧 Ingestion service initialized")
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Full text to chunk
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks
        
        Returns:
            List of text chunks
        """
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If paragraph fits in current chunk
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Start new chunk
                if len(para) > chunk_size:
                    # Split large paragraph
                    words = para.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) < chunk_size:
                            temp_chunk += word + " "
                        else:
                            chunks.append(temp_chunk.strip())
                            temp_chunk = word + " "
                    current_chunk = temp_chunk
                else:
                    current_chunk = para + "\n\n"
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def extract_section_from_content(self, content: str, regulation: str) -> str:
        """Extract section/article number from content"""
        
        # Patterns for different regulations
        patterns = {
            'PCI-DSS': r'Requirement (\d+\.?\d*\.?\d*)',
            'GDPR': r'Article (\d+)',
            'CCPA': r'§\s*(\d+\.\d+)',
        }
        
        pattern = patterns.get(regulation, r'Section (\d+\.?\d*)')
        match = re.search(pattern, content)
        
        if match:
            return match.group(1)
        
        return "General"
    
    def generate_chunk_id(self, regulation: str, section: str, index: int) -> str:
        """Generate unique chunk ID"""
        base = f"{regulation}_{section}_{index}"
        return hashlib.md5(base.encode()).hexdigest()[:16]
    
    async def ingest_document(
        self,
        source: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ingest a regulatory document
        
        Args:
            source: Document identifier
            content: Full document text
            metadata: Additional metadata
        
        Returns:
            Ingestion statistics
        """
        logger.info(f"📥 Ingesting document: {source}")
        
        regulation = metadata.get('regulation', source)
        version = metadata.get('version', '1.0')
        
        # Chunk the document
        chunks = self.chunk_text(content)
        logger.info(f"📄 Created {len(chunks)} chunks")
        
        # Process each chunk
        obligations_created = 0
        
        for idx, chunk_text in enumerate(chunks):
            try:
                # Extract section number
                section = self.extract_section_from_content(chunk_text, regulation)
                
                # Generate chunk ID
                chunk_id = self.generate_chunk_id(regulation, section, idx)
                
                # Prepare chunk metadata
                chunk_metadata = {
                    "regulation": regulation,
                    "section": section,
                    "chunk_index": idx,
                    "source": source,
                    "version": version,
                    "ingested_at": datetime.now().isoformat(),
                    **metadata
                }
                
                # Add chunk to vector store
                self.rag_service.add_chunk(chunk_id, chunk_text, chunk_metadata)
                
                # Extract obligations from chunk
                obligations = await self.extractor.extract_obligations(
                    text=chunk_text,
                    regulation=regulation,
                    section=section,
                    metadata=chunk_metadata
                )
                
                # Store obligations
                for obligation in obligations:
                    # Add obligation_id to chunk metadata
                    chunk_metadata['obligation_id'] = obligation.obligation_id
                    
                    # Store obligation
                    self.rag_service.add_obligation(obligation)
                    obligations_created += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to process chunk {idx}: {e}")
                continue
        
        logger.info(f"✅ Ingestion complete: {len(chunks)} chunks, {obligations_created} obligations")
        
        return {
            "source": source,
            "chunks_created": len(chunks),
            "obligations_extracted": obligations_created,
            "status": "success",
            "message": f"Ingested {len(chunks)} chunks with {obligations_created} obligations"
        }
    
    async def ingest_mock_regulations(self):
        """Ingest mock regulatory data for demo"""
        logger.info("📚 Loading mock regulations...")
        
        # Import mock data
        from app.data.mock_regulations import (
            PCI_DSS_MOCK,
            GDPR_MOCK,
            CCPA_MOCK,
            INTERNAL_POLICY_MOCK
        )
        
        # Ingest each regulation
        mock_docs = [
            ("PCI-DSS-4.0", PCI_DSS_MOCK, {"regulation": "PCI-DSS", "version": "4.0", "jurisdiction": "Global"}),
            ("GDPR", GDPR_MOCK, {"regulation": "GDPR", "version": "2016/679", "jurisdiction": "EU"}),
            ("CCPA", CCPA_MOCK, {"regulation": "CCPA", "version": "2018", "jurisdiction": "California"}),
            ("INTERNAL", INTERNAL_POLICY_MOCK, {"regulation": "INTERNAL", "version": "2024", "jurisdiction": "Company-wide"})
        ]
        
        for source, content, metadata in mock_docs:
            try:
                await self.ingest_document(source, content, metadata)
            except Exception as e:
                logger.error(f"❌ Failed to ingest {source}: {e}")
        
        logger.info("✅ Mock regulations loaded")
