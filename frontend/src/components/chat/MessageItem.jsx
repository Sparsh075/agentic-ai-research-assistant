import { Copy, RefreshCw } from "lucide-react";
import DiagnosticsPanel from "./DiagnosticsPanel";
import SourceCards from "./SourceCards";
import TopicChips from "./TopicChips";

function formatMeta(message) {
  const model = message.diagnostics?.model || "llama3:8b";
  const responseTime = message.diagnostics?.response_time || "-";
  const tokens = message.diagnostics?.tokens_used || 0;
  return `${model} • ${responseTime} • ~${tokens} tokens`;
}

export default function MessageItem({
  message,
  index,
  expandedSources,
  onToggleSource,
  onCopy,
  onRegenerate,
  onTopicClick = () => {},
}) {
  const isAssistant = message.role === "assistant";
  const topics = message.topics || [];

  return (
    <div className={`bubble fade-in ${message.role === "user" ? "user" : "assistant"}`}>
      <div className="bubble-head">
        <div className="bubble-role">{message.role === "user" ? "You" : "Assistant"}</div>
        {isAssistant && (
          <div className="bubble-actions">
            <button className="icon-btn" onClick={() => onCopy(message.content)} title="Copy response">
              <Copy size={14} />
            </button>
            <button
              className="icon-btn"
              onClick={() => onRegenerate(index)}
              title="Regenerate response"
            >
              <RefreshCw size={14} />
            </button>
          </div>
        )}
      </div>

      <div className="bubble-content">{message.content}</div>

      {isAssistant && topics.length > 0 && (
        <TopicChips topics={topics} onTopicClick={onTopicClick} />
      )}

      {isAssistant && <div className="meta-badge">{formatMeta(message)}</div>}

      {isAssistant && (
        <SourceCards
          messageId={message.id || index}
          sources={message.sources || []}
          expandedSources={expandedSources}
          onToggle={onToggleSource}
        />
      )}

      {isAssistant && <DiagnosticsPanel diagnostics={message.diagnostics} />}
    </div>
  );
}

