import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Clock, MoreHorizontal, RefreshCw } from 'lucide-react';
import api from '../services/api';

const AgentActivity = () => {
  const [agents, setAgents] = useState([]);
  const [recentDecisions, setRecentDecisions] = useState([]);
  const [summary, setSummary] = useState({
    active_agents: 0,
    total_tasks_today: 0,
    recent_decisions: 0,
    system_uptime: 99.8,
    health_status: 'All systems operational'
  });
  const [instructions, setInstructions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  const loadAgentStatus = async () => {
    try{
      setLoading(true);
      const data = await api.getAgentStatus();
      setAgents(data.agents || []);
      setRecentDecisions(data.decisions || []);
      setSummary(data.summary || summary);
      setInstructions(data.instructions || null);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load agent status:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAgentStatus();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadAgentStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIndicator = (status) => {
    if (status === 'active') {
      return (
        <motion.div
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
          className="w-3 h-3 bg-risk-green rounded-full"
        ></motion.div>
      );
    }
    if (status === 'waiting') {
      return (
        <div className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{
                repeat: Infinity,
                duration: 1.5,
                delay: i * 0.2,
              }}
              className="w-1.5 h-1.5 bg-risk-amber rounded-full"
            ></motion.div>
          ))}
        </div>
      );
    }
    return <div className="w-3 h-3 bg-text-secondary rounded-full"></div>;
  };

  const getStatusText = (status) => {
    if (status === 'active') return 'Active';
    if (status === 'waiting') return 'Waiting';
    return 'Idle';
  };

  const getStatusColor = (status) => {
    if (status === 'active') return 'text-risk-green';
    if (status === 'waiting') return 'text-risk-amber';
    return 'text-text-secondary';
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'Critical':
        return 'bg-risk-red';
      case 'High':
        return 'bg-risk-amber';
      case 'Medium':
        return 'bg-accent-blue';
      case 'Low':
        return 'bg-text-secondary';
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
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-text-primary">Agent Activity</h2>
        <div className="flex items-center gap-3">
          {lastUpdate && (
            <span className="text-sm text-text-secondary">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={loadAgentStatus}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-visa-blue text-white rounded-lg hover:bg-opacity-90 transition-all disabled:opacity-50"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Instructions Banner (shown when agents are idle) */}
      {instructions && summary.active_agents === 0 && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-visa-blue to-accent-blue rounded-lg p-6 text-white"
        >
          <h3 className="text-lg font-bold mb-2">🚀 How to Activate Agents</h3>
          <p className="text-sm mb-4 opacity-90">{instructions.how_to_activate}</p>
          <div className="bg-white bg-opacity-10 rounded-lg p-4">
            <p className="text-sm font-semibold mb-2">Try these sample violations:</p>
            <ul className="text-sm space-y-1 opacity-90">
              {instructions.sample_violations?.map((sample, idx) => (
                <li key={idx}>• {sample}</li>
              ))}
            </ul>
          </div>
        </motion.div>
      )}

      {/* Agent List */}
      <div className="grid grid-cols-2 gap-6">
        {agents.map((agent, index) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-bg-card rounded-lg p-6 border border-border-color hover:border-accent-blue transition-colors"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <Activity size={24} className="text-accent-blue" />
                <div>
                  <h3 className="text-lg font-semibold text-text-primary">
                    {agent.name}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    {getStatusIndicator(agent.status)}
                    <span className={`text-sm font-medium ${getStatusColor(agent.status)}`}>
                      {getStatusText(agent.status)}
                    </span>
                  </div>
                </div>
              </div>
              <button className="text-text-secondary hover:text-text-primary transition-colors">
                <MoreHorizontal size={20} />
              </button>
            </div>

            <p className="text-text-secondary text-sm mb-4">{agent.description}</p>

            <div className="space-y-3 border-t border-border-color pt-4">
              <div className="flex items-start gap-2">
                <Clock size={16} className="text-text-secondary mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-text-primary">{agent.lastAction}</p>
                  <p className="text-xs text-text-secondary mt-1">
                    {agent.lastActionTime}
                  </p>
                </div>
              </div>

              <div className="bg-bg-primary rounded px-3 py-2">
                <p className="text-xs text-text-secondary">Tasks Completed Today</p>
                <p className="text-2xl font-bold text-text-primary">{agent.tasksToday}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Recent Decisions */}
      <div className="bg-bg-card rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4 text-text-primary">
          Recent Agent Decisions
        </h3>
        <p className="text-sm text-text-secondary mb-6">
          Human-readable reasoning traces from autonomous agents
        </p>

        <div className="space-y-4">
          {recentDecisions.map((decision, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-bg-primary rounded-lg p-4 border-l-4 border-accent-blue"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-semibold text-accent-blue">
                    {decision.agent}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-medium text-white ${getImpactColor(
                      decision.impact
                    )}`}
                  >
                    {decision.impact}
                  </span>
                </div>
                <span className="text-xs text-text-secondary font-mono">
                  {decision.timestamp}
                </span>
              </div>
              <p className="text-text-primary text-sm leading-relaxed">
                {decision.decision}
              </p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Agent System Health */}
      <div className="bg-bg-card rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-text-primary">System Health</h3>
          <span className="px-3 py-1 bg-risk-green text-white text-sm font-medium rounded-full">
            {summary.health_status || 'Operational'}
          </span>
        </div>
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-bg-primary rounded-lg p-4">
            <div className="text-2xl font-bold text-risk-green">
              {summary.active_agents}
            </div>
            <div className="text-sm text-text-secondary">Active Agents</div>
          </div>
          <div className="bg-bg-primary rounded-lg p-4">
            <div className="text-2xl font-bold text-text-primary">
              {summary.total_tasks_today}
            </div>
            <div className="text-sm text-text-secondary">Total Tasks Today</div>
          </div>
          <div className="bg-bg-primary rounded-lg p-4">
            <div className="text-2xl font-bold text-text-primary">
              {summary.recent_decisions}
            </div>
            <div className="text-sm text-text-secondary">Recent Decisions</div>
          </div>
          <div className="bg-bg-primary rounded-lg p-4">
            <div className="text-2xl font-bold text-risk-green">{summary.system_uptime}%</div>
            <div className="text-sm text-text-secondary">System Uptime</div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default AgentActivity;
