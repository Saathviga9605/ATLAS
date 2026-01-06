import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, CheckCircle, XCircle, Brain, Download, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const ComplianceOverview = () => {
  const navigate = useNavigate();
  const [liveViolations, setLiveViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [backendConnected, setBackendConnected] = useState(false);
  const [stats, setStats] = useState({
    total_violations: 0,
    by_regulation: {},
    by_severity: {}
  });
  const [recentActivity, setRecentActivity] = useState([]);
  
  // Fetch violations from backend
  useEffect(() => {
    async function loadViolations() {
      try {
        // Check backend health
        const health = await api.checkHealth();
        setBackendConnected(health.status === 'healthy');
        
        // Fetch existing violations from backend
        const violations = await api.getViolations();
        setLiveViolations(violations || []);
        
        // Generate recent activity from actual violations
        if (violations && violations.length > 0) {
          const activities = violations
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
            .slice(0, 6)
            .map((v, idx) => {
              const time = new Date(v.timestamp);
              const timeStr = time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
              
              if (v.violation_id.startsWith('COMP-')) {
                return {
                  time: timeStr,
                  agent: 'Monitoring Agent',
                  action: `scanned ${v.source_type.replace('_', ' ')} - no violations detected`,
                  type: 'compliant'
                };
              } else {
                return {
                  time: timeStr,
                  agent: 'Cognitive Compliance Agent',
                  action: `detected ${v.regulation} violation in ${v.source_type.replace('_', ' ')}`,
                  type: 'violation',
                  severity: v.severity
                };
              }
            });
          setRecentActivity(activities);
        }
        
        // Fetch statistics
        try {
          const statsData = await api.getMonitoringStats();
          setStats(statsData);
        } catch (statsError) {
          console.warn('Stats not available:', statsError);
        }
        
        // If no violations exist, create some demo data
        if (!violations || violations.length === 0) {
          try {
            await api.detectViolation('Customer card number is 4111 1111 1111 1111', 'support_chat', 'demo_001');
            await api.detectViolation('Payment failed for card 4532015112830366', 'application_log', 'demo_002');
            
            // Refetch violations
            const newViolations = await api.getViolations();
            setLiveViolations(newViolations || []);
          } catch (demoError) {
            console.warn('Demo violation creation failed:', demoError);
          }
        }
      } catch (error) {
        console.error('Failed to connect to backend:', error);
        setBackendConnected(false);
      } finally {
        setLoading(false);
      }
    }
    
    loadViolations();
    
    // Poll for new violations every 5 seconds
    const interval = setInterval(async () => {
      try {
        const violations = await api.getViolations();
        setLiveViolations(violations || []);
        
        const statsData = await api.getMonitoringStats();
        setStats(statsData);
        
        // Update recent activity
        if (violations && violations.length > 0) {
          const activities = violations
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
            .slice(0, 6)
            .map((v, idx) => {
              const time = new Date(v.timestamp);
              const timeStr = time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
              
              if (v.violation_id.startsWith('COMP-')) {
                return {
                  time: timeStr,
                  agent: 'Monitoring Agent',
                  action: `scanned ${v.source_type.replace('_', ' ')} - no violations detected`,
                  type: 'compliant'
                };
              } else {
                return {
                  time: timeStr,
                  agent: 'Cognitive Compliance Agent',
                  action: `detected ${v.regulation} violation in ${v.source_type.replace('_', ' ')}`,
                  type: 'violation',
                  severity: v.severity
                };
              }
            });
          setRecentActivity(activities);
        }
      } catch (error) {
        console.error('Failed to fetch violations:', error);
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Global compliance status
  const complianceStatus = liveViolations.filter(v => v.severity === 'CRITICAL').length > 0 
    ? 'NON-COMPLIANT' 
    : liveViolations.length > 0 
      ? 'AT RISK' 
      : 'COMPLIANT';
  
  // Regulatory heatmap data
  const regulatoryData = [
    { regulation: 'PCI-DSS', data: 'amber', policies: 'green', operations: 'red', overall: 'amber' },
    { regulation: 'GDPR', data: 'green', policies: 'green', operations: 'amber', overall: 'green' },
    { regulation: 'CCPA', data: 'green', policies: 'amber', operations: 'green', overall: 'green' },
    { regulation: 'SOX', data: 'amber', policies: 'green', operations: 'green', overall: 'amber' },
  ];

  // Active risks - now using live violations from backend
  const activeRisks = liveViolations.length > 0 
    ? liveViolations
        .filter(v => !v.violation_id.startsWith('COMP-')) // Exclude compliant records
        .slice(0, 10) // Show top 10 most recent violations
        .map((v, idx) => ({
          id: idx + 1,
          severity: v.severity === 'Critical' ? 'red' : v.severity === 'High' ? 'amber' : 'green',
          title: v.description || 'Compliance violation detected',
          description: `${v.regulation} violation detected in ${v.source_type.replace('_', ' ')}`,
          violationId: v.violation_id,
          timestamp: new Date(v.timestamp).toLocaleString()
        }))
    : [
        {
          id: 1,
          severity: 'green',
          title: backendConnected ? 'No active violations detected' : 'Backend disconnected',
          description: backendConnected ? 'All systems operating normally' : 'Unable to connect to backend API',
        },
      ];

  // Agent activity feed - enhanced with compliance agent
  const agentActivity = recentActivity.length > 0 
    ? recentActivity
    : [
        { time: new Date().toLocaleTimeString().substring(0, 5), agent: 'System', action: 'Waiting for data to scan...', type: 'info' }
      ];

  const getStatusColor = () => {
    if (complianceStatus === 'COMPLIANT') return 'risk-green';
    if (complianceStatus === 'AT RISK') return 'risk-amber';
    return 'risk-red';
  };

  const getStatusIcon = () => {
    if (complianceStatus === 'COMPLIANT') return <CheckCircle size={48} />;
    if (complianceStatus === 'AT RISK') return <AlertTriangle size={48} />;
    return <XCircle size={48} />;
  };

  const getDotColor = (status) => {
    if (status === 'green') return 'bg-risk-green';
    if (status === 'amber') return 'bg-risk-amber';
    return 'bg-risk-red';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="p-8 space-y-8"
    >
      {/* Backend Connection Status */}
      {!backendConnected && !loading && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-risk-red/10 border border-risk-red rounded-lg p-4"
        >
          <div className="flex items-center gap-3">
            <XCircle className="text-risk-red" size={24} />
            <div>
              <h4 className="font-semibold text-risk-red">Backend API Disconnected</h4>
              <p className="text-sm text-text-secondary">
                Unable to connect to http://localhost:8000. Make sure the backend is running.
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Global Compliance Status */}
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ 
          scale: 1, 
          opacity: 1,
          boxShadow: complianceStatus === 'NON-COMPLIANT' 
            ? '0 0 20px rgba(229,72,77,0.4)' 
            : '0 0 0px rgba(0,0,0,0)'
        }}
        transition={{ duration: 0.4 }}
        className={`bg-bg-card rounded-lg p-8 border-2 border-${getStatusColor()}`}
      >
        <div className="flex items-center gap-6">
          <div className={`text-${getStatusColor()}`}>
            {getStatusIcon()}
          </div>
          <div className="flex-1">
            <h2 className={`text-4xl font-bold text-${getStatusColor()} mb-2`}>
              {complianceStatus}
            </h2>
            <p className="text-text-secondary text-lg mb-4">
              Continuous PCI & PII compliance evaluated autonomously
            </p>
            <div className="grid grid-cols-3 gap-4 mt-4">
              <div className="bg-border-color rounded-lg p-3">
                <div className="text-2xl font-bold text-text-primary">{stats.total_violations || 0}</div>
                <div className="text-xs text-text-secondary">Total Violations</div>
              </div>
              <div className="bg-border-color rounded-lg p-3">
                <div className="text-2xl font-bold text-text-primary">
                  {Object.keys(stats.by_regulation || {}).length}
                </div>
                <div className="text-xs text-text-secondary">Regulations Affected</div>
              </div>
              <div className="bg-border-color rounded-lg p-3">
                <div className="text-2xl font-bold text-text-primary">
                  {stats.by_severity?.Critical || 0}
                </div>
                <div className="text-xs text-text-secondary">Critical Severity</div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Regulatory Risk Heatmap */}
      <div className="bg-bg-card rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4 text-text-primary">
          Multi-Regulation Risk Heatmap
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border-color">
                <th className="text-left py-3 px-4 text-text-secondary font-medium">Regulation</th>
                <th className="text-left py-3 px-4 text-text-secondary font-medium">Violations</th>
                <th className="text-left py-3 px-4 text-text-secondary font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-border-color hover:bg-border-color transition-colors">
                <td className="py-4 px-4 text-text-primary font-medium">PCI-DSS</td>
                <td className="py-4 px-4 text-text-primary">{stats.by_regulation['PCI-DSS'] || 0}</td>
                <td className="py-4 px-4">
                  <div className={`w-3 h-3 rounded-full ${getDotColor(stats.by_regulation['PCI-DSS'] > 0 ? 'red' : 'green')}`}></div>
                </td>
              </tr>
              <tr className="border-b border-border-color hover:bg-border-color transition-colors">
                <td className="py-4 px-4 text-text-primary font-medium">GDPR</td>
                <td className="py-4 px-4 text-text-primary">{stats.by_regulation['GDPR'] || 0}</td>
                <td className="py-4 px-4">
                  <div className={`w-3 h-3 rounded-full ${getDotColor(stats.by_regulation['GDPR'] > 0 ? 'amber' : 'green')}`}></div>
                </td>
              </tr>
              <tr className="border-b border-border-color hover:bg-border-color transition-colors">
                <td className="py-4 px-4 text-text-primary font-medium">CCPA</td>
                <td className="py-4 px-4 text-text-primary">{stats.by_regulation['CCPA'] || 0}</td>
                <td className="py-4 px-4">
                  <div className={`w-3 h-3 rounded-full ${getDotColor(stats.by_regulation['CCPA'] > 0 ? 'amber' : 'green')}`}></div>
                </td>
              </tr>
              <tr className="hover:bg-border-color transition-colors">
                <td className="py-4 px-4 text-text-primary font-medium">SOX</td>
                <td className="py-4 px-4 text-text-primary">0</td>
                <td className="py-4 px-4">
                  <div className={`w-3 h-3 rounded-full ${getDotColor('green')}`}></div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="mt-4 p-3 bg-visa-blue bg-opacity-5 rounded-lg">
          <p className="text-sm text-text-secondary">
            <strong className="text-visa-blue">Multi-Regulation Monitoring Active:</strong> System autonomously scans for PCI-DSS, GDPR, and CCPA violations in real-time
          </p>
        </div>
      </div>

      {/* Violation Severity Distribution */}
      <div className="bg-bg-card rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4 text-text-primary">
          Violation Severity Distribution
        </h3>
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 bg-red-500 bg-opacity-10 rounded-lg">
            <div className="text-3xl font-bold text-red-500">{stats.by_severity?.Critical || 0}</div>
            <div className="text-sm text-text-secondary mt-1">Critical</div>
          </div>
          <div className="text-center p-4 bg-amber-500 bg-opacity-10 rounded-lg">
            <div className="text-3xl font-bold text-amber-500">{stats.by_severity?.High || 0}</div>
            <div className="text-sm text-text-secondary mt-1">High</div>
          </div>
          <div className="text-center p-4 bg-blue-500 bg-opacity-10 rounded-lg">
            <div className="text-3xl font-bold text-blue-500">{stats.by_severity?.Medium || 0}</div>
            <div className="text-sm text-text-secondary mt-1">Medium</div>
          </div>
        </div>
        <div className="p-3 bg-amber-500 bg-opacity-5 rounded-lg">
          <p className="text-sm text-text-secondary">
            <strong className="text-amber-500">Risk Assessment:</strong> {
              stats.by_severity?.Critical > 0 
                ? `${stats.by_severity.Critical} critical violations require immediate attention` 
                : stats.total_violations > 0
                  ? `${stats.total_violations} total violations detected - review recommended`
                  : 'No critical violations detected - system compliant'
            }
          </p>
        </div>
      </div>

      {/* Key Active Risks */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-semibold text-text-primary">
              Recent Violations
            </h3>
            <p className="text-sm text-text-secondary mt-1">
              {activeRisks.filter(r => r.violationId).length > 0 
                ? `Showing ${activeRisks.filter(r => r.violationId).length} most recent violations. Click to analyze with AI.`
                : 'No violations detected. System is monitoring continuously.'}
            </p>
          </div>
          {activeRisks.filter(r => r.violationId).length > 0 && (
            <button
              onClick={() => navigate('/violation-analysis')}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-visa-blue to-visa-orange text-white rounded-lg hover:shadow-lg transition-all"
            >
              <Brain size={18} />
              AI Analysis Tool
            </button>
          )}
        </div>
        <div className="grid gap-4">
          {activeRisks.map((risk, index) => (
            <motion.div
              key={risk.id}
              initial={{ x: 30, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: index * 0.05, duration: 0.3 }}
              className={`bg-bg-card rounded-lg p-6 border-l-4 border-${
                risk.severity === 'red' ? 'risk-red' :
                risk.severity === 'amber' ? 'risk-amber' :
                'risk-green'
              } ${risk.violationId ? 'cursor-pointer hover:bg-border-color' : ''} transition-colors`}
              onClick={() => risk.violationId && navigate('/violation-analysis')}
            >
              <div className="flex items-start gap-4">
                <div className={`w-3 h-3 rounded-full mt-1 ${getDotColor(risk.severity)}`}></div>
                <div className="flex-1">
                  <h4 className="text-lg font-semibold text-text-primary mb-1">
                    {risk.title}
                  </h4>
                  <p className="text-text-secondary text-sm mb-2">
                    {risk.description}
                  </p>
                  <div className="flex items-center gap-4 text-xs">
                    {risk.violationId && (
                      <span className="text-visa-blue font-mono">
                        {risk.violationId}
                      </span>
                    )}
                    {risk.timestamp && (
                      <span className="text-text-secondary">
                        Detected: {risk.timestamp}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Autonomous Agent Feed */}
      <div className="bg-bg-card rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-semibold text-text-primary">
              Real-Time Agent Activity
            </h3>
            <p className="text-sm text-text-secondary mt-1">
              Live feed of autonomous compliance monitoring actions
            </p>
          </div>
          {agentActivity.length > 1 && (
            <div className="flex items-center gap-2 px-3 py-1 bg-green-500 bg-opacity-10 rounded-full">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-green-500 font-medium">LIVE</span>
            </div>
          )}
        </div>
        <div className="space-y-3">
          {agentActivity.map((activity, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25, delay: index * 0.05 }}
              className="flex gap-4 items-start p-3 rounded hover:bg-border-color transition-colors"
            >
              <div className="text-text-secondary text-sm font-mono min-w-[45px]">
                {activity.time}
              </div>
              <div className={`w-2 h-2 rounded-full mt-1.5 ${
                activity.type === 'violation' && activity.severity === 'Critical' ? 'bg-risk-red' :
                activity.type === 'violation' ? 'bg-risk-amber' :
                activity.type === 'compliant' ? 'bg-risk-green' :
                'bg-accent-blue'
              }`}></div>
              <div className="flex-1">
                <span className={`font-medium ${
                  activity.type === 'violation' ? 'text-risk-amber' : 'text-accent-blue'
                }`}>
                  {activity.agent}
                </span>
                <span className="text-text-secondary"> {activity.action}</span>
              </div>
            </motion.div>
          ))}
        </div>
        {agentActivity.length === 1 && agentActivity[0].type === 'info' && (
          <div className="mt-4 p-3 bg-blue-500 bg-opacity-5 rounded-lg">
            <p className="text-sm text-text-secondary">
              <strong className="text-blue-500">Tip:</strong> Use the Multi-Regulation Scanner or other pages to generate compliance data. The system will automatically detect violations and display activity here.
            </p>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ComplianceOverview;
