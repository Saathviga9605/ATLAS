import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, CheckCircle, Shield, FileText, Copy, Download } from 'lucide-react';
import api from '../services/api';

const ViolationAnalysis = () => {
  const [inputContent, setInputContent] = useState('');
  const [sourceType, setSourceType] = useState('SUPPORT_TICKET');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [allViolations, setAllViolations] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load existing violations on mount
  useEffect(() => {
    loadViolations();
  }, []);

  const loadViolations = async () => {
    try {
      const violations = await api.getViolations();
      setAllViolations(violations || []);
    } catch (error) {
      console.error('Failed to load violations:', error);
    }
  };

  // Sample test data for demonstration
  const sampleData = [
    {
      label: 'PAN in Support Ticket',
      content: 'Customer card number is 4111 1111 1111 1111',
      type: 'SUPPORT_TICKET'
    },
    {
      label: 'VISA Card Exposure',
      content: 'Payment failed for card 4532015112830366. Please retry.',
      type: 'LOG_FILE'
    },
    {
      label: 'Email with PII',
      content: 'Contact John Doe at john.doe@example.com or call 555-123-4567',
      type: 'EMAIL'
    },
    {
      label: 'Safe Content',
      content: 'Customer reported issue with payment processing system.',
      type: 'SUPPORT_TICKET'
    }
  ];

  const handleAnalyze = async () => {
    if (!inputContent.trim()) {
      alert('Please enter content to analyze');
      return;
    }

    setLoading(true);
    try {
      const result = await api.detectViolation(inputContent, sourceType);
      setAnalysisResult(result);
      
      // Reload all violations
      await loadViolations();
    } catch (error) {
      console.error('Analysis failed:', error);
      alert(`Failed to analyze: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSampleTest = async (sample) => {
    setInputContent(sample.content);
    setSourceType(sample.type);
    
    setLoading(true);
    try {
      const result = await api.detectViolation(sample.content, sample.type);
      setAnalysisResult(result);
      await loadViolations();
    } catch (error) {
      console.error('Sample test failed:', error);
      alert(`Failed to analyze: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(JSON.stringify(text, null, 2));
    alert('Copied to clipboard!');
  };

  const downloadAuditReport = async () => {
    try {
      const violations = await api.getViolations();
      const report = {
        report_id: `AUDIT_${Date.now()}`,
        generated_at: new Date().toISOString(),
        total_violations: violations.length,
        critical_count: violations.filter(v => v.severity === 'CRITICAL').length,
        high_count: violations.filter(v => v.severity === 'HIGH').length,
        violations: violations,
        compliance_status: violations.filter(v => v.severity === 'CRITICAL').length > 0 
          ? 'NON-COMPLIANT' 
          : 'AT RISK'
      };
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `compliance-audit-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download audit report:', error);
      alert(`Failed to download report: ${error.message}`);
    }
  };

  const clearHistory = () => {
    setAllViolations([]);
    setAnalysisResult(null);
  };

  const viewJSON = (data) => {
    const jsonWindow = window.open('', '_blank');
    jsonWindow.document.write('<html><head><title>JSON View</title>');
    jsonWindow.document.write('<style>body{background:#1a1a1a;color:#00ff00;font-family:monospace;padding:20px;}pre{white-space:pre-wrap;}</style>');
    jsonWindow.document.write('</head><body>');
    jsonWindow.document.write('<pre>' + JSON.stringify(data, null, 2) + '</pre>');
    jsonWindow.document.write('</body></html>');
    jsonWindow.document.close();
  };

  const downloadJSON = (data, filename) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getSeverityColor = (severity) => {
    const colors = {
      'CRITICAL': 'risk-red',
      'Critical': 'risk-red',
      'HIGH': 'risk-amber',
      'High': 'risk-amber',
      'MEDIUM': 'visa-orange',
      'Medium': 'visa-orange',
      'LOW': 'risk-green',
      'Low': 'risk-green',
      'None': 'risk-green'
    };
    return colors[severity] || 'text-gray-600';
  };

  const getSeverityBg = (severity) => {
    const colors = {
      'CRITICAL': 'bg-risk-red',
      'Critical': 'bg-risk-red',
      'HIGH': 'bg-risk-amber',
      'High': 'bg-risk-amber',
      'MEDIUM': 'bg-visa-orange',
      'Medium': 'bg-visa-orange',
      'LOW': 'bg-risk-green',
      'Low': 'bg-risk-green',
      'None': 'bg-risk-green'
    };
    return colors[severity] || 'bg-gray-200';
  };

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-visa-blue to-visa-orange bg-clip-text text-transparent">
            Cognitive Compliance Analysis
          </h1>
          <p className="text-text-secondary mt-2">
            Autonomous violation detection powered by regulation-grounded reasoning
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => viewJSON(allViolations)}
            disabled={allViolations.length === 0}
            className="flex items-center gap-2 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FileText size={18} />
            View JSON
          </button>
          <button
            onClick={downloadAuditReport}
            className="flex items-center gap-2 px-4 py-2 bg-visa-blue text-white rounded-lg hover:bg-opacity-90 transition-all"
          >
            <Download size={18} />
            Export Audit
          </button>
          <button
            onClick={clearHistory}
            className="px-4 py-2 border-2 border-visa-orange text-visa-orange rounded-lg hover:bg-visa-orange hover:text-white transition-all"
          >
            Clear History
          </button>
        </div>
      </motion.div>

      {/* Quick Test Samples */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-bg-card rounded-lg p-6 border-2 border-gray-200"
      >
        <h2 className="text-lg font-bold text-text-primary mb-4 flex items-center gap-2">
          <Shield size={20} className="text-visa-blue" />
          Quick Test Samples
        </h2>
        <div className="grid grid-cols-2 gap-3">
          {sampleData.map((sample, idx) => (
            <button
              key={idx}
              onClick={() => handleSampleTest(sample)}
              className="text-left px-4 py-3 bg-white border-2 border-gray-200 rounded-lg hover:border-visa-blue hover:shadow-md transition-all"
            >
              <div className="font-semibold text-sm text-visa-blue">{sample.label}</div>
              <div className="text-xs text-text-secondary mt-1 truncate">{sample.content}</div>
            </button>
          ))}
        </div>
      </motion.div>

      {/* Input Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-bg-card rounded-lg p-6 border-2 border-gray-200"
      >
        <h2 className="text-lg font-bold text-text-primary mb-4">Content Analysis Input</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-text-primary mb-2">
              Source Type
            </label>
            <select
              value={sourceType}
              onChange={(e) => setSourceType(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-visa-blue focus:outline-none"
            >
              <option value="SUPPORT_TICKET">Support Ticket</option>
              <option value="LOG_FILE">Log File</option>
              <option value="EMAIL">Email</option>
              <option value="DATABASE_RECORD">Database Record</option>
              <option value="API_REQUEST">API Request</option>
              <option value="CHAT_MESSAGE">Chat Message</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-text-primary mb-2">
              Content to Analyze
            </label>
            <textarea
              value={inputContent}
              onChange={(e) => setInputContent(e.target.value)}
              placeholder="Enter content that may contain sensitive data or violations..."
              className="w-full h-32 px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-visa-blue focus:outline-none resize-none font-mono text-sm"
            />
          </div>

          <button
            onClick={handleAnalyze}
            className="w-full bg-gradient-to-r from-visa-blue to-visa-orange text-white font-bold py-4 rounded-lg hover:shadow-lg transition-all"
          >
            🔍 Analyze for Compliance Violations
          </button>
        </div>
      </motion.div>

      {/* Analysis Result */}
      {analysisResult && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className={`bg-bg-card rounded-lg p-6 border-2 ${
            analysisResult.is_violation ? 'border-risk-red' : 'border-risk-green'
          }`}
        >
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              {analysisResult.is_violation ? (
                <AlertTriangle size={32} className="text-risk-red" />
              ) : (
                <CheckCircle size={32} className="text-risk-green" />
              )}
              <div>
                <h2 className="text-2xl font-bold text-text-primary">
                  {analysisResult.is_violation ? 'Violation Detected' : 'No Violation'}
                </h2>
                <p className="text-sm text-text-secondary">ID: {analysisResult.violation_id}</p>
              </div>
            </div>
            <button
              onClick={() => copyToClipboard(analysisResult)}
              className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-all"
            >
              <Copy size={16} />
              Copy JSON
            </button>
          </div>

          <div className="space-y-4">
            {/* Severity Badge */}
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-text-secondary">Risk Severity:</span>
              <span className={`px-4 py-1 ${getSeverityBg(analysisResult.risk_severity)} text-white font-bold rounded-full text-sm`}>
                {analysisResult.risk_severity}
              </span>
              <span className={`px-4 py-1 ${
                analysisResult.autonomy_level === 'AUTONOMOUS' ? 'bg-risk-green' : 'bg-risk-amber'
              } text-white font-bold rounded-full text-sm`}>
                {analysisResult.autonomy_level}
              </span>
            </div>

            {/* Explanation */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-bold text-text-primary mb-2">Explanation</h3>
              <p className="text-text-secondary text-sm leading-relaxed">
                {analysisResult.explanation}
              </p>
            </div>

            {/* Regulation Reference */}
            <div className="bg-visa-blue bg-opacity-5 p-4 rounded-lg border border-visa-blue">
              <h3 className="font-bold text-visa-blue mb-2 flex items-center gap-2">
                <FileText size={18} />
                Regulation Reference
              </h3>
              <p className="text-sm text-text-primary font-mono">
                {analysisResult.regulation_reference}
              </p>
            </div>

            {/* Recommended Action */}
            <div className="bg-visa-orange bg-opacity-5 p-4 rounded-lg border border-visa-orange">
              <h3 className="font-bold text-visa-orange mb-2">Recommended Action</h3>
              <p className="text-sm text-text-primary">
                {analysisResult.recommended_action}
              </p>
            </div>

            {/* Detected Data (if violation) */}
            {analysisResult.detected_data && (
              <div className="bg-risk-red bg-opacity-5 p-4 rounded-lg border border-risk-red">
                <h3 className="font-bold text-risk-red mb-2">Detected Sensitive Data (Masked)</h3>
                <p className="text-sm text-text-primary font-mono">
                  {analysisResult.detected_data}
                </p>
              </div>
            )}

            {/* JSON Output */}
            <div className="bg-gray-900 p-4 rounded-lg">
              <h3 className="font-bold text-white mb-2">Machine-Readable Output</h3>
              <pre className="text-xs text-green-400 overflow-x-auto">
                {JSON.stringify(analysisResult, null, 2)}
              </pre>
            </div>
          </div>
        </motion.div>
      )}

      {/* Violations History */}
      {allViolations.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-bg-card rounded-lg p-6 border-2 border-gray-200"
        >
          <h2 className="text-lg font-bold text-text-primary mb-4">
            Detection History ({allViolations.length} items)
          </h2>
          <div className="space-y-3">
            {allViolations.map((violation, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-lg border-2 ${
                  violation.severity === 'CRITICAL' || violation.severity === 'Critical' 
                    ? 'border-risk-red bg-risk-red bg-opacity-5' 
                    : 'border-risk-amber bg-risk-amber bg-opacity-5'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`px-3 py-1 ${getSeverityBg(violation.severity)} text-white text-xs font-bold rounded-full`}>
                        {violation.severity}
                      </span>
                      <span className="font-mono text-sm text-visa-blue">
                        {violation.violation_id}
                      </span>
                      <span className="text-sm text-text-secondary">
                        {violation.regulation}
                      </span>
                    </div>
                    <p className="text-sm text-text-primary mb-1">
                      {violation.description}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-text-secondary">
                      <span>Source: {violation.source_type}</span>
                      <span>Evidence: {violation.evidence_id}</span>
                      <span>{new Date(violation.timestamp).toLocaleString()}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => downloadJSON(violation, `${violation.violation_id}.json`)}
                    className="ml-4 p-2 text-visa-blue hover:bg-visa-blue hover:text-white rounded transition-all"
                    title="Download JSON"
                  >
                    <Download size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default ViolationAnalysis;
