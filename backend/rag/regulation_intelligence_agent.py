"""
Regulation Intelligence Agent - RAG + Obligation Mining System
Complete implementation - LangChain 1.x compatible
"""

import os
import json
from typing import List, Dict, Optional
from pathlib import Path
import requests

# -------------------- LangChain imports (v1.x) --------------------
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.runnables import RunnablePassthrough

# -------------------- Other --------------------
from pydantic import BaseModel, Field


# ==================== CONFIGURATION ====================

class Config:
    """Central configuration"""
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-key-here")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # Use a model that works with your credits
    # Options: "google/gemini-flash-1.5", "meta-llama/llama-3.1-8b-instruct"
    LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/llama-3.1-8b-instruct")
    
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Token limits (important for cost control)
    MAX_TOKENS = 2000  # Reduced from default
    
    PERSIST_DIR_REGULATORY = "./chroma_db_regulatory"
    PERSIST_DIR_POLICY = "./chroma_db_policy"
    DATA_DIR = "./regulatory_data"


# ==================== DATA MODELS ====================

class ComplianceGoal(BaseModel):
    """Structured compliance goal extracted from regulations"""
    goal_id: str
    parent_goal_id: Optional[str] = None
    regulation: str
    section: str
    original_text: str
    goal_description: str
    verb: str
    subject: str
    object: str
    risk_level: str
    applicable_entities: List[str] = []


# ==================== REGULATORY SOURCES ====================

REGULATORY_SOURCES = {
    # =========================
    # VISA – CORE OPERATING RULES
    # =========================
    "VISA_CORE_RULES": {
        "name": "Visa Core Rules and Visa Product and Service Rules (18 October 2025 V1.1)",
        "url": "https://usa.visa.com/content/dam/VCOM/download/about-visa/visa-rules-public.pdf",
        "local_path": "visa_core_rules_oct2025.pdf"
    },
    "INTERLINK_RULES": {
        "name": "Interlink Core Rules and Interlink Product and Service Rules (18 October 2025)",
        "url": "https://usa.visa.com/content/dam/VCOM/regional/na/us/support-legal/documents/interlink-operating-regulations.pdf",
        "local_path": "interlink_rules_oct2025.pdf"
    },
    # =========================
    # GLOBAL / PAYMENT SECURITY – PCI DSS
    # =========================
    "PCI_DSS": {
        "name": "PCI DSS v4.0.1 (Latest Version as of 2026)",
        "url": "https://listings.pcisecuritystandards.org/documents/PCI_DSS_v4-0_1.pdf",
        "local_path": "pci_dss_v4_0_1.pdf"
    },
    # =========================
    # VISA – ADDITIONAL COMPLIANCE GUIDES
    # =========================
    "VISA_MERCHANT_DATA_STANDARDS": {
        "name": "Visa Merchant Data Standards Manual (October 2025)",
        "url": "https://usa.visa.com/content/dam/VCOM/download/merchants/visa-merchant-data-standards-manual.pdf",
        "local_path": "visa_merchant_data_standards.pdf"
    },
    "VISA_GLOBAL_ACQUIRER_RISK_STANDARDS": {
        "name": "Visa Global Acquirer Risk Standards (October 2024)",
        "url": "https://usa.visa.com/dam/VCOM/download/merchants/visa-global-acquirer-risk-standards.pdf",
        "local_path": "visa_global_acquirer_risk_standards.pdf"
    },
    # =========================
    # EUROPE – DATA PRIVACY
    # =========================
    "GDPR": {
        "name": "GDPR Regulation (EU) 2016/679 - Full Text",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32016R0679",
        "local_path": "gdpr_eu_2016_679.pdf"
    },
    # =========================
    # INDIA – DATA PRIVACY
    # =========================
    "INDIA_DPDP_ACT": {
        "name": "Digital Personal Data Protection Act 2023 (India)",
        "url": "https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf",
        "local_path": "india_dpdp_act_2023.pdf"
    },
    # =========================
    # INDIA – RBI
    # =========================
    "RBI_MASTER_DIRECTIONS": {
        "name": "RBI Master Directions and Circulars",
        "url": "https://www.rbi.org.in/commonman/english/scripts/MasterCircular.aspx",
        "local_path": "rbi_master_directions.html"
    },
    "RBI_HANDBOOK": {
        "name": "RBI Handbook of Regulations",
        "url": "https://banklaw.in/manage/images/services/1556052828RBI-HandbookofRegulationsataglance-27.2.2025-3-76.pdf",
        "local_path": "rbi_handbook_regulations.pdf"
    },
    # =========================
    # INDIA – SEBI
    # =========================
    "SEBI_REGULATIONS": {
        "name": "SEBI Regulations (Official Listing)",
        "url": "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&smid=0&ssid=3",
        "local_path": "sebi_regulations.html"
    },
    "SEBI_CIRCULARS": {
        "name": "SEBI Circulars and Notifications",
        "url": "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&smid=0&ssid=7",
        "local_path": "sebi_circulars.html"
    },
    # =========================
    # UK – FCA
    # =========================
    "FCA_HANDBOOK": {
        "name": "UK FCA Handbook (Online Rulebook)",
        "url": "https://www.handbook.fca.org.uk/",
        "local_path": "fca_handbook.html"
    },
    "FCA_ARCHIVE_PDF": {
        "name": "FCA Handbook Archived PDF",
        "url": "https://www.fca.org.uk/publication/archive/fsa-handbook-online.pdf",
        "local_path": "fca_handbook_archive.pdf"
    },
    # =========================
    # USA – SEC
    # =========================
    "SEC_RULES": {
        "name": "US SEC Rules and Regulations",
        "url": "https://www.sec.gov/about/divisions-offices/division-corporation-finance/rules-regulations-schedules",
        "local_path": "sec_rules.html"
    },
    "US_CFR_TITLE_17": {
        "name": "Code of Federal Regulations - Title 17 (Securities)",
        "url": "https://www.govinfo.gov/content/pkg/CFR-2021-title17-vol2/pdf/CFR-2021-title17-vol2.pdf",
        "local_path": "us_cfr_title_17.pdf"
    }
}


# ==================== MOCK DATA ====================

MOCK_COMPANY_POLICIES = {
    "data_retention": """
# Data Retention Policy
2.1 Sensitive Authentication Data (SAD) must be deleted immediately after authorization.
2.2 Primary Account Numbers (PAN) shall be stored only when business necessity is documented.
2.3 Cardholder data retention period: Maximum 18 months unless required by law.
2.4 All stored PAN must be encrypted using AES-256 or equivalent.
    """,
    
    "access_control": """
# Access Control Policy
2.1 Multi-factor authentication (MFA) must be enabled for all administrative access.
2.2 Password complexity: Minimum 12 characters, alphanumeric with special characters.
2.3 Password rotation: Every 90 days for privileged accounts.
3.1 Access shall be granted based on job function and least privilege principle.
    """,
    
    "incident_response": """
# Incident Response Policy
3.1 Critical incidents must be escalated to CISO within 1 hour of detection.
3.2 Forensic preservation shall begin immediately upon incident confirmation.
3.3 Affected parties must be notified within 72 hours for GDPR breaches.
3.4 Payment card brands must be notified of compromises within 24 hours.
    """
}


# ==================== EMBEDDINGS ====================

class HuggingFaceLocalEmbeddings(Embeddings):
    """Local HuggingFace embeddings - free and fast"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        print(f"✓ Loaded embedding model: {model_name}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode([text], show_progress_bar=False)
        return embedding[0].tolist()


# ==================== DOCUMENT PROCESSING ====================

class DocumentProcessor:
    """Handles document processing"""
    
    def __init__(self):
        self.data_dir = Path(Config.DATA_DIR)
        self.data_dir.mkdir(exist_ok=True)
    
    def download_pdf(self, url: str, filename: str) -> Optional[str]:
        """Download PDF from URL"""
        filepath = self.data_dir / filename
        
        if filepath.exists():
            print(f"✓ {filename} already exists")
            return str(filepath)
        
        print(f"Downloading {filename}...")
        try:
            response = requests.get(url, timeout=60, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Downloaded {filename}")
            return str(filepath)
        except Exception as e:
            print(f"✗ Failed to download {filename}: {e}")
            return None
    
    def load_pdf(self, filepath: str) -> List[Document]:
        """Load and parse PDF"""
        try:
            loader = PyPDFLoader(filepath)
            documents = loader.load()
            print(f"✓ Loaded {len(documents)} pages from {Path(filepath).name}")
            return documents
        except Exception as e:
            print(f"✗ Failed to load {filepath}: {e}")
            return []
    
    def create_mock_policies(self) -> List[Document]:
        """Create mock policy documents"""
        docs = []
        for name, content in MOCK_COMPANY_POLICIES.items():
            docs.append(Document(
                page_content=content,
                metadata={"source": f"policy_{name}", "type": "company_policy"}
            ))
        return docs
    
    def create_mock_regulatory(self) -> List[Document]:
        """Create mock regulatory document"""
        content = """
PCI-DSS v4.0 - Requirement 3: Protect Stored Cardholder Data

3.1 Processes and mechanisms for protecting stored account data are defined and understood.
3.2 Storage of sensitive authentication data (SAD) after authorization is prohibited.
- Full track data from the magnetic stripe must not be retained.
- Card verification code must not be retained after authorization.
- PIN and PIN block must never be stored.

3.3 Sensitive authentication data is not stored after authorization.
3.4 Access to displays of full PAN and ability to copy cardholder data are restricted.
3.5 Primary account number (PAN) is secured wherever it is stored.
- If PAN is stored, it must be rendered unreadable using strong cryptography.
- Encryption keys must be as strong as the data-encryption key.

3.6 Cryptographic keys used to protect stored account data are protected.
- Access to cleartext cryptographic keys must be restricted to the fewest custodians.
- Cryptographic keys must be stored in the fewest possible locations.

Visa Core Rules - Data Security Requirements

Rule 5.3.1: Merchants must not store sensitive authentication data after authorization.
Rule 5.3.2: All cardholder data must be protected in accordance with PCI DSS requirements.
Rule 5.3.3: Merchants must implement multi-layered security controls to protect cardholder data.
Rule 5.4.1: Account data compromise investigations must be completed within 10 business days.
Rule 5.4.2: Compromised accounts must be reported to Visa within 3 business days of discovery.
        """
        return [Document(
            page_content=content,
            metadata={"source": "PCI-DSS v4.0 + Visa Rules", "section": "Requirement 3"}
        )]


# ==================== KB BUILDER ====================

class KnowledgeBaseBuilder:
    """Builds and manages vector stores"""
    
    def __init__(self):
        self.embeddings = HuggingFaceLocalEmbeddings(Config.EMBEDDING_MODEL)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " "]
        )
    
    def build_kb(self, documents: List[Document], persist_dir: str, name: str) -> Chroma:
        """Build knowledge base"""
        print(f"\n=== Building {name} Knowledge Base ===")
        chunks = self.splitter.split_documents(documents)
        print(f"✓ Created {len(chunks)} chunks")
        
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=persist_dir,
            collection_name=name
        )
        
        print(f"✓ KB created with {vectorstore._collection.count()} vectors")
        return vectorstore
    
    def load_existing_kb(self, persist_dir: str) -> Chroma:
        """Load existing knowledge base"""
        if not Path(persist_dir).exists():
            raise ValueError(f"KB not found at {persist_dir}")
        
        return Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings
        )


# ==================== EXTRACTION PROMPT ====================

EXTRACTION_PROMPT = """You are an expert RegTech analyst extracting compliance obligations.

Analyze the regulatory text and extract compliance goals as JSON.

## RULES:
1. Look for: must, shall, should, may, must not, shall not
2. Assess risk: High (sensitive data/security), Medium (process), Low (documentation)
3. Generate goal_id: {{REGULATION}}-{{SECTION}}-{{NUMBER}}

## INPUT:
Regulation: {regulation}
Section: {section}

TEXT:
{text}

## OUTPUT (JSON only):
[
  {{
    "goal_id": "PCI-3.2-01",
    "parent_goal_id": null,
    "regulation": "PCI-DSS v4.0",
    "section": "Requirement 3.2",
    "original_text": "exact quote",
    "goal_description": "clear description",
    "verb": "must not",
    "subject": "Organization",
    "object": "store data",
    "risk_level": "High",
    "applicable_entities": ["Merchants", "Processors"]
  }}
]

Return ONLY valid JSON array. If no obligations, return [].
"""


# ==================== RAG ENGINE ====================

class ComplianceRAGEngine:
    """RAG query engine"""
    
    def __init__(self, regulatory_kb: Chroma, policy_kb: Chroma):
        self.regulatory_kb = regulatory_kb
        self.policy_kb = policy_kb
        
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            temperature=0.3,
            openai_api_key=Config.OPENROUTER_API_KEY,
            openai_api_base=Config.OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "https://github.com/hackathon",
                "X-Title": "Regulation Intelligence Agent",
            }
        )

        self.prompt = PromptTemplate.from_template(
            """You are a compliance expert. Use the context to answer.
If not in context, say so.

Context:
{context}

Question:
{question}

Answer:"""
        )

        self.regulatory_chain = self._build_chain(regulatory_kb, k=5)
        self.policy_chain = self._build_chain(policy_kb, k=3)

    def _format_docs(self, docs: List[Document]) -> str:
        return "\n\n".join(d.page_content for d in docs)

    def _build_chain(self, kb: Chroma, k: int):
        retriever = kb.as_retriever(search_kwargs={"k": k})
        return (
            {
                "context": retriever | self._format_docs,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
        )

    def query_regulations(self, question: str) -> str:
        response = self.regulatory_chain.invoke(question)
        return response.content

    def query_policies(self, question: str) -> str:
        response = self.policy_chain.invoke(question)
        return response.content
    
    def retrieve_chunks(self, query: str, kb_type: str = "regulatory", k: int = 5) -> List[Document]:
        kb = self.regulatory_kb if kb_type == "regulatory" else self.policy_kb
        return kb.similarity_search(query, k=k)


# ==================== OBLIGATION EXTRACTOR ====================

class ObligationExtractor:
    """Extracts structured compliance goals"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            temperature=0,
            max_tokens=Config.MAX_TOKENS,  # Add token limit
            openai_api_key=Config.OPENROUTER_API_KEY,
            openai_api_base=Config.OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "https://github.com/hackathon",
                "X-Title": "Regulation Intelligence Agent",
            }
        )
        
        self.prompt = PromptTemplate(
            template=EXTRACTION_PROMPT,
            input_variables=["regulation", "section", "text"]
        )
    
    def extract_from_text(self, text: str, regulation: str, section: str = "Unknown") -> List[ComplianceGoal]:
        """Extract goals from text"""
        try:
            prompt_text = self.prompt.format(
                regulation=regulation,
                section=section,
                text=text
            )
            
            response = self.llm.invoke(prompt_text)
            response_text = response.content.strip()
            
            # Clean markdown if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])
                if response_text.startswith("json"):
                    response_text = response_text[4:].strip()
            
            goals_data = json.loads(response_text)
            goals = [ComplianceGoal(**goal) for goal in goals_data]
            
            return goals
            
        except json.JSONDecodeError as e:
            print(f"✗ JSON error: {e}")
            print(f"Response: {response_text[:200]}...")
            return []
        except Exception as e:
            print(f"✗ Extraction error: {e}")
            return []
    
    def extract_from_documents(self, documents: List[Document], regulation: str) -> List[ComplianceGoal]:
        """Extract from multiple documents"""
        all_goals = []
        
        for i, doc in enumerate(documents):
            print(f"Processing chunk {i+1}/{len(documents)}...")
            section = doc.metadata.get("section", f"Chunk {i+1}")
            goals = self.extract_from_text(doc.page_content, regulation, section)
            all_goals.extend(goals)
        
        print(f"✓ Extracted {len(all_goals)} goals")
        return all_goals


# ==================== MAIN AGENT ====================

class RegulationIntelligenceAgent:
    """Main orchestrator"""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.kb_builder = KnowledgeBaseBuilder()
        self.extractor = ObligationExtractor()
        
        self.regulatory_kb = None
        self.policy_kb = None
        self.rag_engine = None
    
    def setup(self, use_existing: bool = False, download_pdfs: bool = False):
        """Setup knowledge bases"""
        print("\n" + "="*60)
        print("REGULATION INTELLIGENCE AGENT - SETUP")
        print("="*60)
        
        if use_existing:
            try:
                print("\nLoading existing KBs...")
                self.regulatory_kb = self.kb_builder.load_existing_kb(Config.PERSIST_DIR_REGULATORY)
                self.policy_kb = self.kb_builder.load_existing_kb(Config.PERSIST_DIR_POLICY)
                self.rag_engine = ComplianceRAGEngine(self.regulatory_kb, self.policy_kb)
                print("✓ Setup complete!")
                return
            except Exception as e:
                print(f"Failed to load: {e}")
                print("Building new KBs...")
        
        # Create documents
        print("\nCreating documents...")
        
        if download_pdfs:
            print("\n=== Downloading Regulatory PDFs ===")
            regulatory_docs = []
            
            # Download priority regulations (Visa + PCI-DSS + GDPR)
            priority_sources = ["VISA_CORE_RULES", "PCI_DSS", "GDPR", 
                              "VISA_MERCHANT_DATA_STANDARDS", "VISA_GLOBAL_ACQUIRER_RISK_STANDARDS"]
            
            for source_key in priority_sources:
                if source_key in REGULATORY_SOURCES:
                    source = REGULATORY_SOURCES[source_key]
                    print(f"\nDownloading: {source['name']}")
                    filepath = self.doc_processor.download_pdf(source['url'], source['local_path'])
                    
                    if filepath and filepath.endswith('.pdf'):
                        docs = self.doc_processor.load_pdf(filepath)
                        if docs:
                            regulatory_docs.extend(docs)
                            print(f"  → Added {len(docs)} pages")
            
            if not regulatory_docs:
                print("\n⚠ No PDFs loaded, using mock data")
                regulatory_docs = self.doc_processor.create_mock_regulatory()
        else:
            print("Using mock regulatory data (set download_pdfs=True for real PDFs)")
            regulatory_docs = self.doc_processor.create_mock_regulatory()
        
        policy_docs = self.doc_processor.create_mock_policies()
        
        # Build KBs
        self.regulatory_kb = self.kb_builder.build_kb(
            regulatory_docs, 
            Config.PERSIST_DIR_REGULATORY, 
            "regulatory"
        )
        self.policy_kb = self.kb_builder.build_kb(
            policy_docs, 
            Config.PERSIST_DIR_POLICY, 
            "policy"
        )
        
        # Initialize RAG
        self.rag_engine = ComplianceRAGEngine(self.regulatory_kb, self.policy_kb)
        print("\n✓ Setup complete!")
    
    def mine_obligations(self, regulation: str, source_type: str = "regulatory") -> List[ComplianceGoal]:
        """Mine obligations from KB"""
        print(f"\n=== Mining from {regulation} ===")
        
        kb = self.regulatory_kb if source_type == "regulatory" else self.policy_kb
        all_docs = kb.similarity_search("", k=100)[:10]  # Limit to 10 chunks
        
        goals = self.extractor.extract_from_documents(all_docs, regulation)
        return goals
    
    def save_goals(self, goals: List[ComplianceGoal], filename: str):
        """Save to JSON"""
        output_path = Path("./output") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump([g.model_dump() for g in goals], f, indent=2)
        
        print(f"✓ Saved {len(goals)} goals to {output_path}")


# ==================== DEMO ====================

def run_demo():
    """Run demo"""
    
    agent = RegulationIntelligenceAgent()
    
    # For quick testing: use_existing=False, download_pdfs=False (uses mock data)
    # For real data: use_existing=False, download_pdfs=True (downloads Visa + PCI + GDPR PDFs)
    # For fast restart: use_existing=True (loads from disk)
    agent.setup(use_existing=False, download_pdfs=False)
    
    print("\n" + "="*60)
    print("DEMO 1: RAG Query - Regulatory")
    print("="*60)
    
    questions = [
        "What data cannot be stored after authorization?",
        "What are Visa's rules for data security?",
        "How should PAN be protected?"
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        answer = agent.rag_engine.query_regulations(q)
        print(f"A: {answer[:250]}...\n")
    
    print("\n" + "="*60)
    print("DEMO 2: RAG Query - Policy")
    print("="*60)
    
    policy_q = [
        "What is the MFA policy?",
        "How long do we retain data?",
        "What is the incident response time?"
    ]
    
    for q in policy_q:
        print(f"\nQ: {q}")
        answer = agent.rag_engine.query_policies(q)
        print(f"A: {answer[:250]}...\n")
    
    print("\n" + "="*60)
    print("DEMO 3: Obligation Mining")
    print("="*60)
    
    reg_goals = agent.mine_obligations("PCI-DSS v4.0 + Visa Rules", "regulatory")
    
    print(f"\n✓ Extracted {len(reg_goals)} regulatory goals")
    for goal in reg_goals[:5]:  # Show top 5
        print(f"\n{goal.goal_id}: {goal.goal_description}")
        print(f"  Risk: {goal.risk_level} | Verb: {goal.verb}")
    
    agent.save_goals(reg_goals, "pci_visa_goals.json")
    
    policy_goals = agent.mine_obligations("Company Policy", "policy")
    agent.save_goals(policy_goals, "company_policy_goals.json")
    
    print("\n" + "="*60)
    print("DEMO 4: Single Text Extraction")
    print("="*60)
    
    sample = """
The controller shall implement appropriate technical and organisational measures 
to ensure security appropriate to the risk, including:
(a) pseudonymisation and encryption of personal data;
(b) ongoing confidentiality, integrity, availability and resilience.
    """
    
    extractor = ObligationExtractor()
    goals = extractor.extract_from_text(sample, "GDPR", "Article 32")
    
    print(f"\n✓ Extracted {len(goals)} GDPR goals")
    if goals:
        print(json.dumps([g.model_dump() for g in goals[:2]], indent=2))
    
    print("\n" + "="*60)
    print("DEMO COMPLETE!")
    print("="*60)
    print(f"\nGenerated files:")
    print("  - output/pci_visa_goals.json")
    print("  - output/company_policy_goals.json")


def download_all_regulations():
    """Utility function to download all regulatory PDFs"""
    print("\n" + "="*60)
    print("DOWNLOADING ALL REGULATORY SOURCES")
    print("="*60)
    
    processor = DocumentProcessor()
    
    for key, source in REGULATORY_SOURCES.items():
        print(f"\n[{key}] {source['name']}")
        processor.download_pdf(source['url'], source['local_path'])
    
    print("\n✓ Download complete! Files saved to:", Config.DATA_DIR)


if __name__ == "__main__":
    # Set API key
    os.environ["OPENROUTER_API_KEY"] = "your-key-here"
    
    run_demo()