import { FileText, Upload } from "lucide-react";

export default function InspectorPanel({
  provider,
  modelOptions,
  model,
  onModelChange,
  aiSettings,
  onSettingsChange,
  projectDocuments,
  uploadState,
  onUpload,
}) {
  return (
    <aside className="inspector">
      <div className="panel">
        <div className="panel-header">
          <p>AI Module</p>
          <button className="panel-pill">{provider?.toUpperCase?.() || "LOCAL"}</button>
        </div>
        <div className="panel-tabs">
          <button className="tab active">Tools</button>
          <button className="tab">Files</button>
        </div>

        <div className="panel-body">
          <p className="panel-title">Model</p>
          <select className="model-select" value={model} onChange={(e) => onModelChange(e.target.value)}>
            {(modelOptions || []).map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>

          <div className="advanced-settings">
            <p className="panel-title">Advanced AI Settings</p>

            <div className="setting-row">
              <div className="setting-head">
                <span>Temperature</span>
                <span>{aiSettings.temperature.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={aiSettings.temperature}
                onChange={(e) => onSettingsChange({ temperature: parseFloat(e.target.value) })}
              />
            </div>

            <div className="setting-row">
              <div className="setting-head">
                <span>Max tokens</span>
                <span>{aiSettings.max_tokens}</span>
              </div>
              <input
                type="range"
                min="32"
                max="1024"
                step="32"
                value={aiSettings.max_tokens}
                onChange={(e) => onSettingsChange({ max_tokens: parseInt(e.target.value, 10) })}
              />
            </div>

            <div className="toggle-row">
              <div className="toggle-label">RAG enabled</div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={aiSettings.rag_enabled}
                  onChange={(e) => onSettingsChange({ rag_enabled: e.target.checked })}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-row">
              <div className="setting-head">
                <span>Retrieval top_k</span>
                <span>{aiSettings.top_k}</span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                step="1"
                value={aiSettings.top_k}
                disabled={!aiSettings.rag_enabled}
                onChange={(e) => onSettingsChange({ top_k: parseInt(e.target.value, 10) })}
              />
            </div>

            <div className="toggle-row">
              <div className="toggle-label">Fast mode</div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={aiSettings.fast_mode}
                  onChange={(e) => onSettingsChange({ fast_mode: e.target.checked })}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>

          <p className="panel-title">Project Documents</p>
          {projectDocuments.length > 0 ? (
            <div className="documents-list">
              {projectDocuments.map((doc) => (
                <div className="file-card" key={doc.id}>
                  <FileText size={16} />
                  <div>
                    <p>{doc.filename}</p>
                    <span>{doc.uploaded_at}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="panel-muted">No document indexed for this project.</p>
          )}

          <label className="upload-card">
            <div>
              <p>Upload PDF</p>
              <span>Drag or click to index</span>
            </div>
            <Upload size={16} />
            <input type="file" hidden onChange={onUpload} />
          </label>

          {uploadState.status !== "idle" && <div className={`status-pill ${uploadState.status}`}>{uploadState.message}</div>}
        </div>
      </div>
    </aside>
  );
}
