import { useEffect, useState, useRef, useCallback } from 'react';
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
  const [topics, setTopics] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const fetchGraphData = useCallback(async (topic) => {
    if (!topic) return;
    try {
      const res = await fetch(`${API_URL}/api/graph/visualize?topic=${encodeURIComponent(topic)}`);
      if (!res.ok) return;
      const data = await res.json();
      setGraphData(data.data || { nodes: [], links: [] });
    } catch (err) {
      console.error('Graph fetch error:', err);
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    const userMessage = { role: 'user', content: query, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    const sentQuery = query;
    setQuery('');

    try {
      const res = await fetch(`${API_URL}/api/query/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: sentQuery, use_cache: true })
      });
      const data = await res.json();

      const aiMessage = {
        role: 'assistant',
        content: data.response || 'No response received.',
        topics: data.topics || [],
        recommendations: data.recommendations || [],
        explanation: data.explanation || '',
        cached: data.cached || false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
      setTopics(data.topics || []);
      setRecommendations(data.recommendations || []);

      if (data.topics && data.topics.length > 0) {
        setCurrentTopic(data.topics[0]);
        fetchGraphData(data.topics[0]);
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'error',
        content: `Failed to connect: ${err.message}`,
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleTopicClick = useCallback((topic) => {
    setCurrentTopic(topic);
    setQuery(`Tell me about ${topic}`);
    fetchGraphData(topic);
    inputRef.current?.focus();
  }, [fetchGraphData]);

  const handleRecommendationClick = useCallback((topic) => {
    setCurrentTopic(topic);
    setQuery(`Tell me about ${topic}`);
    fetchGraphData(topic);
    inputRef.current?.focus();
  }, [fetchGraphData]);

  return (
    <div className="min-h-screen relative">
      {/* Ambient Background */}
      <div className="ambient-glow" />

      <div className="relative z-10 flex h-screen">
        {/* ─── Main Chat Area ─── */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Header */}
          <header className="glass-panel-strong mx-4 mt-4 mb-2 px-6 py-4 rounded-2xl flex items-center justify-between">
            <div className="animate-fade-in">
              <h1 className="text-xl font-bold flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-400/20 flex items-center justify-center text-lg">
                  🧠
                </div>
                <span className="bg-gradient-to-r from-blue-300 via-purple-300 to-pink-300 bg-clip-text text-transparent">
                  Agentic AI Research Assistant
                </span>
              </h1>
              <p className="text-[11px] text-gray-500 mt-1 ml-12 font-medium tracking-wide uppercase">
                Graph-Based Knowledge · AI Recommendations · DSA Integration
              </p>
            </div>
            <div className="flex gap-2">
              <button
                id="toggle-graph-btn"
                onClick={() => setShowGraph(!showGraph)}
                className={`glass-button text-sm flex items-center gap-2 ${
                  showGraph ? '!border-blue-400/30 !text-blue-300 !bg-blue-500/10' : ''
                }`}
              >
                <span className="text-base">📊</span>
                <span className="hidden sm:inline">Graph</span>
              </button>
            </div>
          </header>

          {/* Topics Bar */}
          {topics.length > 0 && (
            <div className="mx-4 mb-2 px-4 py-2.5 glass-panel flex items-center gap-3 animate-slide-up">
              <span className="text-[10px] uppercase tracking-widest text-gray-500 font-semibold whitespace-nowrap">
                Topics
              </span>
              <div className="flex gap-2 overflow-x-auto flex-1">
                {topics.map((topic, i) => (
                  <button
                    key={i}
                    onClick={() => handleTopicClick(topic)}
                    className="topic-chip whitespace-nowrap"
                  >
                    {topic}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-2 space-y-3">
            {messages.length === 0 && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center max-w-md animate-fade-in">
                  <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-white/[0.06] flex items-center justify-center text-4xl">
                    🚀
                  </div>
                  <h2 className="text-2xl font-bold mb-3 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                    Welcome to AI Research
                  </h2>
                  <p className="text-sm text-gray-500 mb-6 leading-relaxed">
                    Ask any question to explore topics with AI-powered insights,
                    dynamic knowledge graphs, and smart recommendations.
                  </p>
                  <div className="grid grid-cols-2 gap-2.5">
                    {[
                      { icon: '✨', label: 'Topic Extraction' },
                      { icon: '📈', label: 'Knowledge Graphs' },
                      { icon: '🎯', label: 'Smart Recommendations' },
                      { icon: '🧠', label: 'BFS Traversal' },
                    ].map((item, i) => (
                      <div key={i} className="glass-panel px-3 py-2.5 text-xs text-gray-400 flex items-center gap-2">
                        <span>{item.icon}</span>
                        <span>{item.label}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up`}
              >
                <div
                  className={`max-w-[70%] px-5 py-4 rounded-2xl ${
                    msg.role === 'user'
                      ? 'bubble-user'
                      : msg.role === 'error'
                      ? 'bubble-error'
                      : 'bubble-ai'
                  }`}
                >
                  {/* Role Label */}
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-[10px] uppercase tracking-widest text-gray-500 font-semibold">
                      {msg.role === 'user' ? 'You' : msg.role === 'error' ? 'Error' : 'AI Assistant'}
                    </span>
                    {msg.cached && (
                      <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-green-500/10 text-green-400 border border-green-500/20">
                        cached
                      </span>
                    )}
                  </div>

                  {/* Content */}
                  <p className="text-sm leading-relaxed whitespace-pre-wrap text-gray-200">
                    {msg.content}
                  </p>

                  {/* Topics in message */}
                  {msg.topics && msg.topics.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-white/[0.06]">
                      <p className="text-[10px] font-semibold mb-2 text-blue-400/80 uppercase tracking-wider flex items-center gap-1.5">
                        <span>🎯</span> Extracted Topics
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.topics.slice(0, 5).map((topic, i) => (
                          <button
                            key={i}
                            onClick={() => handleTopicClick(topic)}
                            className="topic-chip text-[11px]"
                          >
                            {topic}
                          </button>
                        ))}
                      </div>
                      {msg.explanation && (
                        <p className="text-[11px] text-gray-500 mt-2.5 italic leading-relaxed">
                          💭 {msg.explanation}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Typing Indicator */}
            {loading && (
              <div className="flex justify-start animate-fade-in">
                <div className="bubble-ai px-5 py-4 rounded-2xl">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1.5">
                      <div className="typing-dot" />
                      <div className="typing-dot" />
                      <div className="typing-dot" />
                    </div>
                    <span className="text-xs text-gray-500">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Composer */}
          <div className="p-4">
            <form onSubmit={handleSubmit} className="glass-panel-strong p-3 flex items-center gap-3">
              <input
                ref={inputRef}
                id="query-input"
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about any topic..."
                className="flex-1 glass-input px-4 py-3 text-sm bg-transparent border-none focus:ring-0"
                disabled={loading}
              />
              <button
                id="send-button"
                type="submit"
                disabled={loading || !query.trim()}
                className="gradient-button px-6 py-3 text-sm disabled:opacity-40 disabled:cursor-not-allowed disabled:transform-none flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Processing</span>
                  </>
                ) : (
                  <>
                    <span>Send</span>
                    <span>→</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* ─── Right Panel: Recommendations ─── */}
        <div className="w-80 flex flex-col gap-2 p-4 pl-0">
          <RecommendationPanel
            currentTopic={currentTopic}
            recommendations={recommendations}
            onTopicSelect={handleRecommendationClick}
          />
        </div>
      </div>

      {/* ─── Bottom: Knowledge Graph Panel ─── */}
      {showGraph && (
        <div className="fixed bottom-0 left-0 right-0 z-20 animate-slide-up">
          <div className="glass-panel-strong mx-4 mb-4 overflow-hidden" style={{ height: '320px' }}>
            <div className="flex items-center justify-between px-5 py-3 border-b border-white/[0.06]">
              <div className="flex items-center gap-3">
                <span className="text-base">📊</span>
                <h3 className="text-sm font-semibold text-gray-300">Knowledge Graph</h3>
                {currentTopic && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    {currentTopic}
                  </span>
                )}
              </div>
              <button
                onClick={() => setShowGraph(false)}
                className="w-7 h-7 rounded-lg bg-white/[0.04] border border-white/[0.06] flex items-center justify-center text-gray-500 hover:text-white hover:bg-white/[0.08] transition-all"
              >
                ✕
              </button>
            </div>
            <div className="h-[calc(100%-48px)]">
              <GraphVisualization
                topic={currentTopic}
                graphData={graphData}
                onTopicClick={handleTopicClick}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
