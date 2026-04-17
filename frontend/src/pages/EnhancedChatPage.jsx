import { useEffect, useMemo, useRef, useState } from "react";
import ProjectSidebar from "../components/sidebar/ProjectSidebar";
import InspectorPanel from "../components/sidebar/InspectorPanel";
import MessageList from "../components/chat/MessageList";
import ChatComposer from "../components/chat/ChatComposer";
import GraphVisualization from "../components/GraphVisualization";
import RecommendationPanel from "../components/RecommendationPanel";
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

export default function EnhancedChatPage() {
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

  // New state for enhanced features
  const [currentTopic, setCurrentTopic] = useState("");
  const [showGraph, setShowGraph] = useState(false);
  const [showRecommendations, setShowRecommendations] = useState(true);

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
    };

    bootstrap();
  }, []);

  const handleSendMessage = async (messageText, settings) => {
    if (!activeProjectId || !activeSessionId) return;

    setIsStreaming(true);
    const userMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: messageText,
      sources: [],
      diagnostics: {},
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      // Use the new enhanced query endpoint
      const response = await fetch('/api/query/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: messageText,
          model: model,
          use_cache: true
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      // Update current topic from extracted topics
      if (data.topics && data.topics.length > 0) {
        setCurrentTopic(data.topics[0]);
      }

      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.response,
        sources: [],
        diagnostics: {},
        topics: data.topics || [],
        recommendations: data.recommendations || []
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Also send to original endpoint for session persistence
      await streamAsk(
        activeProjectId,
        activeSessionId,
        {
          question: messageText,
          model: model,
          settings: settings,
        },
        (token) => {
          // Handle streaming if needed
        }
      );

    } catch (error) {
      console.error("Error sending message:", error);
      showToast("Failed to send message. Please try again.");
    } finally {
      setIsStreaming(false);
    }
  };

  const handleTopicSelect = (topic) => {
    setCurrentTopic(topic);
    setInput(`Tell me about ${topic}`);
    composerRef.current?.focus();
  };

  const toggleGraph = () => {
    setShowGraph(!showGraph);
  };

  const toggleRecommendations = () => {
    setShowRecommendations(!showRecommendations);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <ProjectSidebar
        projects={projects}
        activeProjectId={activeProjectId}
        onProjectSelect={async (projectId) => {
          setActiveProjectId(projectId);
          await loadProjectContext(projectId);
        }}
        onCreateProject={async (name) => {
          const newProject = await createProject(name);
          setProjects((prev) => [...prev, newProject]);
          setActiveProjectId(newProject.id);
          await loadProjectContext(newProject.id);
        }}
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSessionSelect={async (sessionId) => {
          setActiveSessionId(sessionId);
          await loadSessionHistory(activeProjectId, sessionId);
        }}
        onCreateSession={async (title) => {
          const newSession = await createSession(activeProjectId, { title });
          setSessions((prev) => [...prev, newSession]);
          setActiveSessionId(newSession.id);
          setMessages([]);
        }}
      />

      <div className="flex-1 flex flex-col">
        <div className="flex-1 flex">
          <div className="flex-1 flex flex-col">
            <div className="flex items-center justify-between p-4 border-b bg-white">
              <h1 className="text-xl font-semibold">{activeProjectName}</h1>
              <div className="flex items-center space-x-2">
                <button
                  onClick={toggleGraph}
                  className={`px-3 py-1 text-sm rounded ${
                    showGraph ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  Knowledge Graph
                </button>
                <button
                  onClick={toggleRecommendations}
                  className={`px-3 py-1 text-sm rounded ${
                    showRecommendations ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  Recommendations
                </button>
              </div>
            </div>

            <div className="flex-1 flex">
              {showGraph && (
                <div className="w-1/2 border-r bg-white">
                  <GraphVisualization
                    topic={currentTopic}
                    onTopicClick={handleTopicSelect}
                  />
                </div>
              )}

              <div className={`${showGraph ? 'w-1/2' : 'w-full'} flex flex-col`}>
                <div className="flex-1 overflow-hidden">
                  <MessageList
                    messages={messages}
                    expandedSources={expandedSources}
                    onToggleSource={(id) =>
                      setExpandedSources((prev) => ({
                        ...prev,
                        [id]: !prev[id],
                      }))
                    }
                  />
                </div>

                <ChatComposer
                  ref={composerRef}
                  input={input}
                  setInput={setInput}
                  onSend={handleSendMessage}
                  isStreaming={isStreaming}
                  model={model}
                  setModel={setModel}
                  modelOptions={modelOptions}
                  aiSettings={aiSettings}
                  setAiSettings={setAiSettings}
                  disabled={!activeSessionId}
                />
              </div>
            </div>
          </div>

          {showRecommendations && (
            <div className="w-80 border-l bg-gray-50">
              <RecommendationPanel
                currentTopic={currentTopic}
                onTopicSelect={handleTopicSelect}
              />
            </div>
          )}
        </div>
      </div>

      <InspectorPanel
        projectDocuments={projectDocuments}
        onUpload={async (file) => {
          setUploadState({ status: "uploading", message: "Uploading PDF..." });
          try {
            await uploadPdf(activeProjectId, file);
            const updatedDocuments = await fetchDocuments(activeProjectId);
            setProjectDocuments(updatedDocuments);
            setUploadState({ status: "success", message: "PDF uploaded successfully!" });
            showToast("PDF uploaded successfully!");
          } catch (error) {
            setUploadState({ status: "error", message: "Failed to upload PDF" });
            showToast("Failed to upload PDF");
          }
        }}
        uploadState={uploadState}
      />

      {toast && <Toast message={toast} />}
    </div>
  );
}