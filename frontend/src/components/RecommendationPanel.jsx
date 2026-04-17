import React, { useState, useEffect } from 'react';
import API_URL from '../services/api';

const RecommendationPanel = ({ currentTopic, recommendations, onTopicSelect }) => {
  const [learningPath, setLearningPath] = useState(null);
  const [activeTab, setActiveTab] = useState('recommendations');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (currentTopic) {
      fetchLearningPath(currentTopic);
    }
  }, [currentTopic]);

  const fetchLearningPath = async (topic) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/graph/learning-path/${encodeURIComponent(topic)}`);
      const data = await response.json();
      setLearningPath(data.learning_path || null);
    } catch (error) {
      console.error('Error fetching learning path:', error);
      setLearningPath(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-xl font-bold bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent mb-2">
          💡 Smart Recommendations
        </h2>
        <p className="text-xs text-gray-400">AI-powered topic suggestions</p>
      </div>

      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setActiveTab('recommendations')}
          className={`px-4 py-2 text-sm rounded-xl font-medium transition-all duration-300 transform hover:scale-105 ${
            activeTab === 'recommendations'
              ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/25'
              : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50 hover:text-white backdrop-blur-sm border border-gray-600/50'
          }`}
        >
          Related Topics
        </button>
        <button
          onClick={() => setActiveTab('learning')}
          className={`px-4 py-2 text-sm rounded-xl font-medium transition-all duration-300 transform hover:scale-105 ${
            activeTab === 'learning'
              ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg shadow-green-500/25'
              : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50 hover:text-white backdrop-blur-sm border border-gray-600/50'
          }`}
        >
          Learning Path
        </button>
      </div>

      <div className="flex-1 overflow-auto space-y-3">
        {activeTab === 'recommendations' && (
          <>
            {recommendations && recommendations.length > 0 ? (
              recommendations.map((rec, idx) => (
                <div
                  key={idx}
                  onClick={() => onTopicSelect(rec.topic)}
                  className="group p-4 bg-gradient-to-br from-gray-700/50 to-gray-800/50 hover:from-gray-600/50 hover:to-gray-700/50 rounded-xl border border-gray-600/30 hover:border-gray-500/50 cursor-pointer transition-all duration-300 transform hover:scale-102 hover:shadow-lg hover:shadow-gray-900/20 backdrop-blur-sm"
                >
                  <div className="font-semibold text-blue-300 group-hover:text-blue-200 transition-colors mb-1">
                    {rec.topic}
                  </div>
                  <div className="text-xs text-gray-400 group-hover:text-gray-300 transition-colors leading-relaxed">
                    {rec.why || `Relevance score: ${(rec.score || 0).toFixed(2)}`}
                  </div>
                  <div className="mt-2 flex items-center gap-2">
                    <div className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      rec.source === 'graph' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' :
                      rec.source === 'ai' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                      'bg-gray-500/20 text-gray-300 border border-gray-500/30'
                    }`}>
                      {rec.source || 'unknown'}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-3">🎯</div>
                <div className="text-sm text-gray-400 mb-2">No recommendations yet</div>
                <div className="text-xs text-gray-500">Ask a question to get AI-powered suggestions!</div>
              </div>
            )}
          </>
        )}

        {activeTab === 'learning' && (
          <>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-6 h-6 border-2 border-green-500/30 border-t-green-500 rounded-full animate-spin"></div>
                <span className="ml-3 text-sm text-gray-400">Generating learning path...</span>
              </div>
            ) : learningPath ? (
              Object.entries(learningPath).map(([level, topics]) => (
                <div key={level} className="mb-4">
                  <h4 className="text-sm font-bold text-green-300 capitalize mb-3 flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      level === 'beginner' ? 'bg-green-400' :
                      level === 'intermediate' ? 'bg-yellow-400' :
                      'bg-red-400'
                    }`}></div>
                    {level} Level
                  </h4>
                  <div className="space-y-2 pl-4 border-l-2 border-gray-600/50">
                    {Array.isArray(topics) && topics.map((topic, idx) => (
                      <button
                        key={idx}
                        onClick={() => onTopicSelect(topic)}
                        className="block text-sm text-gray-300 hover:text-green-300 transition-all duration-200 text-left hover:translate-x-1 p-2 rounded-lg hover:bg-gray-700/30"
                      >
                        • {topic}
                      </button>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-3">📚</div>
                <div className="text-sm text-gray-400 mb-2">No learning path available</div>
                <div className="text-xs text-gray-500">Select a topic to generate a personalized learning journey</div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default RecommendationPanel;