import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, AlertCircle, CheckCircle, FileText, Download } from 'lucide-react';
import * as api from '../services/api';

const MultiRegulationTest = () => {
  const [testData, setTestData] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const sampleData = {
    pciDss: "Customer called about card 4532-1234-5678-9010 declined at checkout.",
    gdpr: "Support ticket: User email john.doe@example.com requested data deletion. Phone: +1-555-123-4567, IP: 192.168.1.100",
    ccpa: "Consumer request: SSN 123-45-6789, Driver's License CA-D1234567 for California resident data access.",
    mixed: "Transaction failed for card 5424-0000-0000-0015. Customer email: jane@example.com, phone: +44-20-7123-4567, IP: 10.0.0.1. California resident SSN: 987-65-4321."
  };

  const handleScan = async () => {
    if (!testData.trim()) {
      setError('Please enter test data');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await api.scanMultiRegulation(testData, 'support_chat');
      setResults(response);
    } catch (err) {
      setError(err.message || 'Scan failed');
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (key) => {
    setTestData(sampleData[key]);
    setResults(null);
    setError('');
  };

  const downloadResults = () => {
    if (!results) return;
    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `multi-regulation-scan-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 space-y-6 max-w-7xl mx-auto"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-visa-blue to-visa-orange rounded-lg p-6 text-white">
        <div className="flex items-center gap-3 mb-2">
          <Shield size={32} />
          <h1 className="text-3xl font-bold">Multi-Regulation Compliance Scanner</h1>
        </div>
        <p className="text-white text-opacity-90">
          Test simultaneous detection across PCI-DSS, GDPR, and CCPA frameworks
        </p>
      </div>

      {/* Sample Data Loader */}
      <div className="bg-bg-card rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-3 text-text-primary">Quick Test Samples</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button
            onClick={() => loadSample('pciDss')}
            className="px-4 py-3 bg-blue-500 bg-opacity-10 text-blue-500 rounded-lg hover:bg-opacity-20 transition-all"
          >
            <FileText size={18} className="mx-auto mb-1" />
            PCI-DSS Only
          </button>
          <button
            onClick={() => loadSample('gdpr')}
            className="px-4 py-3 bg-purple-500 bg-opacity-10 text-purple-500 rounded-lg hover:bg-opacity-20 transition-all"
          >
            <FileText size={18} className="mx-auto mb-1" />
            GDPR Only
          </button>
          <button
            onClick={() => loadSample('ccpa')}
            className="px-4 py-3 bg-amber-500 bg-opacity-10 text-amber-500 rounded-lg hover:bg-opacity-20 transition-all"
          >
            <FileText size={18} className="mx-auto mb-1" />
            CCPA Only
          </button>
          <button
            onClick={() => loadSample('mixed')}
            className="px-4 py-3 bg-red-500 bg-opacity-10 text-red-500 rounded-lg hover:bg-opacity-20 transition-all"
          >
            <FileText size={18} className="mx-auto mb-1" />
            Mixed (All)
          </button>
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-bg-card rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-3 text-text-primary">Test Data Input</h3>
        <textarea
          value={testData}
          onChange={(e) => setTestData(e.target.value)}
          placeholder="Enter text to scan for compliance violations across multiple regulations..."
          className="w-full h-32 p-4 bg-bg-main border border-border-color rounded-lg text-text-primary font-mono text-sm focus:outline-none focus:ring-2 focus:ring-visa-blue"
        />
        <div className="flex gap-3 mt-4">
          <button
            onClick={handleScan}
            disabled={loading}
            className="px-6 py-2 bg-gradient-to-r from-visa-blue to-visa-orange text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Scanning...' : 'Scan All Regulations'}
          </button>
          <button
            onClick={() => { setTestData(''); setResults(null); setError(''); }}
            className="px-6 py-2 bg-border-color text-text-primary rounded-lg hover:bg-opacity-80 transition-all"
          >
            Clear
          </button>
        </div>
        {error && (
          <div className="mt-4 p-3 bg-red-500 bg-opacity-10 border border-red-500 rounded-lg flex items-center gap-2 text-red-500">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Results */}
      {results && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-bg-card rounded-lg p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-text-primary">Scan Results</h3>
            <button
              onClick={downloadResults}
              className="flex items-center gap-2 px-4 py-2 bg-visa-blue text-white rounded-lg hover:bg-opacity-90 transition-all"
            >
              <Download size={18} />
              Download JSON
            </button>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-4 bg-blue-500 bg-opacity-10 rounded-lg">
              <div className="text-2xl font-bold text-blue-500">{results.count || results.violations?.length || 0}</div>
              <div className="text-sm text-text-secondary mt-1">Total Violations</div>
            </div>
            <div className="text-center p-4 bg-red-500 bg-opacity-10 rounded-lg">
              <div className="text-2xl font-bold text-red-500">{results.violations?.filter(v => v.regulation === 'PCI-DSS').length || 0}</div>
              <div className="text-sm text-text-secondary mt-1">PCI-DSS</div>
            </div>
            <div className="text-center p-4 bg-purple-500 bg-opacity-10 rounded-lg">
              <div className="text-2xl font-bold text-purple-500">{results.violations?.filter(v => v.regulation === 'GDPR').length || 0}</div>
              <div className="text-sm text-text-secondary mt-1">GDPR</div>
            </div>
            <div className="text-center p-4 bg-amber-500 bg-opacity-10 rounded-lg">
              <div className="text-2xl font-bold text-amber-500">{results.violations?.filter(v => v.regulation === 'CCPA').length || 0}</div>
              <div className="text-sm text-text-secondary mt-1">CCPA</div>
            </div>
          </div>

          {/* Violations List */}
          {results.violations && results.violations.length > 0 ? (
            <div className="space-y-3">
              <h4 className="font-semibold text-text-primary mb-2">Detected Violations:</h4>
              {results.violations.map((violation, index) => {
                // Generate description from findings
                const getViolationDescription = (reg, findings) => {
                  if (reg === 'PCI-DSS') {
                    return 'Primary Account Number (PAN) exposed in plaintext';
                  } else if (reg === 'GDPR') {
                    if (findings.emails) return `Email address(es) detected: ${findings.emails.length} found`;
                    if (findings.phone_numbers) return `Phone number(s) detected: ${findings.phone_numbers.length} found`;
                    if (findings.ip_addresses) return `IP address(es) detected: ${findings.ip_addresses.length} found`;
                  } else if (reg === 'CCPA') {
                    if (findings.ssn) return `Social Security Number(s) detected: ${findings.ssn.length} found`;
                    if (findings.drivers_license) return `Driver's license number(s) detected: ${findings.drivers_license.length} found`;
                  }
                  return 'Sensitive data detected';
                };

                // Format findings for display
                const getMatchedData = (findings) => {
                  const items = [];
                  if (findings.pan) items.push(`PAN: ${findings.pan}`);
                  if (findings.emails) items.push(`Emails: ${findings.emails.join(', ')}`);
                  if (findings.phone_numbers) items.push(`Phone: ${findings.phone_numbers.join(', ')}`);
                  if (findings.ip_addresses) items.push(`IPs: ${findings.ip_addresses.join(', ')}`);
                  if (findings.ssn) items.push(`SSN: ${findings.ssn.join(', ')}`);
                  if (findings.drivers_license) items.push(`DL: ${findings.drivers_license.join(', ')}`);
                  return items.join(' | ') || 'Data detected';
                };

                return (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border-l-4 ${
                      violation.regulation === 'PCI-DSS' ? 'border-red-500 bg-red-500' :
                      violation.regulation === 'GDPR' ? 'border-purple-500 bg-purple-500' :
                      'border-amber-500 bg-amber-500'
                    } bg-opacity-10`}
                  >
                    <div className="flex items-start gap-3">
                      <AlertCircle size={20} className={
                        violation.regulation === 'PCI-DSS' ? 'text-red-500' :
                        violation.regulation === 'GDPR' ? 'text-purple-500' :
                        'text-amber-500'
                      } />
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-text-primary">{violation.regulation}</span>
                          <span className="text-xs px-2 py-1 bg-bg-main rounded text-text-secondary">
                            ID: {violation.violation_id}
                          </span>
                          <span className={`text-xs px-2 py-1 rounded font-semibold ${
                            violation.severity === 'CRITICAL' ? 'bg-red-500 text-white' :
                            violation.severity === 'HIGH' ? 'bg-orange-500 text-white' :
                            'bg-yellow-500 text-white'
                          }`}>
                            {violation.severity}
                          </span>
                        </div>
                        <p className="text-sm text-text-primary mb-2 font-medium">
                          {getViolationDescription(violation.regulation, violation.findings)}
                        </p>
                        <div className="text-xs font-mono text-text-secondary bg-bg-main p-2 rounded">
                          <strong>Detected:</strong> {getMatchedData(violation.findings)}
                        </div>
                        <div className="mt-2 text-xs text-text-secondary">
                          Regulation: {violation.regulation} | Severity: <span className="font-semibold">{violation.severity}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-6 text-center bg-green-500 bg-opacity-10 rounded-lg">
              <CheckCircle size={48} className="mx-auto mb-3 text-green-500" />
              <p className="text-lg font-semibold text-green-500">No Violations Detected</p>
              <p className="text-sm text-text-secondary mt-1">The text passed all regulatory compliance checks</p>
            </div>
          )}

          {/* Raw JSON View */}
          <details className="mt-6">
            <summary className="cursor-pointer text-text-secondary hover:text-text-primary mb-2">
              View Raw JSON Response
            </summary>
            <pre className="bg-bg-main p-4 rounded-lg overflow-x-auto text-xs text-text-primary">
              {JSON.stringify(results, null, 2)}
            </pre>
          </details>
        </motion.div>
      )}

      {/* Feature Highlights */}
      <div className="bg-bg-card rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 text-text-primary">Autonomous Capabilities</h3>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-500 bg-opacity-10 rounded-lg">
            <Shield size={24} className="text-blue-500 mb-2" />
            <h4 className="font-semibold text-text-primary mb-1">PCI-DSS Detection</h4>
            <p className="text-sm text-text-secondary">
              Detects credit card numbers with Luhn validation
            </p>
          </div>
          <div className="p-4 bg-purple-500 bg-opacity-10 rounded-lg">
            <Shield size={24} className="text-purple-500 mb-2" />
            <h4 className="font-semibold text-text-primary mb-1">GDPR Detection</h4>
            <p className="text-sm text-text-secondary">
              Identifies emails, phone numbers, and IP addresses
            </p>
          </div>
          <div className="p-4 bg-amber-500 bg-opacity-10 rounded-lg">
            <Shield size={24} className="text-amber-500 mb-2" />
            <h4 className="font-semibold text-text-primary mb-1">CCPA Detection</h4>
            <p className="text-sm text-text-secondary">
              Finds SSNs and driver's licenses for California data
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default MultiRegulationTest;
