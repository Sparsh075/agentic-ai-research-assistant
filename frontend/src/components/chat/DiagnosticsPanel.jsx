import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

export default function DiagnosticsPanel({ diagnostics }) {
  const [open, setOpen] = useState(false);
  if (!diagnostics) return null;

  const topChunks = diagnostics.top_chunks || [];
  const retrievedChunks =
    diagnostics.retrieved_chunks ?? (topChunks.length > 0 ? topChunks.length : 0);

  return (
    <div className="diagnostics-card">
      <button className="diagnostics-toggle" onClick={() => setOpen((v) => !v)}>
        Diagnostics
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>
      {open && (
        <div className="diagnostics-grid">
          <div>
            <span className="diag-label">Model</span>
            <p>{diagnostics.model || "llama3:8b"}</p>
          </div>
          <div>
            <span className="diag-label">Retrieval time</span>
            <p>{diagnostics.retrieval_time || "n/a"}</p>
          </div>
          <div>
            <span className="diag-label">Chunks</span>
            <p>{retrievedChunks}</p>
          </div>
          <div>
            <span className="diag-label">Token estimate</span>
            <p>{diagnostics.tokens_used || 0}</p>
          </div>
        </div>
      )}
    </div>
  );
}

