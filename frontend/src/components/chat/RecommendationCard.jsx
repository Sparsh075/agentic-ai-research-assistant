import React from 'react';

export default function RecommendationCard({ recommendation, onClick }) {
  const { topic, score = 0, explanation = '', source = 'unknown' } = recommendation || {};

  if (!topic) return null;

  const sourceColor = {
    'graph': 'from-blue-600 to-blue-800',
    'ai': 'from-purple-600 to-purple-800',
    'popular': 'from-green-600 to-green-800',
    'fallback': 'from-gray-600 to-gray-800'
  };

  const bg = sourceColor[source] || sourceColor.fallback;

  return (
    <div
      onClick={onClick}
      className={`
        p-4 rounded-lg cursor-pointer
        bg-gradient-to-br ${bg}
        border border-white/10
        hover:border-white/30
        hover:shadow-lg hover:shadow-red-500/20
        transform hover:scale-105 hover:-translate-y-1
        transition-all duration-300
        backdrop-blur-sm
        group
      `}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className="text-sm font-bold text-white capitalize group-hover:text-red-300 transition-colors">
            {topic}
          </h4>
          <p className="text-xs text-gray-300 mt-1 line-clamp-2">
            {explanation}
          </p>
        </div>
        <span className="ml-2 text-xs font-semibold text-white/70 whitespace-nowrap">
          {(score * 100).toFixed(0)}%
        </span>
      </div>

      <div className="mt-3 flex items-center justify-between">
        <div className="flex-1 bg-white/10 rounded-full h-1.5 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-red-400 to-red-600 rounded-full transition-all duration-500"
            style={{ width: `${Math.min(100, (score * 100))}%` }}
          />
        </div>
        <span className="ml-2 text-xs text-white/60 font-mono uppercase">
          {source}
        </span>
      </div>
    </div>
  );
}
