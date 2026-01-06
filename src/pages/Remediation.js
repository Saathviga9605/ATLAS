import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, Clock, Play, AlertCircle, Sparkles } from 'lucide-react';
import api from '../services/api';

const Remediation = () => {
  const [violations, setViolations] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total_violations: 0,
    by_regulation: {},
    by_severity: {}
  });
  const [recommendation, setRecommendation] = useState({
    title: 'AI-Generated Remediation Plan',
    content: '',
    steps: []
  });

  useEffect(() => {
    loadRemediationData();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(loadRemediationData, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadRemediationData = async () => {
    try {
      // Fetch violations
      const violationsData = await api.getViolations();
      const activeViolations = violationsData.filter(v => !v.violation_id.startsWith('COMP-'));
      setViolations(activeViolations);
      
      // Fetch stats
      const statsData = await api.getMonitoringStats();
      setStats(statsData);
      
      // Generate dynamic remediation tasks from violations
      const generatedTasks = generateTasksFromViolations(activeViolations);
      setTasks(generatedTasks);
      
      // Generate dynamic recommendation
      const generatedRec = generateRecommendation(activeViolations, statsData);
      setRecommendation(generatedRec);
      
      setLoading(false);
    } catch (error) {
      console.error('Failed to load remediation data:', error);
      setLoading(false);
    }
  };

  const generateTasksFromViolations = (violations) => {
    if (!violations || violations.length === 0) return [];
    
    const tasks = [];
    const regulationGroups = {};
    
    // Group violations by regulation
    violations.forEach(v => {
      if (!regulationGroups[v.regulation]) {
        regulationGroups[v.regulation] = [];
      }
      regulationGroups[v.regulation].push(v);
    });
    
    // Create tasks for each regulation group
    Object.keys(regulationGroups).forEach((regulation, idx) => {
      const violationList = regulationGroups[regulation];
      const count = violationList.length;
      
      // Determine task status based on violation count and age
      let status = 'planned';
      let progress = 0;
      
      if (count < 5) {
        status = 'completed';
        progress = 100;
      } else if (count < 15) {
        status = 'executing';
        progress = Math.max(15, 100 - (count * 3));
      } else {
        status = 'planned';
        progress = 0;
      }
      
      const actionType = regulation === 'PCI-DSS' ? 'Mask PAN' :
                        regulation === 'GDPR' ? 'Redact PII' :
                        regulation === 'CCPA' ? 'Anonymize Personal Data' :
                        'Remediate';
      
      const goal = regulation === 'PCI-DSS' ? 'Protect stored cardholder data' :
                   regulation === 'GDPR' ? 'Ensure GDPR compliance' :
                   regulation === 'CCPA' ? 'Protect consumer privacy' :
                   'Maintain compliance';
      
      tasks.push({
        id: idx + 1,
        title: `${actionType} in ${violationList[0]?.source_type?.replace('_', ' ') || 'system'} (${count} violations)`,
        agent: 'Remediation Agent',
        status: status,
        goal: goal,
        progress: progress,
        regulation: regulation,
        violationCount: count,
        violationIds: violationList.slice(0, 3).map(v => v.violation_id)
      });
    });
    
    // Add audit evidence task if there are violations
    if (violations.length > 0) {
      tasks.push({
        id: tasks.length + 1,
        title: `Generate Audit Evidence for ${violations.length} violations`,
        agent: 'Evidence Agent',
        status: violations.length > 20 ? 'executing' : 'completed',
        goal: 'Document compliance actions',
        progress: violations.length > 20 ? 60 : 100,
        regulation: 'Multi-Regulation',
        violationCount: violations.length,
        violationIds: []
      });
    }
    
    // Add policy update task for high violation counts
    if (violations.length > 30) {
      tasks.push({
        id: tasks.length + 1,
        title: 'Update Data Handling Policies',
        agent: 'Policy Agent',
        status: 'planned',
        goal: 'Prevent future violations',
        progress: 0,
        regulation: 'Governance',
        violationCount: 0,
        violationIds: []
      });
    }
    
    return tasks;
  };

  const generateRecommendation = (violations, stats) => {
    if (!violations || violations.length === 0) {
      return {
        title: 'AI-Generated Remediation Plan',
        content: 'No active violations detected. System is compliant. Continue monitoring for new violations.',
        steps: ['Continue real-time monitoring', 'Review compliance policies quarterly', 'Train staff on data handling best practices']
      };
    }
    
    const regulations = Object.keys(stats.by_regulation || {});
    const totalViolations = stats.total_violations || 0;
    const criticalCount = stats.by_severity?.Critical || 0;
    
    // Generate dynamic content based on violations
    let content = `Based on analysis of ${totalViolations} violations across ${regulations.join(', ')}: `;
    
    if (regulations.includes('PCI-DSS')) {
      content += 'Implement automated PAN masking at data ingestion points. ';
    }
    if (regulations.includes('GDPR')) {
      content += 'Deploy PII redaction rules for EU data subjects. ';
    }
    if (regulations.includes('CCPA')) {
      content += 'Enable consumer data anonymization for California residents. ';
    }
    
    content += `${criticalCount > 0 ? `${criticalCount} critical violations require immediate attention. ` : ''}Establish automated detection and remediation workflows to prevent future violations.`;
    
    const steps = [];
    
    if (criticalCount > 0) {
      steps.push(`Address ${criticalCount} critical violations immediately`);
    }
    
    if (regulations.includes('PCI-DSS')) {
      steps.push('Deploy automated PAN masking rules');
      steps.push('Redact historical logs containing unmasked PANs');
    }
    
    if (violations.length > 20) {
      steps.push(`Schedule bulk remediation for ${violations.length} violations (estimated ${Math.ceil(violations.length / 10)} hours)`);
    }
    
    steps.push('Update staff training materials');
    steps.push('Enable continuous compliance monitoring');
    
    return {
      title: 'AI-Generated Remediation Plan',
      content,
      steps
    };
  };

  const getStatusIcon = (status) => {
    if (status === 'completed') return <CheckCircle size={20} className="text-risk-green" />;
    if (status === 'executing') return <Play size={20} className="text-risk-amber" />;
    return <Clock size={20} className="text-text-secondary" />;
  };

  const getStatusColor = (status) => {
    if (status === 'completed') return 'border-risk-green';
    if (status === 'executing') return 'border-risk-amber';
    return 'border-text-secondary';
  };

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
          Remediation & Actions
        </h2>
        {!loading && tasks.length > 0 && (
          <div className="flex items-center gap-2 px-3 py-1 bg-green-500 bg-opacity-10 rounded-full">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-green-500 font-medium">LIVE</span>
          </div>
        )}
      </div>

      {loading ? (
        <div className="bg-bg-card rounded-lg p-12 text-center">
          <div className="animate-spin w-8 h-8 border-4 border-visa-blue border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-text-secondary">Loading remediation data...</p>
        </div>
      ) : tasks.length === 0 ? (
        <div className="bg-bg-card rounded-lg p-12 text-center">
          <CheckCircle size={48} className="text-risk-green mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-text-primary mb-2">
            No Active Remediation Tasks
          </h3>
          <p className="text-text-secondary max-w-md mx-auto">
            All violations have been addressed. Use the Multi-Regulation Scanner or other monitoring tools to detect new violations.
          </p>
        </div>
      ) : (
        <>
          {/* Active Remediation Tasks */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-text-primary">
                Active Remediation Tasks
              </h3>
              <p className="text-sm text-text-secondary">
                {tasks.length} task{tasks.length !== 1 ? 's' : ''} generated from {violations.length} violation{violations.length !== 1 ? 's' : ''}
              </p>
            </div>
            <div className="grid gap-4">
              <AnimatePresence>
                {tasks.map((task, index) => (
                  <motion.div
                    key={task.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: task.status === 'completed' ? 0.7 : 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: index * 0.05 }}
                    className={`bg-bg-card rounded-lg p-6 border-l-4 ${getStatusColor(task.status)}`}
                    style={
                      task.status === 'executing'
                        ? {
                            backgroundImage:
                              'linear-gradient(90deg, transparent 0%, rgba(26,115,232,0.1) 50%, transparent 100%)',
                            backgroundSize: '200% 100%',
                            animation: 'shimmer 2s linear infinite'
                          }
                        : {}
                    }
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(task.status)}
                        <div>
                          <h4 className="text-lg font-semibold text-text-primary">
                            {task.title}
                          </h4>
                          <p className="text-sm text-text-secondary mt-1">
                            Responsible: {task.agent}
                          </p>
                        </div>
                      </div>
                      <span
                        className={`px-3 py-1 rounded text-xs font-medium uppercase ${
                          task.status === 'completed'
                            ? 'bg-risk-green text-white'
                            : task.status === 'executing'
                            ? 'bg-risk-amber text-white'
                            : 'bg-text-secondary text-white'
                        }`}
                      >
                        {task.status}
                      </span>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <p className="text-text-secondary">
                          Impacted Goal: {task.goal}
                        </p>
                        {task.regulation && (
                          <span className="text-xs text-visa-blue font-medium">
                            {task.regulation}
                          </span>
                        )}
                      </div>

                      {/* Progress bar */}
                      <div className="w-full bg-border-color rounded-full h-2 overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${task.progress}%` }}
                          transition={{ duration: 0.5, delay: 0.2 }}
                          className={`h-full ${
                            task.status === 'completed'
                              ? 'bg-risk-green'
                              : task.status === 'executing'
                              ? 'bg-risk-amber'
                              : 'bg-text-secondary'
                          }`}
                        ></motion.div>
                      </div>
                      <div className="flex items-center justify-between">
                        <p className="text-xs text-text-secondary">
                          {task.progress}% Complete
                        </p>
                        {task.violationIds && task.violationIds.length > 0 && (
                          <p className="text-xs text-text-secondary font-mono">
                            {task.violationIds.slice(0, 2).join(', ')}
                            {task.violationCount > 2 && ` +${task.violationCount - 2} more`}
                          </p>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>

          {/* AI-Generated Recommendations */}
          <div className="bg-bg-card rounded-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles size={20} className="text-visa-blue" />
              <h3 className="text-xl font-semibold text-text-primary">
                {recommendation.title}
              </h3>
            </div>
            <p className="text-text-primary leading-relaxed mb-4">
              {recommendation.content}
            </p>
            {recommendation.steps && recommendation.steps.length > 0 && (
              <div className="mt-4 p-4 bg-border-color rounded">
                <p className="text-sm text-text-secondary">
                  <span className="font-semibold text-accent-blue">Recommended Actions:</span>
                </p>
                <ul className="mt-2 space-y-1">
                  {recommendation.steps.map((step, idx) => (
                    <li key={idx} className="text-sm text-text-secondary flex items-start gap-2">
                      <span className="text-accent-blue">•</span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Human-in-the-Loop */}
          <div className="bg-bg-card rounded-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <AlertCircle size={20} className="text-risk-amber" />
              <h3 className="text-xl font-semibold text-text-primary">
                Human Approval Required
              </h3>
            </div>
            <p className="text-text-secondary mb-4">
              {tasks.filter(t => t.status === 'planned' || t.status === 'executing').length > 0 
                ? `${tasks.filter(t => t.status === 'planned' || t.status === 'executing').length} remediation task${tasks.filter(t => t.status === 'planned' || t.status === 'executing').length !== 1 ? 's' : ''} require${tasks.filter(t => t.status === 'planned' || t.status === 'executing').length === 1 ? 's' : ''} human authorization before execution.`
                : 'All remediation tasks have been completed or approved.'}
            </p>
            <div className="flex gap-4">
              <button 
                className={`${
                  tasks.filter(t => t.status === 'planned').length > 0
                    ? 'bg-accent-blue hover:bg-opacity-90'
                    : 'bg-border-color cursor-not-allowed'
                } text-white px-6 py-2 rounded transition-colors`}
                disabled={tasks.filter(t => t.status === 'planned').length === 0}
              >
                Approve All Actions
              </button>
              <button 
                className={`${
                  tasks.length > 0
                    ? 'bg-border-color hover:bg-text-secondary'
                    : 'bg-border-color cursor-not-allowed'
                } text-text-primary px-6 py-2 rounded transition-colors`}
                disabled={tasks.length === 0}
              >
                Review Individual Tasks
              </button>
              <button className="bg-transparent border border-risk-red text-risk-red hover:bg-risk-red hover:text-white px-6 py-2 rounded transition-colors">
                Simulate Remediation
              </button>
            </div>
          </div>

          {/* Remediation Statistics */}
          <div className="grid grid-cols-4 gap-4">
            <motion.div 
              className="bg-bg-card rounded-lg p-4"
              whileHover={{ scale: 1.02 }}
              transition={{ duration: 0.2 }}
            >
              <div className="text-2xl font-bold text-risk-green">
                {tasks.filter((t) => t.status === 'completed').length}
              </div>
              <div className="text-sm text-text-secondary">Completed</div>
            </motion.div>
            <motion.div 
              className="bg-bg-card rounded-lg p-4"
              whileHover={{ scale: 1.02 }}
              transition={{ duration: 0.2 }}
            >
              <div className="text-2xl font-bold text-risk-amber">
                {tasks.filter((t) => t.status === 'executing').length}
              </div>
              <div className="text-sm text-text-secondary">In Progress</div>
            </motion.div>
            <motion.div 
              className="bg-bg-card rounded-lg p-4"
              whileHover={{ scale: 1.02 }}
              transition={{ duration: 0.2 }}
            >
              <div className="text-2xl font-bold text-text-secondary">
                {tasks.filter((t) => t.status === 'planned').length}
              </div>
              <div className="text-sm text-text-secondary">Planned</div>
            </motion.div>
            <motion.div 
              className="bg-bg-card rounded-lg p-4"
              whileHover={{ scale: 1.02 }}
              transition={{ duration: 0.2 }}
            >
              <div className="text-2xl font-bold text-text-primary">
                {tasks.length > 0
                  ? Math.round(tasks.reduce((acc, t) => acc + t.progress, 0) / tasks.length)
                  : 0}
                %
              </div>
              <div className="text-sm text-text-secondary">Overall Progress</div>
            </motion.div>
          </div>
        </>
      )}

      <style jsx>{`
        @keyframes shimmer {
          0% { background-position: 0% 0; }
          100% { background-position: 200% 0; }
        }
      `}</style>
    </motion.div>
  );
};

export default Remediation;
