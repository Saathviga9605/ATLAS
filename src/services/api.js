/**
 * Backend API Service
 * Connects React frontend to FastAPI backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      const errorMessage = typeof error.detail === 'string' 
        ? error.detail 
        : JSON.stringify(error.detail || error);
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

/**
 * Health Check
 */
export async function checkHealth() {
  return fetchAPI('/health');
}

/**
 * Get system status
 */
export async function getSystemStatus() {
  return fetchAPI('/');
}

// ============= Monitoring Agent APIs =============

/**
 * Detect violations in content
 */
export async function detectViolation(content, source_type = 'support_chat', source_id = null) {
  // Map frontend source types to backend accepted values
  const sourceTypeMap = {
    'SUPPORT_TICKET': 'support_chat',
    'LOG_FILE': 'application_log',
    'EMAIL': 'email',
    'DATABASE_RECORD': 'database',
    'API_REQUEST': 'api_request',
    'CHAT_MESSAGE': 'support_chat',
    'TRANSACTION': 'transaction'
  };
  
  const mappedSourceType = sourceTypeMap[source_type] || source_type.toLowerCase();
  
  return fetchAPI('/monitor/ingest', {
    method: 'POST',
    body: JSON.stringify({ 
      content, 
      source_type: mappedSourceType, 
      source_id: source_id || `src_${Date.now()}`,
      timestamp: new Date().toISOString()
    }),
  });
}

/**
 * Get all violations
 */
export async function getViolations() {
  const response = await fetchAPI('/monitor/violations');
  return response.violations || [];
}

/**
 * Get monitoring stats
 */
export async function getMonitoringStats() {
  return fetchAPI('/monitor/stats');
}

/**
 * Scan content across multiple regulations
 */
export async function scanMultiRegulation(content, source_type = 'support_chat', source_id = null) {
  return fetchAPI('/monitor/scan-multi', {
    method: 'POST',
    body: JSON.stringify({
      content,
      source_type,
      source_id: source_id || `multi_${Date.now()}`,
      timestamp: new Date().toISOString()
    }),
  });
}

// ============= Cognitive Agent APIs =============

/**
 * Analyze violation with LLM reasoning
 */
export async function analyzeViolation(violationId) {
  return fetchAPI(`/agent/analyze/${violationId}`, {
    method: 'POST',
  });
}

/**
 * Get remediation plan
 */
export async function getRemediation(violationId) {
  return fetchAPI(`/agent/remediate/${violationId}`);
}

/**
 * Get agent reasoning history
 */
export async function getReasoningHistory() {
  return fetchAPI('/agent/reasoning-history');
}

// ============= Evidence Layer APIs =============

/**
 * Get all evidence records
 */
export async function getEvidence() {
  const response = await fetchAPI('/evidence');
  return response.evidence || [];
}

/**
 * Get evidence by ID
 */
export async function getEvidenceById(evidenceId) {
  return fetchAPI(`/evidence/${evidenceId}`);
}

/**
 * Get explanation for evidence
 */
export async function getExplanation(evidenceId) {
  return fetchAPI(`/evidence/explain/${evidenceId}`);
}

// ============= Audit Chain APIs =============

/**
 * Get audit chain
 */
export async function getAuditChain() {
  return fetchAPI('/audit/chain');
}

/**
 * Verify audit chain integrity
 */
export async function verifyAuditChain() {
  return fetchAPI('/audit/verify');
}

/**
 * Get audit bundle
 */
export async function getAuditBundle(evidenceId) {
  return fetchAPI(`/audit/bundle/${evidenceId}`);
}

/**
 * Get agent status and activity
 */
export async function getAgentStatus() {
  return fetchAPI('/agents/status');
}

// Export all as named exports for convenience
const api = {
  checkHealth,
  getSystemStatus,
  detectViolation,
  getViolations,
  getMonitoringStats,
  scanMultiRegulation,
  analyzeViolation,
  getRemediation,
  getReasoningHistory,
  getEvidence,
  getEvidenceById,
  getExplanation,
  getAuditChain,
  verifyAuditChain,
  getAuditBundle,
  getAgentStatus,
};

export default api;
