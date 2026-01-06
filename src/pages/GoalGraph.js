import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, RefreshCw } from 'lucide-react';
import api from '../services/api';

const GoalGraph = () => {
  const [selectedNode, setSelectedNode] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  const loadGoalData = async () => {
    try {
      setLoading(true);
      const [violations, stats] = await Promise.all([
        api.getViolations(),
        api.getMonitoringStats()
      ]);

      // Build dynamic goal graph
      const newNodes = [];
      let nodeId = 1;

      // Track regulations with violations
      const regulationMap = {};
      
      // Add regulation nodes and violation nodes
      violations.forEach((violation, idx) => {
        const regulation = violation.regulation;
        
        // Add regulation node if not already added
        if (!regulationMap[regulation]) {
          const hasViolations = violations.filter(v => v.regulation === regulation && v.severity !== 'None').length > 0;
          regulationMap[regulation] = {
            id: nodeId++,
            type: 'regulatory',
            label: regulation,
            x: 20,
            y: 20 + (Object.keys(regulationMap).length * 35),
            description: `${regulation} compliance framework`,
            clause: getRegulationClause(regulation),
            status: hasViolations ? 'at-risk' : 'satisfied',
            violationCount: violations.filter(v => v.regulation === regulation && v.severity !== 'None').length
          };
          newNodes.push(regulationMap[regulation]);
        }

        // Add violation node if it's an actual violation
        if (violation.severity !== 'None') {
          const violationNode = {
            id: nodeId++,
            type: 'violation',
            label: violation.description.substring(0, 30) + '...',
            x: 50,
            y: 20 + (idx * 25),
            description: violation.description,
            regulation: violation.regulation,
            status: 'violated',
            severity: violation.severity,
            evidenceId: violation.evidence_id,
            violationId: violation.violation_id,
            timestamp: violation.timestamp
          };
          newNodes.push(violationNode);
        }
      });

      // Add control nodes (complementary to regulations)
      Object.keys(regulationMap).forEach((regulation, idx) => {
        const controlNode = {
          id: nodeId++,
          type: 'control',
          label: getControlName(regulation),
          x: 80,
          y: 20 + (idx * 35),
          description: getControlDescription(regulation),
          linkedPolicies: getLinkedPolicies(regulation),
          status: regulationMap[regulation].status === 'at-risk' ? 'at-risk' : 'satisfied'
        };
        newNodes.push(controlNode);
      });

      // If no violations, add default compliant state
      if (violations.length === 0) {
        newNodes.push({
          id: 1,
          type: 'regulatory',
          label: 'All Regulations',
          x: 30,
          y: 40,
          description: 'No violations detected - all regulations compliant',
          clause: 'Multi-regulation compliance monitoring active',
          status: 'satisfied',
          violationCount: 0
        });
        newNodes.push({
          id: 2,
          type: 'control',
          label: 'System Monitoring',
          x: 70,
          y: 40,
          description: 'Continuous monitoring across PCI-DSS, GDPR, and CCPA',
          linkedPolicies: ['Compliance Monitoring Policy'],
          status: 'satisfied'
        });
      }

      setNodes(newNodes);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load goal data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGoalData();
    
    // Auto-refresh every 15 seconds
    const interval = setInterval(loadGoalData, 15000);
    return () => clearInterval(interval);
  }, []);

  // Helper functions
  const getRegulationClause = (regulation) => {
    const clauses = {
      'PCI-DSS': 'Requirement 3: Protect stored cardholder data',
      'GDPR': 'Article 32: Security of processing',
      'CCPA': 'Section 1798.100: Consumer privacy rights',
      'Multi-Regulation Scan': 'Comprehensive compliance monitoring'
    };
    return clauses[regulation] || `${regulation} compliance requirements`;
  };

  const getControlName = (regulation) => {
    const controls = {
      'PCI-DSS': 'Data Encryption',
      'GDPR': 'Data Protection',
      'CCPA': 'Privacy Controls',
      'Multi-Regulation Scan': 'System Monitoring'
    };
    return controls[regulation] || 'Compliance Control';
  };

  const getControlDescription = (regulation) => {
    const descriptions = {
      'PCI-DSS': 'Encrypt all cardholder data and restrict PAN exposure',
      'GDPR': 'Protect personal data and ensure privacy compliance',
      'CCPA': 'Safeguard consumer personal information',
      'Multi-Regulation Scan': 'Continuous monitoring and violation detection'
    };
    return descriptions[regulation] || 'Compliance control implementation';
  };

  const getLinkedPolicies = (regulation) => {
    const policies = {
      'PCI-DSS': ['Data Security Policy v2.1', 'PAN Protection Policy v1.0'],
      'GDPR': ['Data Protection Policy v3.0', 'Privacy Policy v2.5'],
      'CCPA': ['Consumer Privacy Policy v1.2', 'Data Rights Policy v1.0'],
      'Multi-Regulation Scan': ['Compliance Monitoring Policy']
    };
    return policies[regulation] || ['Compliance Policy'];
  };

  // Goal status summary
  const goalsSatisfied = nodes.filter(n => n.status === 'satisfied').length;
  const goalsAtRisk = nodes.filter(n => n.status === 'at-risk').length;
  const goalsViolated = nodes.filter(n => n.status === 'violated').length;

  const getNodeColor = (type, status) => {
    if (status === 'violated') return 'bg-risk-red';
    if (status === 'at-risk') return 'bg-risk-amber';
    if (type === 'regulatory') return 'bg-accent-blue';
    if (type === 'control') return 'bg-risk-green';
    return 'bg-text-secondary';
  };

  const getNodeBorderColor = (type, status) => {
    if (status === 'violated') return 'border-risk-red';
    if (status === 'at-risk') return 'border-risk-amber';
    if (type === 'regulatory') return 'border-accent-blue';
    if (type === 'control') return 'border-risk-green';
    return 'border-text-secondary';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="p-8 h-screen overflow-hidden"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-text-primary">
          Compliance Goal Graph
        </h2>
        <div className="flex items-center gap-3">
          {lastUpdate && (
            <span className="text-sm text-text-secondary">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={loadGoalData}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-visa-blue text-white rounded-lg hover:bg-opacity-90 transition-all disabled:opacity-50"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      <div className="flex gap-6 h-[calc(100%-8rem)]">
        {/* Graph Canvas */}
        <div className="flex-1 bg-bg-card rounded-lg p-6 relative overflow-hidden">
          {nodes.length > 0 ? (
            <div className="relative w-full h-full">
              {/* SVG for connections - dynamically generated */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none">
                {nodes.map((node, idx) => {
                  if (node.type === 'regulatory') {
                    // Connect regulation to violations and controls
                    return nodes
                      .filter(n => n.type === 'violation' && n.regulation === node.label)
                      .map((targetNode, i) => (
                        <line
                          key={`${node.id}-${targetNode.id}`}
                          x1={`${node.x}%`}
                          y1={`${node.y}%`}
                          x2={`${targetNode.x}%`}
                          y2={`${targetNode.y}%`}
                          stroke="var(--risk-red)"
                          strokeWidth="2"
                          strokeDasharray="5,5"
                        />
                      ));
                  }
                  return null;
                })}
                {/* Connect regulations to controls */}
                {nodes.filter(n => n.type === 'regulatory').map((regNode, idx) => {
                  const controlNode = nodes.filter(n => n.type === 'control')[idx];
                  if (controlNode) {
                    return (
                      <line
                        key={`reg-${regNode.id}-ctrl-${controlNode.id}`}
                        x1={`${regNode.x}%`}
                        y1={`${regNode.y}%`}
                        x2={`${controlNode.x}%`}
                        y2={`${controlNode.y}%`}
                        stroke={regNode.status === 'at-risk' ? 'var(--risk-amber)' : 'var(--risk-green)'}
                        strokeWidth="2"
                      />
                    );
                  }
                  return null;
                })}
              </svg>

              {/* Nodes */}
              {nodes.map((node) => (
                <motion.div
                  key={node.id}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ 
                    scale: 1, 
                    opacity: 1,
                    boxShadow: node.status === 'violated' 
                      ? [
                          '0 0 0px rgba(229,72,77,0)',
                          '0 0 18px rgba(229,72,77,0.6)',
                          '0 0 0px rgba(229,72,77,0)'
                        ]
                      : '0 0 0px rgba(0,0,0,0)'
                  }}
                  transition={{ 
                    scale: { duration: 0.3, delay: node.id * 0.05 },
                    boxShadow: node.status === 'violated' 
                      ? { repeat: Infinity, duration: 2 }
                      : { duration: 0 }
                  }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setSelectedNode(node)}
                  className={`absolute cursor-pointer ${getNodeColor(node.type, node.status)} 
                    border-2 ${getNodeBorderColor(node.type, node.status)} 
                    rounded-lg px-4 py-3 shadow-lg`}
                  style={{ left: `${node.x}%`, top: `${node.y}%` }}
                >
                  <div className="text-sm font-semibold text-white whitespace-nowrap">
                    {node.label}
                  </div>
                  <div className="text-xs text-white opacity-80 mt-1">
                    {node.type === 'regulatory' ? '📋 Regulation' : 
                     node.type === 'control' ? '🔒 Control' : 
                     '🔴 Violation'}
                  </div>
                  {node.violationCount > 0 && (
                    <div className="text-xs text-white font-bold mt-1">
                      {node.violationCount} violation{node.violationCount > 1 ? 's' : ''}
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-text-secondary">
              {loading ? 'Loading goal graph...' : 'No compliance data available'}
            </div>
          )}
        </div>

        {/* Node Details Panel */}
        <AnimatePresence>
          {selectedNode && (
            <motion.aside
              initial={{ x: 40, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 40, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="w-96 bg-bg-card rounded-lg p-6 overflow-y-auto"
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-semibold text-text-primary">
                  {selectedNode.label}
                </h3>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-text-secondary hover:text-text-primary transition-colors"
                >
                  <X size={20} />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <p className="text-xs text-text-secondary uppercase mb-1">Description</p>
                  <p className="text-text-primary">{selectedNode.description}</p>
                </div>

                {selectedNode.clause && (
                  <div>
                    <p className="text-xs text-text-secondary uppercase mb-1">Source Regulation</p>
                    <p className="text-text-primary">{selectedNode.clause}</p>
                  </div>
                )}

                {selectedNode.linkedPolicies && (
                  <div>
                    <p className="text-xs text-text-secondary uppercase mb-1">Linked Policies</p>
                    <ul className="space-y-1">
                      {selectedNode.linkedPolicies.map((policy, idx) => (
                        <li key={idx} className="text-accent-blue text-sm">• {policy}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {selectedNode.regulation && (
                  <div>
                    <p className="text-xs text-text-secondary uppercase mb-1">Regulation Impacted</p>
                    <p className="text-text-primary">{selectedNode.regulation}</p>
                  </div>
                )}

                <div>
                  <p className="text-xs text-text-secondary uppercase mb-1">Current Status</p>
                  <span className={`inline-block px-3 py-1 rounded text-sm font-medium ${
                    selectedNode.status === 'satisfied' ? 'bg-risk-green text-white' :
                    selectedNode.status === 'at-risk' ? 'bg-risk-amber text-white' :
                    'bg-risk-red text-white'
                  }`}>
                    {selectedNode.status.toUpperCase().replace('-', ' ')}
                  </span>
                </div>

                <div>
                  <p className="text-xs text-text-secondary uppercase mb-1">Last Updated</p>
                  <p className="text-text-primary text-sm">
                    {selectedNode.timestamp ? new Date(selectedNode.timestamp).toLocaleString() : 
                     selectedNode.status === 'violated' ? 'Monitoring Agent detected' : 
                     selectedNode.type === 'regulatory' ? 'Regulation Agent monitored' :
                     'Policy Agent verified'}
                  </p>
                </div>

                {selectedNode.violationId && (
                  <div>
                    <p className="text-xs text-text-secondary uppercase mb-1">Violation ID</p>
                    <p className="text-text-primary text-sm font-mono">{selectedNode.violationId}</p>
                  </div>
                )}

                {selectedNode.evidenceId && (
                  <div>
                    <p className="text-xs text-text-secondary uppercase mb-1">Evidence ID</p>
                    <p className="text-text-primary text-sm font-mono">{selectedNode.evidenceId}</p>
                  </div>
                )}

                {selectedNode.severity && (
                  <div>
                    <p className="text-xs text-text-secondary uppercase mb-1">Severity Level</p>
                    <span className={`inline-block px-3 py-1 rounded text-sm font-medium ${
                      selectedNode.severity === 'CRITICAL' ? 'bg-risk-red text-white' :
                      selectedNode.severity === 'HIGH' ? 'bg-risk-amber text-white' :
                      'bg-accent-blue text-white'
                    }`}>
                      {selectedNode.severity}
                    </span>
                  </div>
                )}
              </div>
            </motion.aside>
          )}
        </AnimatePresence>
      </div>

      {/* Goal Status Summary */}
      <div className="fixed bottom-8 left-80 right-8 flex gap-4">
        <div className="bg-bg-card rounded-lg px-6 py-4 border-l-4 border-risk-green shadow-lg">
          <div className="text-2xl font-bold text-text-primary">{goalsSatisfied}</div>
          <div className="text-sm text-text-secondary">Goals Satisfied</div>
        </div>
        <div className="bg-bg-card rounded-lg px-6 py-4 border-l-4 border-risk-amber shadow-lg">
          <div className="text-2xl font-bold text-text-primary">{goalsAtRisk}</div>
          <div className="text-sm text-text-secondary">Goals At Risk</div>
        </div>
        <div className="bg-bg-card rounded-lg px-6 py-4 border-l-4 border-risk-red shadow-lg">
          <div className="text-2xl font-bold text-text-primary">{goalsViolated}</div>
          <div className="text-sm text-text-secondary">Goals Violated</div>
        </div>
      </div>
    </motion.div>
  );
};

export default GoalGraph;
