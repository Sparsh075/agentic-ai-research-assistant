import { LayoutGrid, Library, MessageSquare, Plus, Search, Settings, Sparkles } from "lucide-react";

export default function ProjectSidebar({
  projects,
  activeProjectId,
  sessions,
  activeSessionId,
  onCreateProject,
  onSwitchProject,
  onCreateSession,
  onSelectSession,
}) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <Sparkles size={16} />
        </div>
        <div>
          <p className="brand-title">Query</p>
          <p className="brand-subtitle">Research Console</p>
        </div>
      </div>

      <div className="history-header">
        <p className="nav-label">Project</p>
        <button className="new-chat-btn" onClick={onCreateProject}>
          <Plus size={12} />
          New
        </button>
      </div>

      <select className="model-select" value={activeProjectId || ""} onChange={(e) => onSwitchProject(e.target.value)}>
        {projects.map((project) => (
          <option key={project.id} value={project.id}>
            {project.name}
          </option>
        ))}
      </select>

      <div className="search-box">
        <Search size={14} />
        <input type="text" placeholder="Search sessions" />
      </div>

      <div className="nav-section">
        <p className="nav-label">Features</p>
        <button className="nav-item active">
          <LayoutGrid size={16} />
          Dashboard
        </button>
        <button className="nav-item">
          <MessageSquare size={16} />
          AI Chat
        </button>
        <button className="nav-item">
          <Library size={16} />
          Library
        </button>
        <button className="nav-item">
          <Settings size={16} />
          Settings
        </button>
      </div>

      <div className="history">
        <div className="history-header">
          <p className="nav-label">Sessions</p>
          <button className="new-chat-btn" onClick={onCreateSession}>
            <Plus size={12} />
            New
          </button>
        </div>

        {sessions.length === 0 && <div className="history-empty">No sessions yet.</div>}

        {sessions.map((session) => (
          <button
            key={session.id}
            className={`history-item session-item ${activeSessionId === session.id ? "active" : ""}`}
            onClick={() => onSelectSession(session.id)}
          >
            <div>
              <p>{session.title}</p>
              <span>{session.message_count} messages</span>
            </div>
          </button>
        ))}
      </div>
    </aside>
  );
}

