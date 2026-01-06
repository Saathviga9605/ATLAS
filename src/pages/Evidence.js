import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Download, FileText, AlertCircle } from 'lucide-react';
import api from '../services/api';

const Evidence = () => {
  const [evidenceRecords, setEvidenceRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEvidence();
  }, []);

  const loadEvidence = async () => {
    try {
      const records = await api.getEvidence();
      setEvidenceRecords(records || []);
    } catch (error) {
      console.error('Failed to load evidence:', error);
    } finally {
      setLoading(false);
    }
  };
  const incidentTimeline = [
    {
      id: 1,
      timestamp: '2026-01-04 14:32:18',
      phase: 'Detection',
      agent: 'Monitoring Agent',
      description: 'PAN detected in support chat ticket #3847',
      evidence: 'violation-report-3847.json',
    },
    {
      id: 2,
      timestamp: '2026-01-04 14:32:20',
      phase: 'Assessment',
      agent: 'Regulation Agent',
      description: 'Violation mapped to PCI-DSS 3.2.1 Requirement 3',
      evidence: 'regulatory-mapping.pdf',
    },
    {
      id: 3,
      timestamp: '2026-01-04 14:32:25',
      phase: 'Action',
      agent: 'Remediation Agent',
      description: 'Initiated PAN masking in ticket #3847',
      evidence: 'remediation-log-001.json',
    },
    {
      id: 4,
      timestamp: '2026-01-04 14:45:12',
      phase: 'Resolution',
      agent: 'Remediation Agent',
      description: 'PAN successfully masked, historical logs redacted',
      evidence: 'completion-report.pdf',
    },
  ];

  const evidenceArtifacts = [
    {
      id: 1,
      name: 'Redacted Chat Logs',
      type: 'PDF',
      size: '234 KB',
      generated: '2026-01-04 14:45:12',
      description: 'Support chat transcript with PAN redacted',
    },
    {
      id: 2,
      name: 'Policy Diff',
      type: 'JSON',
      size: '12 KB',
      generated: '2026-01-04 14:32:25',
      description: 'Changes to data handling policy',
    },
    {
      id: 3,
      name: 'Violation Report',
      type: 'PDF',
      size: '456 KB',
      generated: '2026-01-04 14:32:20',
      description: 'Detailed violation analysis and impact assessment',
    },
    {
      id: 4,
      name: 'Audit Trail',
      type: 'JSON',
      size: '89 KB',
      generated: '2026-01-04 14:50:00',
      description: 'Complete chronological record of all actions taken',
    },
  ];

  const getPhaseColor = (phase) => {
    switch (phase) {
      case 'Detection':
        return 'bg-risk-red';
      case 'Assessment':
        return 'bg-risk-amber';
      case 'Action':
        return 'bg-accent-blue';
      case 'Resolution':
        return 'bg-risk-green';
      default:
        return 'bg-text-secondary';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="p-8 space-y-6"
    >
      <h2 className="text-2xl font-semibold text-text-primary">
        Evidence & Audit Trail
      </h2>

      {/* Incident Timeline */}
      <div className="bg-bg-card rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-6 text-text-primary">
          Incident Timeline - Ticket #3847
        </h3>

        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border-color"></div>

          <div className="space-y-6">
            {incidentTimeline.map((event, index) => (
              <motion.div
                key={event.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="relative pl-16"
              >
                {/* Timeline dot */}
                <div
                  className={`absolute left-4 top-2 w-5 h-5 rounded-full ${getPhaseColor(
                    event.phase
                  )} border-4 border-bg-card`}
                ></div>

                <div className="bg-bg-primary rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <span
                        className={`inline-block px-2 py-1 rounded text-xs font-medium text-white ${getPhaseColor(
                          event.phase
                        )}`}
                      >
                        {event.phase}
                      </span>
                    </div>
                    <span className="text-xs text-text-secondary font-mono">
                      {event.timestamp}
                    </span>
                  </div>

                  <p className="text-text-primary font-medium mb-1">
                    {event.description}
                  </p>
                  <p className="text-sm text-text-secondary mb-2">
                    Agent: {event.agent}
                  </p>

                  <div className="flex items-center gap-2 text-sm">
                    <FileText size={14} className="text-accent-blue" />
                    <span className="text-accent-blue">{event.evidence}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Evidence Artifacts */}
      <div className="bg-bg-card rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4 text-text-primary">
          Evidence Artifacts
        </h3>

        <div className="grid gap-4">
          {evidenceArtifacts.map((artifact) => (
            <motion.div
              key={artifact.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              whileHover={{ backgroundColor: 'rgba(31,42,68,0.5)' }}
              transition={{ duration: 0.2 }}
              className="flex items-center justify-between p-4 bg-bg-primary rounded-lg"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-border-color rounded flex items-center justify-center">
                  <FileText size={24} className="text-accent-blue" />
                </div>
                <div>
                  <h4 className="text-text-primary font-semibold">
                    {artifact.name}
                  </h4>
                  <p className="text-sm text-text-secondary mt-1">
                    {artifact.description}
                  </p>
                  <div className="flex gap-4 mt-2 text-xs text-text-secondary">
                    <span>{artifact.type}</span>
                    <span>•</span>
                    <span>{artifact.size}</span>
                    <span>•</span>
                    <span>{artifact.generated}</span>
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                <button className="px-4 py-2 bg-accent-blue hover:bg-opacity-90 text-white rounded transition-colors flex items-center gap-2">
                  <Download size={16} />
                  Download PDF
                </button>
                <button className="px-4 py-2 bg-border-color hover:bg-text-secondary text-text-primary rounded transition-colors">
                  View JSON
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Audit Summary */}
      <div className="bg-bg-card rounded-lg p-6 border-l-4 border-accent-blue">
        <div className="flex items-start gap-4">
          <AlertCircle size={24} className="text-accent-blue mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              Audit-Ready Documentation
            </h3>
            <p className="text-text-secondary">
              All evidence has been timestamped, cryptographically signed, and stored
              in compliance with audit requirements. Chain of custody preserved for all
              artifacts. Ready for regulatory review.
            </p>
            <div className="mt-4 grid grid-cols-3 gap-4">
              <div>
                <div className="text-2xl font-bold text-text-primary">4</div>
                <div className="text-sm text-text-secondary">Total Artifacts</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-text-primary">791 KB</div>
                <div className="text-sm text-text-secondary">Total Size</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-risk-green">100%</div>
                <div className="text-sm text-text-secondary">Compliance Coverage</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Evidence;
