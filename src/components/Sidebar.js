import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, Network, Radio, Wrench, FolderOpen, Bot, Sparkles, Zap, MessageSquare, Shield } from 'lucide-react';
import { motion } from 'framer-motion';

const Sidebar = () => {
  const navItems = [
    { path: '/', icon: Home, label: 'Compliance Overview' },
    { path: '/goal-graph', icon: Network, label: 'Compliance Goal Graph' },
    { path: '/monitoring', icon: Radio, label: 'Live Monitoring' },
    { path: '/compliance-query', icon: MessageSquare, label: 'Ask Compliance AI', featured: true },
    { path: '/multi-regulation-test', icon: Shield, label: 'Multi-Regulation Scanner' },
    // { path: '/remediation', icon: Wrench, label: 'Remediation & Actions' },
    { path: '/evidence', icon: FolderOpen, label: 'Evidence & Audit Trail' },
    { path: '/agents', icon: Bot, label: 'Agent Activity' },
    { path: '/violation-analysis', icon: Sparkles, label: 'AI Violation Analysis' },
  ];

  return (
    <motion.aside 
      initial={{ x: -300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.8, type: "spring", damping: 25 }}
      className="w-72 bg-white border-r-4 border-visa-blue h-screen fixed left-0 top-0 flex flex-col shadow-2xl z-50"
      style={{
        background: 'linear-gradient(180deg, #FFFFFF 0%, #FAFBFC 100%)',
        boxShadow: '4px 0 40px rgba(0, 61, 130, 0.15)',
      }}
    >
      {/* Header */}
      <motion.div 
        className="p-8 border-b-2 border-visa-orange relative overflow-hidden"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="absolute top-0 right-0 w-24 h-24 bg-visa-orange opacity-5 rounded-full animate-float"></div>
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-3">
            <motion.div 
              className="w-12 h-12 bg-gradient-to-br from-visa-blue to-visa-orange rounded-xl flex items-center justify-center shadow-lg"
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.8 }}
            >
              <Sparkles size={24} className="text-white" />
            </motion.div>
            <div>
              <h1 className="text-2xl font-black bg-gradient-to-r from-visa-blue to-visa-orange bg-clip-text text-transparent">
                ATLAS
              </h1>
            </div>
          </div>
          <p className="text-sm text-visa-blue font-bold tracking-wider uppercase">
            PCI/PII Real-Time Analytics
          </p>
        </div>
      </motion.div>

      {/* Navigation */}
      <nav className="flex-1 p-6 overflow-y-auto">
        <motion.ul 
          className="space-y-3"
          initial="hidden"
          animate="visible"
          variants={{
            hidden: { opacity: 0 },
            visible: {
              opacity: 1,
              transition: { staggerChildren: 0.1 }
            }
          }}
        >
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <motion.li 
                key={item.path}
                variants={{
                  hidden: { opacity: 0, x: -20 },
                  visible: { opacity: 1, x: 0 }
                }}
                whileHover={{ scale: 1.03 }}
              >
                <NavLink
                  to={item.path}
                  end={item.path === '/'}
                  className={({ isActive }) =>
                    `flex items-center gap-4 px-6 py-4 rounded-2xl transition-all duration-300 border-2 relative ${
                      isActive
                        ? 'bg-gradient-to-r from-visa-blue to-visa-orange text-white border-transparent shadow-lg'
                        : 'text-text-primary hover:text-visa-blue border-transparent hover:border-visa-blue hover:bg-bg-card'
                    } ${item.featured ? 'ring-2 ring-visa-orange ring-offset-2' : ''}`
                  }
                >
                  {item.featured && (
                    <motion.div
                      className="absolute -top-1 -right-1 w-3 h-3 bg-visa-orange rounded-full"
                      animate={{ scale: [1, 1.3, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  )}
                  <Icon size={22} />
                  <span className="text-sm font-bold">{item.label}</span>
                </NavLink>
              </motion.li>
            );
          })}
        </motion.ul>
      </nav>

      {/* Footer */}
      <motion.div 
        className="p-6 border-t-2 border-visa-orange"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
      >
        <div className="flex items-center gap-4 p-4 rounded-2xl bg-gradient-to-r from-visa-blue to-visa-orange shadow-lg">
          <motion.div 
            className="w-4 h-4 bg-risk-green rounded-full"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <div className="flex-1">
            <span className="text-white text-sm font-bold">System Status</span>
            <div className="text-xs text-white opacity-90">All Services Active</div>
          </div>
          <motion.div animate={{ rotate: [0, 360] }} transition={{ duration: 4, repeat: Infinity }}>
            <Zap size={18} className="text-white" />
          </motion.div>
        </div>
      </motion.div>
    </motion.aside>
  );
};

export default Sidebar;