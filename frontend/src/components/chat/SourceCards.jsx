import { ChevronDown, ChevronUp } from "lucide-react";

export default function SourceCards({ messageId, sources, expandedSources, onToggle }) {
  if (!sources?.length) return null;

  return (
    <div className="source-section">
      <p className="source-title">Sources</p>
      {sources.map((source, srcIdx) => {
        const key = `${messageId}_${srcIdx}`;
        const expanded = !!expandedSources[key];
        return (
          <div key={key} className="source-card">
            <div className="source-head">
              <span className="source-doc">{source.document || "Uploaded PDF"}</span>
              <span className="source-meta">
                Page {source.page_number} | Score {source.score}
              </span>
            </div>
            <button className="source-toggle" onClick={() => onToggle(key)}>
              {expanded ? (
                <>
                  Hide snippet <ChevronUp size={14} />
                </>
              ) : (
                <>
                  Show snippet <ChevronDown size={14} />
                </>
              )}
            </button>
            {expanded && <p className="source-snippet">{source.snippet}</p>}
          </div>
        );
      })}
    </div>
  );
}

