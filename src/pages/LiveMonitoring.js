import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, AlertCircle } from 'lucide-react';
import api from '../services/api';

const LiveMonitoring = () => {
  const [activeTab, setActiveTab] = useState('support-chats');
  const [violations, setViolations] = useState([]);
  const [stats, setStats] = useState({
    total_violations: 0,
    by_regulation: {},
    by_severity: {}
  });
  const [selectedViolation, setSelectedViolation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  const loadViolations = async () => {
    try {
      setLoading(true);
      const [violationsData, statsData] = await Promise.all([
        api.getViolations(),
        api.getMonitoringStats()
      ]);
      
      setViolations(violationsData || []);
      setStats(statsData || stats);
      
      // Auto-select the most recent violation
      if (violationsData && violationsData.length > 0) {
        setSelectedViolation(violationsData[0]);
      }
      
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load violations:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadViolations();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(loadViolations, 10000);
    return () => clearInterval(interval);
  }, []);

  const tabs = [
    { id: 'transaction-logs', label: 'Transaction Logs', count: violations.filter(v => v.source_type === 'transaction').length },
    { id: 'support-chats', label: 'Support Chats', count: violations.filter(v => v.source_type === 'support_chat').length },
    { id: 'internal-docs', label: 'Internal Documents', count: violations.filter(v => v.source_type === 'application_log').length },
  ];

  const getFilteredViolations = () => {
    if (activeTab === 'transaction-logs') {
      return violations.filter(v => v.source_type === 'transaction');
    } else if (activeTab === 'support-chats') {
      return violations.filter(v => v.source_type === 'support_chat' || v.source_type === 'message' || v.source_type === 'email');
    } else {
      return violations.filter(v => v.source_type === 'application_log' || v.source_type === 'database');
    }
  };

  const formatTimestamp = (timestamp) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const getSeverityColor = (severity) => {
    if (severity === 'CRITICAL' || severity === 'Critical') return 'risk-red';
    if (severity === 'HIGH' || severity === 'High') return 'risk-amber';
    if (severity === 'MEDIUM' || severity === 'Medium') return 'accent-blue';
    return 'text-secondary';
  };

  const filteredViolations = getFilteredViolations();
  const displayViolation = selectedViolation || (filteredViolations.length > 0 ? filteredViolations[0] : null);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="p-8 space-y-6"
    >
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-text-primary">
          Live Monitoring
        </h2>
        <div className="flex items-center gap-3">
          {lastUpdate && (
            <span className="text-sm text-text-secondary">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={loadViolations}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-visa-blue text-white rounded-lg hover:bg-opacity-90 transition-all disabled:opacity-50"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Data Source Selector */}
      <div className="flex gap-2 border-b border-border-color">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-6 py-3 text-sm font-medium transition-colors relative ${
              activeTab === tab.id
                ? 'text-accent-blue'
                : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            {tab.label}
            {tab.count > 0 && (
              <span className="ml-2 px-2 py-0.5 bg-risk-red text-white text-xs rounded-full">
                {tab.count}
              </span>
            )}
            {activeTab === tab.id && (
              <motion.div
                layoutId="activeTab"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent-blue"
              />
            )}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Live Data Viewer */}
        <div className="col-span-2 bg-bg-card rounded-lg p-6">
          {filteredViolations.length > 0 ? (
            <>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-text-primary">
                    {displayViolation.source_type.replace('_', ' ').toUpperCase()} - {displayViolation.source_id}
                  </h3>
                  <p className="text-sm text-text-secondary mt-1">
                    {formatTimestamp(displayViolation.timestamp)}
                  </p>
                </div>
              </div>

              <div className="space-y-4 bg-bg-primary rounded p-4 max-h-96 overflow-y-auto">
                <div className="space-y-2">
                  <div className="text-xs text-text-secondary font-medium uppercase">
                    Violation Details
                  </div>
                  <div className="text-text-primary">
                    <span className="font-semibold">{displayViolation.regulation}:</span> {displayViolation.description}
                  </div>
                  <div className="mt-3 p-3 bg-risk-red bg-opacity-10 border border-risk-red rounded">
                    <div className="text-xs text-risk-red font-semibold mb-1">DETECTED ISSUE</div>
                    <div className="text-sm text-text-primary font-mono">
                      Evidence ID: {displayViolation.evidence_id}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 flex items-center gap-2 text-sm">
                <div className="w-2 h-2 bg-risk-red rounded-full animate-pulse"></div>
                <span className="text-risk-red font-medium">
                  {displayViolation.description} - Detected by Monitoring Agent
                </span>
              </div>

              {/* Violation List */}
              {filteredViolations.length > 1 && (
                <div className="mt-4 border-t border-border-color pt-4">
                  <h4 className="text-sm font-semibold text-text-secondary mb-2">
                    Recent {activeTab.replace('-', ' ')} ({filteredViolations.length})
                  </h4>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {filteredViolations.slice(0, 10).map((v, idx) => (
                      <button
                        key={idx}
                        onClick={() => setSelectedViolation(v)}
                        className={`w-full text-left p-2 rounded text-xs transition-colors ${
                          selectedViolation?.violation_id === v.violation_id
                            ? 'bg-accent-blue bg-opacity-20 border border-accent-blue'
                            : 'bg-bg-main hover:bg-border-color'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-text-primary font-mono">{v.violation_id}</span>
                          <span className={`text-${getSeverityColor(v.severity)}`}>{v.severity}</span>
                        </div>
                        <div className="text-text-secondary mt-1">{formatTimestamp(v.timestamp)}</div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <AlertCircle size={48} className="mx-auto text-text-secondary mb-3" />
              <p className="text-text-secondary">No violations detected in {activeTab.replace('-', ' ')}</p>
              <p className="text-sm text-text-secondary mt-2">
                Test the system by going to Compliance Violations Analysis page
              </p>
            </div>
          )}
        </div>

        {/* Violation Context Card (Sticky) */}
        {displayViolation && (
          <motion.div
            animate={{ boxShadow: '0 0 15px rgba(244,196,48,0.4)' }}
            className="bg-bg-card rounded-lg p-6 h-fit sticky top-8"
          >
            <h3 className="text-lg font-semibold text-risk-red mb-4">
              Active Violation
            </h3>

            <div className="space-y-4">
              <div>
                <p className="text-xs text-text-secondary uppercase mb-1">
                  Regulation Impacted
                </p>
                <p className="text-text-primary text-sm">
                  {displayViolation.regulation}
                </p>
              </div>

              <div>
                <p className="text-xs text-text-secondary uppercase mb-1">
                  Violation Description
                </p>
                <p className="text-text-primary text-sm">
                  {displayViolation.description}
                </p>
              </div>

              <div>
                <p className="text-xs text-text-secondary uppercase mb-1">
                  Severity
                </p>
                <span className={`inline-block px-3 py-1 rounded bg-${getSeverityColor(displayViolation.severity)} text-white text-sm font-medium`}>
                  {displayViolation.severity}
                </span>
              </div>

              <div>
                <p className="text-xs text-text-secondary uppercase mb-1">
                  Time Detected
                </p>
                <p className="text-text-primary text-sm font-mono">
                  {formatTimestamp(displayViolation.timestamp)}
                </p>
              </div>

              <div>
                <p className="text-xs text-text-secondary uppercase mb-1">
                  Evidence ID
                </p>
                <p className="text-text-primary text-sm font-mono">
                  {displayViolation.evidence_id}
                </p>
              </div>

              <div>
                <p className="text-xs text-text-secondary uppercase mb-1">
                  Source
                </p>
                <p className="text-text-primary text-sm">
                  {displayViolation.source_type} - {displayViolation.source_id}
                </p>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-border-color">
              <button 
                onClick={() => window.location.href = '/remediation'}
                className="w-full bg-accent-blue hover:bg-opacity-90 text-white py-2 px-4 rounded transition-colors"
              >
                View Remediation
              </button>
            </div>
          </motion.div>
        )}
      </div>

      {/* Additional monitoring stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-bg-card rounded-lg p-4">
          <div className="text-2xl font-bold text-text-primary">{stats.total_violations || 0}</div>
          <div className="text-sm text-text-secondary">Total Violations</div>
        </div>
        <div className="bg-bg-card rounded-lg p-4">
          <div className="text-2xl font-bold text-text-primary">{stats.by_regulation?.['PCI-DSS'] || 0}</div>
          <div className="text-sm text-text-secondary">PCI-DSS Violations</div>
        </div>
        <div className="bg-bg-card rounded-lg p-4">
          <div className="text-2xl font-bold text-risk-red">{stats.by_severity?.['CRITICAL'] || stats.by_severity?.['Critical'] || 0}</div>
          <div className="text-sm text-text-secondary">Critical Severity</div>
        </div>
        <div className="bg-bg-card rounded-lg p-4">
          <div className="text-2xl font-bold text-risk-amber">{stats.by_severity?.['HIGH'] || stats.by_severity?.['High'] || 0}</div>
          <div className="text-sm text-text-secondary">High Severity</div>
        </div>
      </div>
    </motion.div>
  );
};

export default LiveMonitoring;
