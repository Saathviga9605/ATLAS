/**
 * Cognitive Compliance Agent Service
 * 
 * Autonomous compliance violation detection and reasoning system for financial services.
 * Implements PCI-DSS, GDPR, and internal policy compliance checks.
 */

// Regulation contexts and policy database
const REGULATIONS = {
  'PCI-DSS': {
    '3.2.1': 'Primary Account Number (PAN) must not be stored or transmitted in plaintext in logs, support tickets, or customer communications.',
    '3.4': 'PAN must be rendered unreadable anywhere it is stored (including portable digital media, backup media, in logs).',
    '4.2': 'Never send unprotected PANs by end-user messaging technologies (e.g., e-mail, instant messaging, chat).',
    '8.2.1': 'User password/passphrase must meet minimum 7 characters (or 12 for system passwords) and contain both numeric and alphabetic characters.',
  },
  'GDPR': {
    'Article 5(1)(e)': 'Personal data shall be kept in a form which permits identification of data subjects for no longer than is necessary.',
    'Article 17': 'Data subjects have the right to obtain erasure of personal data without undue delay.',
    'Article 32': 'Appropriate technical and organizational measures must be implemented to ensure security of processing.',
    'Article 33': 'Personal data breach must be notified to supervisory authority within 72 hours.',
  },
  'CCPA': {
    '1798.100': 'Consumers have the right to know what personal information is collected about them.',
    '1798.105': 'Consumers have the right to request deletion of their personal information.',
  },
  'INTERNAL_POLICY': {
    'DATA_RETENTION': 'Customer data must not be retained longer than 24 months unless legally required.',
    'ACCESS_CONTROL': 'All access to sensitive data must be logged and require MFA.',
    'ENCRYPTION': 'All sensitive data at rest and in transit must use AES-256 or equivalent encryption.',
  }
};

// PAN detection patterns (Primary Account Number - Credit Card)
const PAN_PATTERNS = [
  // VISA: 4xxx-xxxx-xxxx-xxxx (13-16 digits)
  /\b4[0-9]{12}(?:[0-9]{3})?\b/,
  // MasterCard: 5[1-5]xx-xxxx-xxxx-xxxx or 2[2-7]xx-xxxx-xxxx-xxxx
  /\b(?:5[1-5][0-9]{14}|2(?:2[2-9]|[3-6][0-9]|7[01])[0-9]{12})\b/,
  // AMEX: 3[47]xx-xxxxxx-xxxxx (15 digits)
  /\b3[47][0-9]{13}\b/,
  // Discover: 6(?:011|5[0-9]{2})-xxxx-xxxx-xxxx
  /\b6(?:011|5[0-9]{2})[0-9]{12}\b/,
  // Generic pattern with common separators
  /\b[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}\b/,
];

// PII detection patterns
const PII_PATTERNS = {
  SSN: /\b\d{3}-\d{2}-\d{4}\b/,
  EMAIL: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/,
  PHONE: /\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/,
  IP_ADDRESS: /\b(?:\d{1,3}\.){3}\d{1,3}\b/,
};

/**
 * Compliance Agent Class
 * Performs autonomous compliance checking and reasoning
 */
class ComplianceAgent {
  constructor() {
    this.violationIdCounter = 1000;
    this.detectedViolations = [];
  }

  /**
   * Generate unique violation ID
   */
  generateViolationId() {
    return `VIOL_${this.violationIdCounter++}`;
  }

  /**
   * Detect PAN (Primary Account Number) in content
   */
  detectPAN(content) {
    for (const pattern of PAN_PATTERNS) {
      const matches = content.match(pattern);
      if (matches) {
        // Basic Luhn algorithm check for credit card validation
        const cardNumber = matches[0].replace(/[\s\-]/g, '');
        if (this.luhnCheck(cardNumber)) {
          return {
            detected: true,
            value: matches[0],
            type: 'PAN',
            sanitized: this.maskPAN(matches[0])
          };
        }
      }
    }
    return { detected: false };
  }

  /**
   * Luhn algorithm for credit card validation
   */
  luhnCheck(cardNumber) {
    let sum = 0;
    let isEven = false;
    
    for (let i = cardNumber.length - 1; i >= 0; i--) {
      let digit = parseInt(cardNumber.charAt(i), 10);
      
      if (isEven) {
        digit *= 2;
        if (digit > 9) {
          digit -= 9;
        }
      }
      
      sum += digit;
      isEven = !isEven;
    }
    
    return (sum % 10) === 0;
  }

  /**
   * Mask PAN for safe display
   */
  maskPAN(pan) {
    const cleaned = pan.replace(/[\s\-]/g, '');
    const last4 = cleaned.slice(-4);
    return `****-****-****-${last4}`;
  }

  /**
   * Detect PII in content
   */
  detectPII(content) {
    const detected = [];
    
    for (const [type, pattern] of Object.entries(PII_PATTERNS)) {
      const matches = content.match(pattern);
      if (matches) {
        detected.push({
          type,
          value: matches[0],
          sanitized: this.maskPII(matches[0], type)
        });
      }
    }
    
    return detected;
  }

  /**
   * Mask PII for safe display
   */
  maskPII(value, type) {
    if (type === 'SSN') {
      return `***-**-${value.slice(-4)}`;
    } else if (type === 'EMAIL') {
      const [name, domain] = value.split('@');
      return `${name.slice(0, 2)}***@${domain}`;
    } else if (type === 'PHONE') {
      return `***-***-${value.slice(-4)}`;
    }
    return '***REDACTED***';
  }

  /**
   * Assess risk severity based on violation type and context
   */
  assessRiskSeverity(violationType, context) {
    const severityMatrix = {
      PAN_PLAINTEXT: 'Critical',
      PAN_LOG: 'Critical',
      PAN_SUPPORT: 'Critical',
      SSN_EXPOSED: 'High',
      PII_UNENCRYPTED: 'High',
      POLICY_OUTDATED: 'Medium',
      ACCESS_UNLOGGED: 'Medium',
      WEAK_PASSWORD: 'Low',
    };

    return severityMatrix[violationType] || 'Medium';
  }

  /**
   * Determine if action can be executed autonomously
   */
  determineAutonomyLevel(severity, actionType) {
    // Critical violations require human approval
    if (severity === 'Critical') {
      if (actionType === 'MASK_DATA' || actionType === 'BLOCK_ACCESS') {
        return 'AUTONOMOUS';
      }
      return 'HUMAN_APPROVAL_REQUIRED';
    }
    
    // High severity - most actions are autonomous except deletion
    if (severity === 'High') {
      if (actionType === 'DELETE_DATA') {
        return 'HUMAN_APPROVAL_REQUIRED';
      }
      return 'AUTONOMOUS';
    }
    
    // Medium and Low can be autonomous
    return 'AUTONOMOUS';
  }

  /**
   * Main compliance analysis function
   * Analyzes content for violations and produces structured output
   */
  analyzeViolation(params) {
    const {
      regulationContext = REGULATIONS['PCI-DSS'],
      goalDescription = 'Ensure PCI-DSS compliance for payment card data protection',
      sourceType = 'SUPPORT_TICKET',
      contentSnippet,
      customViolationId = null
    } = params;

    const violationId = customViolationId || this.generateViolationId();
    
    // Detect PAN
    const panDetection = this.detectPAN(contentSnippet);
    
    if (panDetection.detected) {
      const violation = {
        violation_id: violationId,
        is_violation: true,
        explanation: `The detected content contains a Primary Account Number (PAN) exposed in plaintext within ${sourceType.toLowerCase().replace('_', ' ')}. ` +
                    `This is explicitly prohibited by PCI-DSS as it poses a critical risk of unauthorized access to payment card data. ` +
                    `The PAN "${panDetection.sanitized}" must be immediately removed or masked to prevent data breach.`,
        regulation_reference: 'PCI-DSS 3.2.1, 4.2',
        risk_severity: 'Critical',
        recommended_action: `Immediately mask the PAN in the ${sourceType.toLowerCase().replace('_', ' ')} to "${panDetection.sanitized}". ` +
                          `Remove the plaintext content from all records and logs. Alert security team for incident review.`,
        autonomy_level: 'AUTONOMOUS',
        detected_data: panDetection.sanitized,
        original_source: sourceType,
        timestamp: new Date().toISOString(),
        remediation_script: this.generateRemediationScript('PAN', panDetection.value, panDetection.sanitized)
      };
      
      this.detectedViolations.push(violation);
      return violation;
    }

    // Detect other PII
    const piiDetections = this.detectPII(contentSnippet);
    if (piiDetections.length > 0) {
      const piiTypes = piiDetections.map(p => p.type).join(', ');
      const violation = {
        violation_id: violationId,
        is_violation: true,
        explanation: `Personally Identifiable Information (${piiTypes}) detected in ${sourceType.toLowerCase().replace('_', ' ')}. ` +
                    `This may violate GDPR Article 32 requirements for data protection and security measures.`,
        regulation_reference: 'GDPR Article 32',
        risk_severity: 'High',
        recommended_action: `Review and encrypt or mask the PII data. Ensure proper access controls are in place.`,
        autonomy_level: 'AUTONOMOUS',
        detected_data: piiDetections.map(p => p.sanitized).join(', '),
        original_source: sourceType,
        timestamp: new Date().toISOString(),
        remediation_script: null
      };
      
      this.detectedViolations.push(violation);
      return violation;
    }

    // No violation detected
    return {
      violation_id: violationId,
      is_violation: false,
      explanation: 'No compliance violations detected in the provided content.',
      regulation_reference: 'N/A',
      risk_severity: 'None',
      recommended_action: 'Continue monitoring.',
      autonomy_level: 'N/A',
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Generate remediation script for automated fixes
   */
  generateRemediationScript(violationType, originalValue, maskedValue) {
    if (violationType === 'PAN') {
      return {
        type: 'MASK_AND_LOG',
        steps: [
          {
            action: 'REPLACE_TEXT',
            from: originalValue,
            to: maskedValue,
            description: 'Replace plaintext PAN with masked version'
          },
          {
            action: 'LOG_INCIDENT',
            severity: 'CRITICAL',
            description: 'Log PAN exposure incident for security review'
          },
          {
            action: 'NOTIFY_SECURITY',
            recipients: ['security@company.com', 'compliance@company.com'],
            description: 'Alert security team of PCI-DSS violation'
          }
        ]
      };
    }
    return null;
  }

  /**
   * Batch analyze multiple content items
   */
  batchAnalyze(contentItems) {
    return contentItems.map(item => this.analyzeViolation(item));
  }

  /**
   * Get all detected violations
   */
  getViolations(filter = {}) {
    let violations = [...this.detectedViolations];
    
    if (filter.severity) {
      violations = violations.filter(v => v.risk_severity === filter.severity);
    }
    
    if (filter.regulation) {
      violations = violations.filter(v => 
        v.regulation_reference.includes(filter.regulation)
      );
    }
    
    return violations;
  }

  /**
   * Clear violation history
   */
  clearViolations() {
    this.detectedViolations = [];
    this.violationIdCounter = 1000;
  }

  /**
   * Export violations as audit-ready JSON
   */
  exportAuditReport() {
    return {
      report_id: `AUDIT_${Date.now()}`,
      generated_at: new Date().toISOString(),
      total_violations: this.detectedViolations.length,
      critical_count: this.detectedViolations.filter(v => v.risk_severity === 'Critical').length,
      high_count: this.detectedViolations.filter(v => v.risk_severity === 'High').length,
      violations: this.detectedViolations,
      compliance_status: this.detectedViolations.filter(v => v.risk_severity === 'Critical').length > 0 
        ? 'NON-COMPLIANT' 
        : 'AT RISK'
    };
  }
}

// Export singleton instance
const complianceAgent = new ComplianceAgent();

export default complianceAgent;
export { ComplianceAgent, REGULATIONS };
