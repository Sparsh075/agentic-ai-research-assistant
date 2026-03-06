import { Send } from "lucide-react";
import { useRef } from "react";
import useAutosizeTextarea from "../../hooks/useAutosizeTextarea";

export default function ChatComposer({ value, onChange, onSend, disabled, inputRef }) {
  const localRef = useRef(null);
  const textareaRef = inputRef || localRef;
  useAutosizeTextarea(textareaRef, value);

  return (
    <section className="composer">
      <div className="composer-left">
        <span className="chip">RAG</span>
        <span className="chip">Project scoped</span>
      </div>
      <div className="composer-right">
        <textarea
          ref={textareaRef}
          className="composer-textarea"
          placeholder="Write your request..."
          rows={1}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
        />
        <button onClick={onSend} disabled={disabled} title="Send">
          <Send size={16} />
        </button>
      </div>
    </section>
  );
}

