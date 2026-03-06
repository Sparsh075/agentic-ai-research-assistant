export default function TypingIndicator() {
  return (
    <div className="typing-indicator" aria-live="polite">
      <span className="typing-label">Assistant is typing</span>
      <div className="typing-dots" aria-hidden="true">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  );
}

