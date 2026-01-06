"""
RAG (Retrieval Augmented Generation) Service
Handles vector store operations and compliance question answering
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

from app.models.schemas import Obligation

logger = logging.getLogger(__name__)


class RAGService:
    """
    Vector-based retrieval augmented generation for regulatory compliance
    """
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize RAG service with vector store and embedding model"""
        logger.info(f"🔧 Initializing RAG service with {embedding_model}")
        
        # Initialize embedding model
        self.embedder = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedder.get_sentence_embedding_dimension()
        
        # Initialize ChromaDB (in-memory for demo)
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        # Create collections
        try:
            self.chroma_client.delete_collection("regulations")
        except:
            pass
        
        self.collection = self.chroma_client.create_collection(
            name="regulations",
            metadata={"hnsw:space": "cosine"}
        )
        
        # In-memory obligation store
        self.obligations: Dict[str, Obligation] = {}
        
        logger.info(f"✅ RAG service initialized (embedding_dim={self.embedding_dim})")
    
    def add_chunk(self, chunk_id: str, content: str, metadata: Dict[str, Any]):
        """Add a regulation chunk to the vector store"""
        try:
            # Generate embedding
            embedding = self.embedder.encode(content, convert_to_tensor=False)
            
            # Add to ChromaDB
            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding.tolist()],
                documents=[content],
                metadatas=[metadata]
            )
            
            logger.debug(f"✅ Added chunk: {chunk_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to add chunk {chunk_id}: {e}")
            raise
    
    def add_obligation(self, obligation: Obligation):
        """Store a structured obligation"""
        self.obligations[obligation.obligation_id] = obligation
        logger.debug(f"✅ Added obligation: {obligation.obligation_id}")
    
    def get_all_obligations(self) -> List[Obligation]:
        """Get all stored obligations"""
        return list(self.obligations.values())
    
    def similarity_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search
        
        Returns:
            List of {id, content, metadata, distance} dicts
        """
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode(query, convert_to_tensor=False)
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i, chunk_id in enumerate(results['ids'][0]):
                    formatted_results.append({
                        'id': chunk_id,
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else 0.0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Similarity search failed: {e}")
            return []
    
    async def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Answer a compliance question using RAG
        
        Args:
            question: Natural language question
            top_k: Number of relevant chunks to retrieve
        
        Returns:
            {
                "answer": str,
                "obligations": List[str],
                "confidence": float,
                "sources": List[Dict]
            }
        """
        try:
            # Retrieve relevant chunks
            results = self.similarity_search(question, top_k=top_k)
            
            if not results:
                return {
                    "answer": "No relevant regulatory information found.",
                    "obligations": [],
                    "confidence": 0.0,
                    "sources": []
                }
            
            # Extract relevant obligations
            obligation_ids = set()
            for result in results:
                metadata = result.get('metadata', {})
                if 'obligation_id' in metadata:
                    obligation_ids.add(metadata['obligation_id'])
            
            # Generate answer using retrieved context
            answer, confidence = self._generate_answer(question, results)
            
            return {
                "answer": answer,
                "obligations": list(obligation_ids),
                "confidence": confidence,
                "sources": [
                    {
                        "regulation": r['metadata'].get('regulation', 'Unknown'),
                        "section": r['metadata'].get('section', 'N/A'),
                        "content": r['content'][:200] + "..." if len(r['content']) > 200 else r['content'],
                        "relevance": 1.0 - r.get('distance', 0.5)
                    }
                    for r in results[:3]  # Top 3 sources
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            raise
    
    def _generate_answer(self, question: str, context_chunks: List[Dict[str, Any]]) -> tuple[str, float]:
        """
        Generate answer from retrieved context
        Uses rule-based approach for demo (can be replaced with LLM)
        """
        if not context_chunks:
            return "No relevant information found.", 0.0
        
        # Get the most relevant chunk
        top_chunk = context_chunks[0]
        content = top_chunk['content']
        metadata = top_chunk['metadata']
        distance = top_chunk.get('distance', 0.5)
        
        # Calculate confidence (inverse of distance)
        confidence = max(0.0, min(1.0, 1.0 - distance))
        
        # Rule-based answer generation based on question patterns
        question_lower = question.lower()
        
        # Check for prohibition questions
        if any(word in question_lower for word in ['allowed', 'can', 'permitted', 'okay', 'ok to']):
            if any(word in content.lower() for word in ['must not', 'prohibited', 'cannot', 'shall not', 'do not']):
                answer = f"No. {metadata.get('regulation', 'Regulation')} {metadata.get('section', '')} prohibits this. {content[:150]}..."
            else:
                answer = f"Based on {metadata.get('regulation', 'regulations')}, this requires specific controls. {content[:150]}..."
        
        # Check for requirement questions
        elif any(word in question_lower for word in ['what', 'which', 'how', 'requirement']):
            answer = f"{metadata.get('regulation', 'Regulation')} {metadata.get('section', '')} requires: {content[:200]}..."
        
        # Default answer
        else:
            answer = f"According to {metadata.get('regulation', 'regulatory guidance')}: {content[:200]}..."
        
        return answer, confidence
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            count = self.collection.count()
            
            # Calculate obligation statistics
            obligation_counts = {}
            severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
            
            for obligation in self.obligations.values():
                reg = obligation.regulation
                obligation_counts[reg] = obligation_counts.get(reg, 0) + 1
                severity_counts[obligation.severity] = severity_counts.get(obligation.severity, 0) + 1
            
            return {
                "total_chunks": count,
                "total_obligations": len(self.obligations),
                "obligations_by_regulation": obligation_counts,
                "obligations_by_severity": severity_counts,
                "embedding_dimension": self.embedding_dim,
                "vector_store": "ChromaDB"
            }
        except Exception as e:
            logger.error(f"❌ Failed to get statistics: {e}")
            return {}
