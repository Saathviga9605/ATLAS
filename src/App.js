import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';
import Sidebar from './components/Sidebar';
import ComplianceOverview from './pages/ComplianceOverview';
import GoalGraph from './pages/GoalGraph';
import LiveMonitoring from './pages/LiveMonitoring';
import Remediation from './pages/Remediation';
import Evidence from './pages/Evidence';
import AgentActivity from './pages/AgentActivity';
import ViolationAnalysis from './pages/ViolationAnalysis';
import ComplianceQuery from './pages/ComplianceQuery';
import MultiRegulationTest from './pages/MultiRegulationTest';

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-gradient-to-br from-white via-bg-card to-bg-secondary relative overflow-hidden">
        {/* Animated background elements */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <motion.div
            className="absolute top-20 right-20 w-96 h-96 bg-visa-orange rounded-full opacity-5 blur-3xl"
            animate={{
              x: [0, 50, -30, 0],
              y: [0, -40, 20, 0],
              scale: [1, 1.1, 0.9, 1],
            }}
            transition={{ duration: 20, repeat: Infinity }}
          />
          <motion.div
            className="absolute bottom-20 left-20 w-80 h-80 bg-visa-blue rounded-full opacity-5 blur-3xl"
            animate={{
              x: [0, -40, 30, 0],
              y: [0, 40, -20, 0],
              scale: [1, 0.8, 1.2, 1],
            }}
            transition={{ duration: 25, repeat: Infinity, delay: 5 }}
          />
          <motion.div
            className="absolute top-1/2 left-1/2 w-64 h-64 bg-visa-orange rounded-full opacity-3 blur-2xl transform -translate-x-1/2 -translate-y-1/2"
            animate={{
              rotate: [0, 360],
              scale: [1, 1.3, 0.7, 1],
            }}
            transition={{ duration: 30, repeat: Infinity }}
          />
        </div>

        <Sidebar />
        
        <main className="flex-1 ml-72 overflow-x-hidden relative z-10">
          {/* Creative Top Header with VISA Theme */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-r from-white via-bg-card to-white border-b-2 border-visa-orange backdrop-blur-lg sticky top-0 z-50 shadow-lg"
            style={{
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(250, 251, 252, 0.8) 100%)',
              backdropFilter: 'blur(20px)',
            }}
          >
            <div className="px-8 py-6 flex items-center justify-between relative">
              {/* Animated geometric shapes */}
              <div className="absolute top-0 right-0 w-20 h-20 bg-visa-blue opacity-5 rounded-full animate-bounce-gentle" 
                   style={{ animationDelay: '1s' }}></div>
              <div className="absolute bottom-0 left-1/3 w-16 h-16 bg-visa-orange opacity-5 rounded-lg animate-float" 
                   style={{ animationDelay: '2s' }}></div>

              <motion.div 
                className="flex flex-col"
                initial={{ x: -50, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 100 }}
              >
                <h2 className="text-4xl font-black">
                  <span className="bg-gradient-to-r from-visa-blue to-visa-orange bg-clip-text text-transparent">
                    COMPLIANCE
                  </span>
                  {' '}
                  <span className="text-text-primary">DASHBOARD</span>
                </h2>
                <motion.p 
                  className="text-lg text-visa-blue mt-1 font-bold tracking-wide"
                  animate={{ 
                    backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'] 
                  }}
                  transition={{ duration: 4, repeat: Infinity }}
                  style={{
                    background: 'linear-gradient(90deg, #003D82, #FF8200, #003D82)',
                    backgroundSize: '300% 100%',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  Real-time VISA Standard Monitoring & Analytics
                </motion.p>
              </motion.div>

              {/* Creative Status Indicator with Flexbox */}
              <motion.div
                className="flex items-center gap-6"
                initial={{ x: 50, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.4, type: "spring", stiffness: 100 }}
              >
                {/* Live Indicator */}
                <motion.div
                  className="flex items-center gap-3 px-6 py-3 rounded-2xl bg-gradient-to-r from-visa-blue to-visa-orange shadow-lg border-2 border-white"
                  whileHover={{ 
                    scale: 1.08,
                    boxShadow: "0 8px 32px rgba(0, 61, 130, 0.3)"
                  }}
                  whileTap={{ scale: 0.95 }}
                  transition={{ type: "spring", stiffness: 400 }}
                >
                  <motion.div 
                    className="w-3 h-3 bg-white rounded-full relative"
                    animate={{
                      scale: [1, 1.4, 1],
                      opacity: [1, 0.7, 1]
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity
                    }}
                  >
                    <motion.div
                      className="absolute inset-0 bg-white rounded-full"
                      animate={{
                        scale: [1, 2, 1],
                        opacity: [0.8, 0, 0.8]
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity
                      }}
                    />
                  </motion.div>
                  <span className="text-white text-sm font-bold uppercase tracking-wider">LIVE</span>
                </motion.div>

                {/* User Profile */}
                <motion.div
                  className="flex items-center gap-3 px-4 py-2 rounded-xl bg-white shadow-lg border border-border-color"
                  whileHover={{ 
                    scale: 1.05,
                    borderColor: '#FF8200'
                  }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <div className="w-8 h-8 bg-gradient-to-br from-visa-blue to-visa-orange rounded-full flex items-center justify-center">
                    <span className="text-white text-xs font-bold">UA</span>
                  </div>
                  <span className="text-text-primary font-semibold text-sm">User Admin</span>
                </motion.div>
              </motion.div>

              {/* Animated border line */}
              <motion.div
                className="absolute bottom-0 left-0 right-0 h-1"
                style={{
                  background: 'linear-gradient(90deg, transparent, #003D82, #FF8200, #003D82, transparent)',
                  backgroundSize: '200% 100%',
                }}
                animate={{
                  backgroundPosition: ['200% 0%', '-200% 0%']
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: "linear"
                }}
              />
            </div>
          </motion.div>

          {/* Main Content with Beautiful Flexbox Layout */}
          <motion.div 
            className="p-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.8 }}
          >
            <Routes>
              <Route path="/" element={<ComplianceOverview />} />
              <Route path="/goal-graph" element={<GoalGraph />} />
              <Route path="/monitoring" element={<LiveMonitoring />} />
              {/* <Route path="/remediation" element={<Remediation />} /> */}
              <Route path="/evidence" element={<Evidence />} />
              <Route path="/agents" element={<AgentActivity />} />
              <Route path="/violation-analysis" element={<ViolationAnalysis />} />
              <Route path="/compliance-query" element={<ComplianceQuery />} />
              <Route path="/multi-regulation-test" element={<MultiRegulationTest />} />
            </Routes>
          </motion.div>
        </main>
      </div>
    </Router>
  );
}

export default App;
