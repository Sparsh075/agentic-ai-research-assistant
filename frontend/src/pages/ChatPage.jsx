import { useEffect, useMemo, useRef, useState } from "react";
import ProjectSidebar from "../components/sidebar/ProjectSidebar";
import InspectorPanel from "../components/sidebar/InspectorPanel";
import MessageList from "../components/chat/MessageList";
import ChatComposer from "../components/chat/ChatComposer";
import Toast from "../ui/Toast";
import useGlobalHotkeys from "../hooks/useGlobalHotkeys";
import {
  DEFAULT_AI_SETTINGS,
  createProject,
  createSession,
  fetchDocuments,
  fetchProject,
  fetchProjects,
  fetchLLMConfig,
  fetchSession,
  fetchSessions,
  MODEL_OPTIONS,
  streamAsk,
  uploadPdf,
} from "../services/api";

function estimateTokens(content) {
  return Math.max(1, Math.round(content.trim().split(/\s+/).length * 1.3));
}

export default function ChatPage() {
  const [projects, setProjects] = useState([]);
  const [activeProjectId, setActiveProjectId] = useState(null);
  const [projectDocuments, setProjectDocuments] = useState([]);

  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);

  const [messages, setMessages] = useState([]);
  const [expandedSources, setExpandedSources] = useState({});
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);

  const [uploadState, setUploadState] = useState({ status: "idle", message: "" });
  const [model, setModel] = useState("llama3:8b");
  const [provider, setProvider] = useState("ollama");
  const [modelOptions, setModelOptions] = useState(MODEL_OPTIONS);
  const [aiSettings, setAiSettings] = useState(DEFAULT_AI_SETTINGS);
  const [toast, setToast] = useState("");

  const composerRef = useRef(null);
  const toastTimeoutRef = useRef(null);

  const showToast = (message) => {
    setToast(message);
    window.clearTimeout(toastTimeoutRef.current);
    toastTimeoutRef.current = window.setTimeout(() => setToast(""), 1800);
  };

  useGlobalHotkeys({
    onFocusComposer: () => composerRef.current?.focus(),
  });

  const activeProjectName = useMemo(() => {
    return projects.find((p) => p.id === activeProjectId)?.name || "Project";
  }, [projects, activeProjectId]);

  const loadProjectContext = async (projectId) => {
    const [projectData, sessionList] = await Promise.all([
      fetchProject(projectId),
      fetchSessions(projectId),
    ]);
    setProjectDocuments(projectData?.documents || []);
    setSessions(sessionList || []);
    setActiveSessionId(null);
    setMessages([]);
    setAiSettings(DEFAULT_AI_SETTINGS);
  };

  const loadSessionHistory = async (projectId, sessionId) => {
    const session = await fetchSession(projectId, sessionId);
    setAiSettings({ ...DEFAULT_AI_SETTINGS, ...(session?.settings || {}) });
    const mapped = (session?.messages || []).map((msg, idx) => ({
      id: `${msg.id || idx}`,
      role: msg.role,
      content: msg.content,
      sources: msg.sources || [],
      diagnostics: msg.diagnostics || {},
    }));
    setMessages(mapped);
  };

  useEffect(() => {
    const bootstrap = async () => {
      let existingProjects = await fetchProjects();
      if (existingProjects.length === 0) {
        await createProject("Default Project");
        existingProjects = await fetchProjects();
      }
      setProjects(existingProjects);

      const firstProjectId = existingProjects[0]?.id;
      if (!firstProjectId) return;

      setActiveProjectId(firstProjectId);
      await loadProjectContext(firstProjectId);

      const llmConfig = await fetchLLMConfig();
      const activeProvider = llmConfig?.provider || "ollama";
      const providerModels = llmConfig?.models?.[activeProvider] || MODEL_OPTIONS;
      setProvider(activeProvider);
      setModelOptions(providerModels.length ? providerModels : MODEL_OPTIONS);
      setModel((prev) => (providerModels.includes(prev) ? prev : providerModels[0] || prev));
    };

    bootstrap().catch(() => {
      showToast("Failed to connect backend");
    });

    return () => window.clearTimeout(toastTimeoutRef.current);
  }, []);

  const refreshSessions = async (projectId) => {
    const nextSessions = await fetchSessions(projectId);
    setSessions(nextSessions || []);
  };

  const handleCreateProject = async () => {
    const created = await createProject();
    const nextProjects = await fetchProjects();
    setProjects(nextProjects);
    setActiveProjectId(created.id);
    await loadProjectContext(created.id);
  };

  const handleSwitchProject = async (projectId) => {
    setActiveProjectId(projectId);
    await loadProjectContext(projectId);
  };

  const handleCreateSession = async () => {
    if (!activeProjectId) return;
    const created = await createSession(activeProjectId, "New Session");
    setActiveSessionId(created.id);
    setMessages([]);
    setAiSettings({ ...DEFAULT_AI_SETTINGS, ...(created.settings || {}) });
    await refreshSessions(activeProjectId);
  };

  const ensureSession = async () => {
    if (activeSessionId) return activeSessionId;
    const created = await createSession(activeProjectId, "New Session");
    setActiveSessionId(created.id);
    await refreshSessions(activeProjectId);
    return created.id;
  };

  const sendPrompt = async ({ prompt, regenerateIndex = null }) => {
    if (!prompt.trim() || isStreaming || !activeProjectId) return;

    const sessionId = await ensureSession();
    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: prompt,
      sources: [],
      diagnostics: {},
    };

    const assistantMessageId = crypto.randomUUID();

    if (regenerateIndex !== null) {
      setMessages((prev) => {
        const next = [...prev];
        next[regenerateIndex] = {
          ...next[regenerateIndex],
          id: assistantMessageId,
          content: "",
          sources: [],
          diagnostics: {},
        };
        return next;
      });
    } else {
      setMessages((prev) => [
        ...prev,
        userMessage,
        {
          id: assistantMessageId,
          role: "assistant",
          content: "",
          sources: [],
          diagnostics: {},
        },
      ]);
      setInput("");
    }

    setIsStreaming(true);

    try {
      const stream = await streamAsk({
        projectId: activeProjectId,
        sessionId,
        question: prompt,
        model,
        settings: aiSettings,
      });

      const decoder = new TextDecoder();
      let assistantText = "";
      const targetIndex = regenerateIndex !== null ? regenerateIndex : messages.length + 1;

      const baseDiagnostics = {
        model: stream.diagnostics?.model || model,
        retrieval_time: stream.diagnostics?.retrieval_time || "n/a",
        retrieved_chunks: stream.diagnostics?.retrieved_chunks || (stream.sources || []).length,
        top_chunks: stream.diagnostics?.top_chunks || [],
      };

      while (true) {
        const { value, done } = await stream.reader.read();
        if (done) break;
        assistantText += decoder.decode(value, { stream: true });
        setMessages((prev) => {
          const next = [...prev];
          if (!next[targetIndex]) return prev;
          next[targetIndex] = {
            ...next[targetIndex],
            content: assistantText,
            sources: stream.sources,
            diagnostics: {
              ...baseDiagnostics,
              tokens_used: estimateTokens(assistantText),
              response_time: `${((performance.now() - stream.startedAt) / 1000).toFixed(2)}s`,
            },
          };
          return next;
        });
      }

      await refreshSessions(activeProjectId);
    } catch {
      setMessages((prev) => {
        const next = [...prev];
        const fallbackIndex = regenerateIndex !== null ? regenerateIndex : next.length - 1;
        if (!next[fallbackIndex]) return prev;
        next[fallbackIndex] = {
          ...next[fallbackIndex],
          content: "Backend request failed. Check API and Ollama services.",
          sources: [],
          diagnostics: {},
        };
        return next;
      });
    }

    setIsStreaming(false);
  };

  const handleSend = async () => {
    await sendPrompt({ prompt: input });
  };

  const handleRegenerate = async (assistantIndex) => {
    const question = (() => {
      for (let i = assistantIndex - 1; i >= 0; i -= 1) {
        if (messages[i]?.role === "user") return messages[i].content;
      }
      return "";
    })();

    if (!question) {
      showToast("No source prompt to regenerate");
      return;
    }

    await sendPrompt({ prompt: question, regenerateIndex: assistantIndex });
  };

  const handleCopy = async (content) => {
    try {
      await navigator.clipboard.writeText(content || "");
      showToast("Copied to clipboard");
    } catch {
      showToast("Copy failed");
    }
  };

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file || !activeProjectId) return;

    try {
      setUploadState({ status: "uploading", message: "Indexing document..." });
      await uploadPdf(activeProjectId, file);
      const docs = await fetchDocuments(activeProjectId);
      setProjectDocuments(docs || []);
      setUploadState({ status: "success", message: "Document ready." });
    } catch {
      setUploadState({ status: "error", message: "Upload failed. Try again." });
    }
  };

  const toggleSource = (key) => {
    setExpandedSources((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="app-shell">
      <Toast message={toast} />

      <div className="shell-grid">
        <ProjectSidebar
          projects={projects}
          activeProjectId={activeProjectId}
          sessions={sessions}
          activeSessionId={activeSessionId}
          onCreateProject={handleCreateProject}
          onSwitchProject={handleSwitchProject}
          onCreateSession={handleCreateSession}
          onSelectSession={async (sessionId) => {
            setActiveSessionId(sessionId);
            await loadSessionHistory(activeProjectId, sessionId);
          }}
        />

        <main className="workspace">
          <header className="workspace-header">
            <div>
              <h1>Chat with Research AI</h1>
              <p>{activeProjectName}: an interactive tool for sourcing, drafting, and technical Q&A.</p>
            </div>
            <div className="header-actions">
              <span className="status-dot"></span>
              Live
            </div>
          </header>

          <MessageList
            messages={messages}
            isStreaming={isStreaming}
            expandedSources={expandedSources}
            onToggleSource={toggleSource}
            onCopy={handleCopy}
            onRegenerate={handleRegenerate}
          />

          <ChatComposer
            value={input}
            onChange={setInput}
            onSend={handleSend}
            disabled={isStreaming}
            inputRef={composerRef}
          />
        </main>

        <InspectorPanel
          provider={provider}
          modelOptions={modelOptions}
          model={model}
          onModelChange={setModel}
          aiSettings={aiSettings}
          onSettingsChange={(patch) => setAiSettings((prev) => ({ ...prev, ...patch }))}
          projectDocuments={projectDocuments}
          uploadState={uploadState}
          onUpload={handleUpload}
        />
      </div>
    </div>
  );
}

