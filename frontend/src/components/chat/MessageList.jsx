import { useEffect, useRef } from "react";
import TypingIndicator from "./TypingIndicator";
import MessageItem from "./MessageItem";

export default function MessageList({
  messages,
  isStreaming,
  expandedSources,
  onToggleSource,
  onCopy,
  onRegenerate,
  onTopicClick = () => {},
}) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isStreaming]);

  return (
    <section className="chat-window">
      <div className="chat-title">
        <div className="chat-pill">Query</div>
      </div>

      {messages.length === 0 && (
        <div className="empty-state">Ask: "Summarize the core contribution in two sentences."</div>
      )}

      {messages.map((message, index) => (
        <MessageItem
          key={message.id || index}
          message={message}
          index={index}
          expandedSources={expandedSources}
          onToggleSource={onToggleSource}
          onCopy={onCopy}
          onRegenerate={onRegenerate}
          onTopicClick={onTopicClick}
        />
      ))}

      {isStreaming && <TypingIndicator />}
      <div ref={endRef} />
    </section>
  );
}

