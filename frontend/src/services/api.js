import axios from "axios";

const API_URL = "http://127.0.0.1:9000";

export const MODEL_OPTIONS = [
  "llama3:8b",
  "mistral:7b-instruct",
  "deepseek-coder:6.7b",
  "tinyllama",
  "llama-3.3-70b-versatile",
  "llama-3.1-8b-instant",
  "mixtral-8x7b-32768",
];

export const DEFAULT_AI_SETTINGS = {
  temperature: 0.3,
  max_tokens: 256,
  rag_enabled: true,
  top_k: 3,
  fast_mode: false,
};

export const api = axios.create({
  baseURL: API_URL,
});

export async function fetchProjects() {
  const res = await api.get("/projects");
  return res.data || [];
}

export async function createProject(name) {
  const res = await api.post("/projects", { name });
  return res.data;
}

export async function fetchProject(projectId) {
  const res = await api.get(`/projects/${projectId}`);
  return res.data;
}

export async function fetchDocuments(projectId) {
  const res = await api.get(`/projects/${projectId}/documents`);
  return res.data || [];
}

export async function uploadPdf(projectId, file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await api.post(`/projects/${projectId}/upload-pdf`, formData);
  return res.data;
}

export async function fetchSessions(projectId) {
  const res = await api.get(`/projects/${projectId}/sessions`);
  return res.data || [];
}

export async function createSession(projectId, title) {
  const res = await api.post(`/projects/${projectId}/sessions`, { title });
  return res.data;
}

export async function fetchSession(projectId, sessionId) {
  const res = await api.get(`/projects/${projectId}/sessions/${sessionId}`);
  return res.data;
}

export async function fetchLLMConfig() {
  const res = await api.get("/llm-config");
  return res.data;
}

export async function streamAsk({ projectId, sessionId, question, model, settings }) {
  const startedAt = performance.now();
  const response = await fetch(`${API_URL}/projects/${projectId}/ask/${sessionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      model,
      fast: settings.fast_mode,
      settings,
    }),
  });

  if (!response.ok || !response.body) {
    throw new Error(`Stream failed: ${response.status}`);
  }

  const parseHeaderJson = (name, fallback) => {
    try {
      const raw = response.headers.get(name);
      if (!raw) return fallback;
      return JSON.parse(decodeURIComponent(raw));
    } catch {
      return fallback;
    }
  };

  return {
    response,
    reader: response.body.getReader(),
    startedAt,
    sources: parseHeaderJson("X-Sources", []),
    diagnostics: parseHeaderJson("X-Diagnostics", {}),
    document: response.headers.get("X-Document") || "",
  };
}

export default API_URL;

