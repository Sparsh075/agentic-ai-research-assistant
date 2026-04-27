import React from 'react';

export default function TopicChips({ topics = [], onTopicClick = () => {} }) {
  if (!topics || topics.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {topics.map((topic, idx) => (
        <button
          key={idx}
          onClick={() => onTopicClick(topic)}
          className="px-3 py-1 text-xs font-semibold rounded-full 
            bg-gradient-to-r from-red-500/30 to-blue-500/30
            border border-red-400/50
            text-red-200
            hover:from-red-500/50 hover:to-blue-500/50
            hover:border-red-300/70
            hover:text-red-100
            hover:shadow-lg hover:shadow-red-500/20
            transition-all duration-200
            backdrop-blur-sm
            cursor-pointer"
        >
          #{topic}
        </button>
      ))}
    </div>
  );
}
