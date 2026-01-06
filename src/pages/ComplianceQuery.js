import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Send, BookOpen, AlertCircle, CheckCircle, Brain } from 'lucide-react';

const ComplianceQuery = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      type: 'system',
      content: 'Welcome! Ask me anything about compliance regulations, violations, or policies.',
      timestamp: new Date()
    }
  ]);
  const [loading, setLoading] = useState(false);

  const sampleQueries = [
    "Is PAN allowed in application logs?",
    "What are the GDPR requirements for data retention?",
    "Show me recent PCI-DSS violations",
    "What regulations apply to customer emails?"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    const userMessage = {
      type: 'user',
      content: query,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      // Call RAG query endpoint
      const response = await fetch('http://localhost:8000/regulations/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query })
      });

      if (response.ok) {
        const data = await response.json();
        
        const aiMessage = {
          type: 'assistant',
          content: data.answer || 'No answer available.',
          obligations: data.obligations || [],
          confidence: data.confidence || null,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, aiMessage]);
      } else {
        // Mock response for demo if endpoint not available
        const mockMessage = {
          type: 'assistant',
          content: getMockResponse(query),
          timestamp: new Date()
        };
        setMessages(prev => [...prev, mockMessage]);
      }
    } catch (error) {
      console.error('Query error:', error);
      
      // Provide mock response for demo
      const mockMessage = {
        type: 'assistant',
        content: getMockResponse(query),
        timestamp: new Date()
      };
      setMessages(prev => [...prev, mockMessage]);
    } finally {
      setLoading(false);
      setQuery('');
    }
  };

  const getMockResponse = (question) => {
    const q = question.toLowerCase();
    
    if (q.includes('pan') && q.includes('log')) {
      return "No. PCI-DSS Requirement 3.2.1 explicitly prohibits storing Primary Account Numbers (PAN) in application logs. PAN must be masked or encrypted at all times when stored or transmitted. Any PAN exposure in logs is a CRITICAL violation.";
    } else if (q.includes('gdpr') && q.includes('retention')) {
      return "Under GDPR Article 5(1)(e), personal data must be kept only for as long as necessary for the purposes for which it was collected. Organizations must define and document specific retention periods for different data categories. Financial services typically retain transaction data for 7 years for audit purposes, but customer contact information should be deleted upon request under Article 17 (Right to Erasure).";
    } else if (q.includes('violation')) {
      return "Based on current monitoring, I've detected PAN exposure violations in support tickets and application logs. All violations have been classified as CRITICAL severity and evidence has been captured. Would you like me to provide a detailed breakdown?";
    } else if (q.includes('email')) {
      return "Customer emails are subject to multiple regulations: GDPR (Article 6 - lawful processing), CCPA (personal information protection), and PCI-DSS if they contain payment card data. Emails must be encrypted in transit, access-controlled, and included in data protection impact assessments.";
    }
    
    return "I can help you understand compliance requirements across PCI-DSS, GDPR, and CCPA. Ask me about specific regulations, violations, or compliance controls.";
  };

  const handleSampleQuery = (sampleQuery) => {
    setQuery(sampleQuery);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-8 space-y-6 h-screen flex flex-col"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-visa-blue to-visa-orange bg-clip-text text-transparent">
            Compliance Intelligence Assistant
          </h1>
          <p className="text-text-secondary mt-2">
            Natural language access to regulations, violations, and compliance knowledge
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 bg-visa-blue bg-opacity-10 rounded-lg">
            <Brain className="text-visa-blue" size={20} />
            <span className="text-sm text-visa-blue font-semibold">RAG-Powered</span>
          </div>
        </div>
      </div>

      {/* Sample Queries */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-bg-card rounded-lg p-4 border-2 border-gray-200"
      >
        <h3 className="text-sm font-semibold text-text-secondary mb-3 flex items-center gap-2">
          <BookOpen size={16} />
          Try asking:
        </h3>
        <div className="grid grid-cols-2 gap-2">
          {sampleQueries.map((sq, idx) => (
            <button
              key={idx}
              onClick={() => handleSampleQuery(sq)}
              className="text-left px-3 py-2 bg-white border border-gray-200 rounded-lg hover:border-visa-blue hover:bg-visa-blue hover:bg-opacity-5 transition-all text-sm"
            >
              "{sq}"
            </button>
          ))}
        </div>
      </motion.div>

      {/* Chat Messages */}
      <div className="flex-1 bg-bg-card rounded-lg border-2 border-gray-200 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-3xl ${msg.type === 'user' ? 'ml-12' : 'mr-12'}`}>
                <div className={`flex items-start gap-3 ${msg.type === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div className={`p-2 rounded-full ${
                    msg.type === 'user' 
                      ? 'bg-visa-blue' 
                      : msg.type === 'system'
                      ? 'bg-gray-400'
                      : 'bg-visa-orange'
                  }`}>
                    {msg.type === 'user' ? (
                      <MessageSquare className="text-white" size={20} />
                    ) : msg.type === 'system' ? (
                      <AlertCircle className="text-white" size={20} />
                    ) : (
                      <Brain className="text-white" size={20} />
                    )}
                  </div>
                  <div className={`flex-1 ${msg.type === 'user' ? 'text-right' : ''}`}>
                    <div className={`inline-block px-4 py-3 rounded-lg ${
                      msg.type === 'user'
                        ? 'bg-visa-blue text-white'
                        : 'bg-white border-2 border-gray-200'
                    }`}>
                      <p className={`text-sm ${msg.type === 'user' ? 'text-white' : 'text-text-primary'}`}>
                        {msg.content}
                      </p>
                      {msg.confidence && (
                        <div className="mt-2 pt-2 border-t border-gray-200">
                          <span className="text-xs text-text-secondary">
                            Confidence: {(msg.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                      )}
                      {msg.obligations && msg.obligations.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-gray-200">
                          <span className="text-xs text-text-secondary font-semibold">
                            Related Obligations:
                          </span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {msg.obligations.map((ob, i) => (
                              <span key={i} className="text-xs px-2 py-1 bg-visa-blue bg-opacity-10 text-visa-blue rounded">
                                {ob}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    <span className="text-xs text-text-secondary mt-1 inline-block">
                      {msg.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
          
          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-full bg-visa-orange">
                  <Brain className="text-white animate-pulse" size={20} />
                </div>
                <div className="bg-white border-2 border-gray-200 px-4 py-3 rounded-lg">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-visa-orange rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-visa-orange rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-visa-orange rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Input Form */}
        <div className="border-t-2 border-gray-200 p-4 bg-white">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about regulations, violations, or compliance requirements..."
              className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-visa-blue focus:outline-none"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-6 py-3 bg-visa-blue text-white rounded-lg hover:bg-opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send size={20} />
              Send
            </button>
          </form>
        </div>
      </div>
    </motion.div>
  );
};

export default ComplianceQuery;
