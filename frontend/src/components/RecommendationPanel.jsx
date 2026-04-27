import { useState, useEffect } from 'react';
import API_URL from '../services/api';

const RecommendationPanel = ({ currentTopic, recommendations, onTopicSelect }) => {
  const [learningPath, setLearningPath] = useState(null);
  const [activeTab, setActiveTab] = useState('recommendations');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (currentTopic && activeTab === 'learning') {
      fetchLearningPath(currentTopic);
    }
  }, [currentTopic, activeTab]);

  const fetchLearningPath = async (topic) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/graph/learning-path/${encodeURIComponent(topic)}`);
      if (!response.ok) throw new Error('Failed to fetch');
      const data = await response.json();
      setLearningPath(data.learning_path || null);
    } catch (error) {
      console.error('Error fetching learning path:', error);
      setLearningPath(null);
    } finally {
      setLoading(false);
    }
  };

  const getSourceBadgeClass = (source) => {
    switch (source) {
      case 'graph': return 'source-badge-graph';
      case 'ai': return 'source-badge-ai';
      case 'popular': return 'source-badge-popular';
      default: return 'source-badge-ai';
    }
  };

  const getSourceLabel = (source) => {
    switch (source) {
      case 'graph': return '🔗 Graph';
      case 'ai': return '🤖 AI';
      case 'popular': return '⭐ Popular';
      default: return source || 'unknown';
    }
  };

  const levelConfig = {
    beginner: { color: 'text-emerald-400', dot: 'bg-emerald-400', border: 'border-emerald-500/20', icon: '🌱' },
    intermediate: { color: 'text-amber-400', dot: 'bg-amber-400', border: 'border-amber-500/20', icon: '📘' },
    advanced: { color: 'text-rose-400', dot: 'bg-rose-400', border: 'border-rose-500/20', icon: '🚀' },
  };

  return (
    <div className="h-full flex flex-col glass-panel-strong rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="px-5 pt-5 pb-3">
        <div className="flex items-center gap-2.5 mb-1">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-purple-500/15 to-pink-500/15 border border-purple-400/15 flex items-center justify-center text-base">
            💡
          </div>
          <div>
            <h2 className="text-sm font-bold text-gray-200">Recommendations</h2>
            <p className="text-[10px] text-gray-600 uppercase tracking-wider font-medium">AI-Powered Suggestions</p>
          </div>
        </div>
        {currentTopic && (
          <div className="mt-2.5 px-2.5 py-1.5 rounded-lg bg-blue-500/[0.06] border border-blue-500/10 flex items-center gap-2">
            <span className="text-[10px] text-gray-500">Topic:</span>
            <span className="text-[11px] text-blue-300 font-medium truncate">{currentTopic}</span>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mx-5 mb-3 p-1 rounded-xl bg-white/[0.02] border border-white/[0.04]">
        <button
          id="tab-recommendations"
          onClick={() => setActiveTab('recommendations')}
          className={`flex-1 px-3 py-2 text-[11px] font-medium rounded-lg transition-all duration-200 ${
            activeTab === 'recommendations'
              ? 'bg-blue-500/15 text-blue-300 border border-blue-500/20'
              : 'text-gray-500 hover:text-gray-300 border border-transparent'
          }`}
        >
          Related Topics
        </button>
        <button
          id="tab-learning"
          onClick={() => setActiveTab('learning')}
          className={`flex-1 px-3 py-2 text-[11px] font-medium rounded-lg transition-all duration-200 ${
            activeTab === 'learning'
              ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/20'
              : 'text-gray-500 hover:text-gray-300 border border-transparent'
          }`}
        >
          Learning Path
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-5 pb-5 space-y-2.5">
        {activeTab === 'recommendations' && (
          <>
            {recommendations && recommendations.length > 0 ? (
              recommendations.map((rec, idx) => (
                <div
                  key={idx}
                  onClick={() => onTopicSelect(rec.topic)}
                  className="recommendation-card group animate-slide-up"
                  style={{ animationDelay: `${idx * 60}ms` }}
                >
                  {/* Topic Name */}
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <h4 className="text-sm font-semibold text-gray-300 group-hover:text-blue-300 transition-colors leading-snug">
                      {rec.topic}
                    </h4>
                    <span className={`text-[9px] px-2 py-0.5 rounded-full font-medium whitespace-nowrap ${getSourceBadgeClass(rec.source)}`}>
                      {getSourceLabel(rec.source)}
                    </span>
                  </div>

                  {/* Explanation / Why */}
                  <p className="text-[11px] text-gray-500 group-hover:text-gray-400 transition-colors leading-relaxed mb-2.5">
                    {rec.explanation || rec.why || `Relevance: ${((rec.score || 0) * 100).toFixed(0)}%`}
                  </p>

                  {/* Score Bar */}
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-[3px] rounded-full bg-white/[0.04] overflow-hidden">
                      <div
                        className="score-bar"
                        style={{ width: `${Math.min(100, (rec.score || 0) * 100)}%` }}
                      />
                    </div>
                    <span className="text-[10px] text-gray-600 font-mono">
                      {((rec.score || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <EmptyState
                icon="🎯"
                title="No recommendations yet"
                subtitle="Ask a question to get AI-powered topic suggestions"
              />
            )}
          </>
        )}

        {activeTab === 'learning' && (
          <>
            {loading ? (
              <div className="flex flex-col items-center justify-center py-12 gap-3">
                <div className="w-6 h-6 border-2 border-emerald-500/20 border-t-emerald-400 rounded-full animate-spin" />
                <span className="text-[11px] text-gray-500">Building learning path...</span>
              </div>
            ) : learningPath ? (
              Object.entries(learningPath)
                .filter(([level]) => level !== 'full_path')
                .map(([level, topics]) => {
                  const config = levelConfig[level] || levelConfig.beginner;
                  return (
                    <div key={level} className="mb-4 animate-slide-up">
                      <div className="flex items-center gap-2 mb-2.5">
                        <span className="text-sm">{config.icon}</span>
                        <h4 className={`text-[11px] font-bold uppercase tracking-wider ${config.color}`}>
                          {level}
                        </h4>
                        <div className="flex-1 h-px bg-white/[0.04]" />
                      </div>
                      <div className={`space-y-1 pl-3 border-l ${config.border}`}>
                        {Array.isArray(topics) && topics.length > 0 ? (
                          topics.map((t, idx) => (
                            <button
                              key={idx}
                              onClick={() => onTopicSelect(t)}
                              className="block w-full text-left text-[12px] text-gray-400 hover:text-blue-300 transition-all duration-200 hover:translate-x-1 py-1.5 px-2.5 rounded-lg hover:bg-white/[0.03]"
                            >
                              {t}
                            </button>
                          ))
                        ) : (
                          <p className="text-[11px] text-gray-600 py-1.5 px-2.5 italic">
                            No topics at this level yet
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })
            ) : (
              <EmptyState
                icon="📚"
                title="No learning path"
                subtitle="Explore topics to build a personalized learning journey"
              />
            )}
          </>
        )}
      </div>
    </div>
  );
};

const EmptyState = ({ icon, title, subtitle }) => (
  <div className="flex flex-col items-center justify-center py-12 text-center">
    <div className="text-3xl mb-3 opacity-30">{icon}</div>
    <p className="text-xs text-gray-500 font-medium mb-1">{title}</p>
    <p className="text-[10px] text-gray-600 max-w-[200px] leading-relaxed">{subtitle}</p>
  </div>
);

export default RecommendationPanel;