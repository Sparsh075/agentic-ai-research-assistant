import { useEffect, useState, useRef } from 'react';
import './App.css';
import { API_URL } from './services/api';
import GraphVisualization from './components/GraphVisualization';
import RecommendationPanel from './components/RecommendationPanel';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentTopic, setCurrentTopic] = useState('');
  const [showGraph, setShowGraph] = useState(false);
  const [showRecommendations, setShowRecommendations] = useState(true);
  const [topics, setTopics] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    console.debug('API_URL', API_URL);
    const userMessage = { role: 'user', content: query, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);

    try {
      const url = `${API_URL}/api/query/process`;
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, use_cache: true })
      });
      const data = await res.json();
      
      const aiMessage = {
        role: 'assistant',
        content: data.response,
        topics: data.topics || [],
        recommendations: data.recommendations || [],
        explanation: data.explanation || '',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      setTopics(data.topics || []);
      setRecommendations(data.recommendations || []);
      
      if (data.topics && data.topics.length > 0) {
        setCurrentTopic(data.topics[0]);
      }
    } catch (err) {
      const errorMessage = {
        role: 'error',
        content: `Error: ${err.message} - ${API_URL}/api/query/process`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      console.error('Query request failed', err);
    } finally {
      setLoading(false);
      setQuery('');
    }
  };

  const handleTopicClick = (topic) => {
    setCurrentTopic(topic);
    setQuery(`Tell me about ${topic}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      <div className="flex h-screen">
        {/* Graph Panel */}
        {showGraph && (
          <div className="w-1/3 border-r border-gray-700 overflow-auto bg-gray-900 p-4">
            <GraphVisualization topic={currentTopic} onTopicClick={handleTopicClick} />
          </div>
        )}

        {/* Main Chat Area */}
        <div className={`flex-1 flex flex-col ${showGraph ? 'w-2/3' : 'w-full'}`}>
          {/* Header */}
          <div className="border-b border-gray-700/50 bg-gradient-to-r from-gray-800/80 via-gray-800/60 to-gray-800/80 backdrop-blur-md p-6 shadow-lg">
            <div className="flex items-center justify-between">
              <div className="animate-fade-in">
                <h1 className="text-3xl font-bold flex items-center gap-3 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  🚀 Agentic AI Research Assistant
                </h1>
                <p className="text-gray-400 text-sm mt-1 font-medium">Advanced Graph-Based Knowledge System with AI-Powered Insights</p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowGraph(!showGraph)}
                  className={`px-5 py-2.5 rounded-xl font-medium transition-all duration-300 transform hover:scale-105 ${
                    showGraph
                      ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/25'
                      : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50 hover:text-white backdrop-blur-sm border border-gray-600/50'
                  }`}
                >
                  📊 Knowledge Graph
                </button>
                <button
                  onClick={() => setShowRecommendations(!showRecommendations)}
                  className={`px-5 py-2.5 rounded-xl font-medium transition-all duration-300 transform hover:scale-105 ${
                    showRecommendations
                      ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg shadow-green-500/25'
                      : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50 hover:text-white backdrop-blur-sm border border-gray-600/50'
                  }`}
                >
                  💡 Recommendations
                </button>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-auto p-6 space-y-4">
            {messages.length === 0 && (
              <div className="flex items-center justify-center h-full text-center">
                <div>
                  <h2 className="text-2xl font-bold mb-2">Welcome to Advanced AI Assistant</h2>
                  <p className="text-gray-400">Ask questions and explore topics with:</p>
                  <ul className="text-gray-400 mt-4 space-y-1">
                    <li>✨ Intelligent topic extraction</li>
                    <li>📈 Dynamic knowledge graphs</li>
                    <li>🎯 Smart recommendations</li>
                    <li>📚 Learning path generation</li>
                  </ul>
                </div>
              </div>
            )}
            
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-in`}>
                <div
                  className={`max-w-2xl px-5 py-4 rounded-2xl shadow-lg backdrop-blur-sm border ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white border-blue-500/30 shadow-blue-500/20'
                      : msg.role === 'error'
                      ? 'bg-gradient-to-r from-red-600 to-red-700 text-white border-red-500/30 shadow-red-500/20'
                      : 'bg-gradient-to-br from-gray-700/80 to-gray-800/80 text-gray-100 border-gray-600/30 shadow-gray-900/20'
                  } transition-all duration-300 hover:shadow-xl`}
                >
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content.substring(0, 800)}</p>
                  {msg.topics && msg.topics.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-gray-600/50">
                      <p className="text-xs font-semibold mb-3 text-blue-300 flex items-center gap-2">
                        🎯 Topics Extracted:
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {msg.topics.slice(0, 5).map((topic, i) => (
                          <button
                            key={i}
                            onClick={() => handleTopicClick(topic)}
                            className="text-xs bg-gradient-to-r from-blue-500/20 to-purple-500/20 hover:from-blue-500/30 hover:to-purple-500/30 border border-blue-400/30 hover:border-blue-400/50 px-3 py-1.5 rounded-full cursor-pointer transition-all duration-200 transform hover:scale-105 backdrop-blur-sm"
                          >
                            {topic}
                          </button>
                        ))}
                      </div>
                      {msg.explanation && (
                        <p className="text-xs text-gray-400 mt-3 italic bg-gray-800/50 p-2 rounded-lg border border-gray-600/30">
                          💭 {msg.explanation}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-700/50 bg-gradient-to-r from-gray-800/80 via-gray-800/60 to-gray-800/80 backdrop-blur-md p-6 shadow-lg">
            <form onSubmit={handleSubmit} className="flex gap-3">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question about any topic..."
                className="flex-1 px-5 py-3.5 bg-gray-700/50 border border-gray-600/50 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20 backdrop-blur-sm transition-all duration-200"
              />
              <button
                type="submit"
                disabled={loading}
                className="px-8 py-3.5 bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 hover:from-blue-500 hover:via-purple-500 hover:to-blue-600 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40"
              >
                {loading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Processing...
                  </div>
                ) : (
                  '✈️ Send'
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Recommendations Panel */}
        {showRecommendations && (
          <div className="w-80 border-l border-gray-700 bg-gray-900 overflow-auto p-4">
            <RecommendationPanel
              currentTopic={currentTopic}
              recommendations={recommendations}
              onTopicSelect={handleTopicClick}
            />
          </div>
        )}
      </div>
    </div>
  );
}

