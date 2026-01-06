# ATLAS - Autonomous Compliance Intelligence Platform

**A**utonomous **T**rust **L**ayer for **A**gent **S**ystems  
Multi-Regulation Compliance Monitoring with AI-Powered Analysis

---

## Overview

ATLAS is an autonomous compliance monitoring system that detects, analyzes, and remediates regulatory violations across **PCI-DSS**, **GDPR**, and **CCPA** frameworks in real-time. It combines pattern-based detection, AI-powered analysis via OpenRouter, and cryptographic evidence chains to provide comprehensive compliance assurance.

### Key Features

**Multi-Regulation Detection** - Simultaneous scanning for PCI-DSS, GDPR, and CCPA violations  
**AI-Powered Analysis** - OpenRouter LLM integration for intelligent violation reasoning  
**Natural Language Queries** - Ask compliance questions in plain English  
**Evidence Chain** - Cryptographic hash-chain for immutable audit trails  
**Real-time Monitoring** - Live ingestion from multiple data sources  
**Automated Remediation** - AI-generated fix suggestions and action plans  
**Analytics Dashboard** - Risk heatmaps, severity tracking, and statistics  
**Autonomous Agents** - Self-orchestrating compliance workflows  

---

## Architecture

### Technology Stack

**Backend:**
- FastAPI 0.115.0 - High-performance async API framework
- ChromaDB 0.5.11 - Vector database for RAG
- Sentence Transformers 2.3.1 - Embeddings generation
- OpenAI/Anthropic SDKs - LLM integrations
- Pydantic 2.8.0 - Data validation

**Frontend:**
- React 19.2.3 - UI framework
- React Router 7.11.0 - Navigation
- Framer Motion 12.23.26 - Animations
- Lucide React - Icon library
- Recharts 3.6.0 - Data visualization

### System Components

```
Backend (Port 8000)
├── Monitoring Agent       → Real-time violation detection (PCI-DSS, GDPR, CCPA)
├── Cognitive Agent        → AI analysis & remediation (OpenRouter LLM)
├── Evidence Layer         → Cryptographic audit trail (Hash-chain)
├── RAG Service            → Regulatory knowledge base (Vector search)
└── API Layer              → RESTful endpoints (FastAPI)

Frontend (Port 3000)
├── Compliance Overview    → Dashboard with risk heatmaps
├── Multi-Regulation Test  → Interactive scanner
├── Compliance Query       → AI chat interface
├── Live Monitoring        → Real-time ingestion
├── Violation Analysis     → AI-powered insights
├── Evidence Viewer        → Audit trail explorer
└── Agent Activity         → Autonomous agent logs
```

---

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn
- OpenRouter API key (for AI features)

### Installation & Setup

#### 1. Clone and Install

```bash
# Clone repository
git clone <repository-url>
cd mergeconflicts

# Backend setup
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Frontend setup (from project root)
cd ..
npm install
```

#### 2. Environment Configuration

Create `backend/.env`:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=anthropic/claude-3.5-sonnet
```

Create `.env.local` in project root:
```env
REACT_APP_API_BASE_URL=http://localhost:8000
```

#### 3. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload
```
Backend running at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

**Terminal 2 - Frontend:**
```bash
npm start
```
 Frontend running at `http://localhost:3000`

---

## 📖 User Guide

### 1. Compliance Overview Dashboard
**URL:** `http://localhost:3000/`

- **Global Compliance Status** - Compliant/Non-Compliant indicator
- **Multi-Regulation Risk Heatmap** - Violations by PCI-DSS, GDPR, CCPA, SOX
- **Severity Distribution** - Critical, High, Medium counts with charts
- **Key Active Risks** - Recent violations with AI analysis links
- **Agent Activity Feed** - Real-time autonomous agent logs

---

### 2. Multi-Regulation Scanner
**URL:** `http://localhost:3000/multi-regulation-test`

Interactive testing interface for all regulations. Click sample buttons to load test data:

**PCI-DSS Sample:**
```
Transaction for card 4532-1234-5678-9010 was declined
```

**GDPR Sample:**
```
Contact: john.doe@example.com, Phone: +1-555-123-4567, IP: 192.168.1.100
```

**CCPA Sample:**
```
California resident SSN: 123-45-6789, Driver License: CA-D1234567
```

**Mixed Sample (All Regulations):**
```
Card 4111111111111111, Email: jane@example.com
Phone: +44-20-7123-4567, SSN: 987-65-4321, IP: 10.0.0.1
```

**How to Use:**
1. Click a sample button (PCI-DSS, GDPR, CCPA, or Mixed)
2. Click "Scan All Regulations"
3. View detected violations grouped by regulation
4. Click "Download JSON" to export results

---

### 3. Natural Language Compliance Assistant
**URL:** `http://localhost:3000/compliance-query`

Ask compliance questions in plain English using AI-powered RAG.

**Sample Questions:**
- "What are the requirements for PCI-DSS compliance?"
- "How should we handle GDPR data deletion requests?"
- "What are CCPA consumer rights regarding personal data?"
- "Explain the difference between PCI-DSS and GDPR"

**Features:**
- Chat-style interface with message history
- AI-powered responses using regulatory knowledge base
- Sample question shortcuts for quick testing
- Context-aware follow-up questions

---

### 4. Live Monitoring
**URL:** `http://localhost:3000/monitoring`

Real-time data ingestion and violation detection.

**Source Types:**
- **SUPPORT_TICKET** - Customer service interactions
- **APPLICATION_LOG** - System logs
- **TRANSACTION_DATA** - Payment processing
- **EMAIL_CONTENT** - Email communications

**How to Use:**
1. Select source type from dropdown
2. Paste or type data to scan
3. Click "Scan for Violations"
4. Review detected violations with severity levels
5. System automatically creates evidence records

---

### 5. AI Violation Analysis
**URL:** `http://localhost:3000/violation-analysis`

Deep AI analysis of compliance violations using OpenRouter LLM.

**Analysis Includes:**
- **Root Cause** - Why the violation occurred
- **Impact Assessment** - Business, regulatory, and reputation risks
- **Regulatory Penalties** - Potential fines (PCI-DSS: $5K-$100K/month, GDPR: €20M/4% revenue)
- **Remediation Steps** - Specific actions to resolve
- **Prevention Strategies** - Long-term solutions and best practices

**How to Use:**
1. Navigate to violation list
2. Click "Analyze with AI" on any violation
3. View comprehensive analysis
4. Follow suggested remediation steps

---

### 6. Evidence & Audit Trail
**URL:** `http://localhost:3000/evidence`

Cryptographic hash-chain verification for immutable audit logs.

**Features:**
- Complete event log of all compliance activities
- Hash-chain integrity verification 
- Tamper detection via cryptographic linking
- JSON export for compliance reports

**Evidence Structure:**
```json
{
  "id": "EVD_ABC123",
  "timestamp": "2026-01-05T10:30:00Z",
  "event_type": "violation_detected",
  "violation_id": "VIO_XYZ789",
  "regulation": "PCI-DSS",
  "hash": "abc123...",
  "previous_hash": "def456..."
}
```

---

### 7. Autonomous Agent Activity
**URL:** `http://localhost:3000/agents`

View real-time activity of autonomous compliance agents.

**Agent Types:**
- **Monitoring Agent** - Scans data sources for violations
- **Evidence Agent** - Collects and chains proof
- **Cognitive Agent** - Analyzes violations with AI

---

## 🔌 API Reference

### Base URL
```
http://localhost:8000
```

### Key Endpoints

#### Multi-Regulation Scanning
**POST** `/monitor/scan-multi`

Scan text for violations across all regulations.

```bash
curl -X POST http://localhost:8000/monitor/scan-multi \
  -H "Content-Type: application/json" \
  -d '{
    "data": "Card 4111111111111111, email john@example.com",
    "source_type": "support_chat"
  }'
```

**Response:**
```json
{
  "violations": [
    {
      "id": "VIO_ABC123",
      "regulation": "PCI-DSS",
      "violation_type": "UNMASKED_PAN",
      "description": "Credit card number detected in plaintext",
      "matched_pattern": "4111111111111111",
      "severity": "critical"
    }
  ],
  "summary": {
    "total_violations": 2,
    "regulations_affected": ["PCI-DSS", "GDPR"],
    "by_regulation": {"PCI-DSS": 1, "GDPR": 1},
    "by_severity": {"critical": 1, "high": 1}
  }
}
```

#### Monitoring Statistics
**GET** `/monitor/stats`

```bash
curl http://localhost:8000/monitor/stats
```

**Response:**
```json
{
  "total_violations": 15,
  "by_regulation": {"PCI-DSS": 5, "GDPR": 7, "CCPA": 3},
  "by_severity": {"critical": 3, "high": 8, "medium": 4}
}
```

#### Natural Language Query
**POST** `/regulations/query`

```bash
curl -X POST http://localhost:8000/regulations/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What are PCI-DSS requirements?"}'
```

#### AI Violation Analysis
**POST** `/cognitive/analyze`

```bash
curl -X POST http://localhost:8000/cognitive/analyze \
  -H "Content-Type: application/json" \
  -d '{"violation_id":"VIO_ABC123"}'
```

#### Evidence Chain
**GET** `/evidence`

```bash
curl http://localhost:8000/evidence
```

**Full API Documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## Detection Capabilities

### PCI-DSS (Payment Card Industry)
**Detects:** Unmasked credit card numbers (PAN)  
**Validation:** Luhn algorithm verification  
**Patterns:**
- `4111111111111111` ✓ Visa
- `5424-0000-0000-0015` ✓ Mastercard
- `3782-822463-10005` ✓ Amex
- `**** **** **** 1111` ✗ Masked (allowed)

**Severity:** Critical  
**Penalty:** $5,000 - $100,000/month

---

### GDPR (General Data Protection Regulation)
**Detects:** Personal identifiable information  
**Patterns:**
- Email: `john.doe@example.com` ✓
- Phone: `+1-555-123-4567` ✓
- Phone: `+44-20-7123-4567` ✓
- IP: `192.168.1.100` ✓

**Severity:** High to Critical  
**Penalty:** €20M or 4% global revenue

---

### CCPA (California Consumer Privacy Act)
**Detects:** California consumer personal data  
**Patterns:**
- SSN: `123-45-6789` ✓
- Driver License: `CA-D1234567` ✓
- Driver License: `CA-A9876543` ✓

**Severity:** High  
**Penalty:** $2,500 - $7,500 per violation

---

## Testing

### Using the Multi-Regulation Scanner UI

1. Navigate to `http://localhost:3000/multi-regulation-test`
2. Click sample buttons to load test data
3. Click "Scan All Regulations"
4. Verify violations are detected correctly

### API Testing with PowerShell

```powershell
# Test PCI-DSS
$body = @{
    data = "Transaction for card 4532-1234-5678-9010"
    source_type = "support_chat"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/monitor/scan-multi" `
    -Method POST -Body $body -ContentType "application/json"

# Get Statistics
Invoke-RestMethod -Uri "http://localhost:8000/monitor/stats"
```

### API Testing with cURL

```bash
# Multi-regulation scan
curl -X POST http://localhost:8000/monitor/scan-multi \
  -H "Content-Type: application/json" \
  -d '{"data":"Card 4111111111111111","source_type":"support_chat"}'

# Get statistics
curl http://localhost:8000/monitor/stats

# Get evidence
curl http://localhost:8000/evidence
```

---

##  5-Minute Demo Script

### Minute 1: Introduction
"ATLAS is an autonomous compliance platform that monitors PCI-DSS, GDPR, and CCPA violations in real-time with AI-powered analysis and immutable audit trails."

### Minute 2: Multi-Regulation Detection
1. Open `http://localhost:3000/multi-regulation-test`
2. Click "Mixed (All)" sample
3. Click "Scan All Regulations"
4. Show violations across all frameworks
5. Download JSON evidence

### Minute 3: Natural Language AI
1. Navigate to `http://localhost:3000/compliance-query`
2. Ask "What are PCI-DSS requirements?"
3. Show AI response
4. Ask "How to handle GDPR data deletion?"

### Minute 4: Analytics & Analysis
1. Open `http://localhost:3000/` (Overview)
2. Show Multi-Regulation Risk Heatmap
3. Show Violation Severity Distribution
4. Click "AI Analysis Tool" on violation
5. View remediation steps

### Minute 5: Evidence & Audit
1. Navigate to `http://localhost:3000/evidence`
2. Show hash-chain verification ( Chain Verified)
3. Download evidence JSON
4. Highlight: "Each event cryptographically linked for tamper-proof compliance"

---

##  Troubleshooting

### Backend Won't Start

**Issue:** `ModuleNotFoundError: No module named 'fastapi'`  
**Fix:**
```bash
cd backend
pip install -r requirements.txt
```

**Issue:** `Port 8000 already in use`  
**Fix:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Frontend Won't Start

**Issue:** `npm ERR! missing script: start`  
**Fix:**
```bash
npm install
npm start
```

**Issue:** `Port 3000 already in use`  
**Fix:**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### API Returns 422 Errors

**Issue:** `422 Unprocessable Entity`  
**Cause:** Invalid `source_type` value

**Valid source types:**
- `support_chat`
- `application_log`
- `transaction_data`
- `email_content`

**Example:**
```json
// ❌ Wrong
{"data": "...", "source_type": "SUPPORT_TICKET"}

// ✅ Correct
{"data": "...", "source_type": "support_chat"}
```

### No Violations Detected

**Possible causes:**
1. Invalid credit card (fails Luhn check)
2. Malformed email/phone/SSN
3. Already masked data

**Test with valid data:**
```
PCI-DSS: 4111111111111111
GDPR: test@example.com
CCPA: 123-45-6789
```

### AI Analysis Fails

**Issue:** `OpenRouter API key not configured`  
**Fix:**
1. Create `backend/.env`
2. Add `OPENROUTER_API_KEY=sk-or-v1-...`
3. Restart backend

---

## Project Structure

```
mergeconflicts/
├── backend/                    # FastAPI Python backend
│   ├── main.py                 # Application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (create this)
│   ├── monitoring_agent/       # Violation detection engine
│   │   ├── api.py              # REST endpoints
│   │   ├── detectors.py        # PCI-DSS, GDPR, CCPA detectors
│   │   ├── models.py           # Data schemas
│   │   └── store.py            # Violation persistence
│   ├── cognitive_agent/        # AI analysis & remediation
│   │   ├── api.py              # Cognitive endpoints
│   │   ├── reasoner_openrouter.py  # LLM integration
│   │   ├── remediation.py      # Fix generation
│   │   └── evidence.py         # Evidence collection
│   ├── evidence_layer/         # Audit trail management
│   │   ├── evidence_service.py # Hash chain logic
│   │   └── api.py              # Evidence endpoints
│   ├── rag/                    # Regulatory knowledge base
│   │   ├── regulation_intelligence_agent.py
│   │   └── regulatory_data/    # Compliance documents
│   ├── app/                    # Core services
│   │   ├── services/
│   │   │   ├── rag_service.py  # Vector search
│   │   │   └── ingestion_service.py
│   │   └── models/schemas.py   # API models
│   └── data/                   # Persistent storage
│       ├── violations.json     # Violation records
│       └── evidence.json       # Evidence chain
├── src/                        # React frontend
│   ├── App.js                  # Main router
│   ├── index.js                # Entry point
│   ├── components/
│   │   └── Sidebar.js          # Navigation
│   ├── pages/                  # Route pages
│   │   ├── ComplianceOverview.js    # Main dashboard
│   │   ├── MultiRegulationTest.js   # Interactive scanner
│   │   ├── ComplianceQuery.js       # AI chat
│   │   ├── LiveMonitoring.js        # Real-time ingestion
│   │   ├── ViolationAnalysis.js     # AI analysis
│   │   ├── Evidence.js              # Audit trail
│   │   ├── AgentActivity.js         # Agent logs
│   │   ├── GoalGraph.js             # Compliance goals
│   │   └── Remediation.js           # Action plans
│   └── services/
│       └── api.js              # Backend API client
├── public/                     # Static assets
│   ├── index.html
│   └── manifest.json
├── package.json                # Node dependencies
└── README.md                   # This file
```

---

##  Security

### Data Protection
- ✅ Credit cards **never stored in plaintext**
- ✅ Violations logged with **masked PAN** (e.g., `4111********1111`)
- ✅ Evidence chain uses **SHA-256 cryptographic hashing**
- ✅ API keys in `.env` files (not committed to Git)

### Production Recommendations
1. **Enable HTTPS** - Use TLS certificates
2. **Restrict CORS** - Limit to specific domains
3. **Add Authentication** - Implement JWT or OAuth
4. **Rate Limiting** - Prevent API abuse
5. **Input Validation** - Sanitize all user inputs
6. **Secrets Management** - Use HashiCorp Vault or AWS Secrets Manager
7. **Network Segmentation** - Isolate backend from public internet

---

## 🛠️ Development

### Adding New Regulations

**1. Create Detector Class:**
```python
# backend/monitoring_agent/detectors.py

class SOXDetector:
    """Detects SOX (Sarbanes-Oxley) violations"""
    
    PATTERN = re.compile(r'...')
    
    def detect(self, text: str) -> List[dict]:
        # Detection logic
        pass
```

**2. Add to Multi-Detector:**
```python
class MultiRegulationDetector:
    def __init__(self):
        self.pan_detector = PANDetector()
        self.gdpr_detector = GDPRDetector()
        self.ccpa_detector = CCPADetector()
        self.sox_detector = SOXDetector()  # New
```

**3. Update Frontend:**
```javascript
// src/pages/MultiRegulationTest.js
const sampleData = {
  sox: "Financial data...",
  // ...
};
```

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
npm test
```

---

##  Performance

**Detection Speed:** <100ms per scan  
**AI Analysis:** 2-5 seconds (LLM-dependent)  
**Vector Search:** <50ms per query  
**Evidence Verification:** <10ms  
**Concurrent Users:** 100+ (tested)

---

##  Data Persistence

### Evidence Storage
- **Location:** `backend/data/evidence.json`
- **Format:** JSON array of evidence records
- **Backup:** Automatic on startup

### Violation Storage
- **Location:** `backend/data/violations.json`
- **Format:** JSON array of violations
- **Retention:** Persistent across restarts

### Vector Database
- **Location:** `backend/chroma_db/`
- **Purpose:** Regulation document embeddings
- **Rebuild:** Delete folder and restart

---


##  License

MIT License

---
