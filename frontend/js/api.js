/**
 * api.js
 * -------
 * Tiny fetch wrapper shared by every page. Centralizing this here means
 * the backend base URL only needs to change in one place (handy once this
 * moves behind a Kubernetes Ingress / API gateway).
 */

// When the backend is containerized behind a reverse proxy, change this
// to a relative path like "/api". For local dev, Flask runs on :5000.
const API_BASE = window.API_BASE_URL || "http://127.0.0.1:5000/api";

/**
 * Core request helper. Always sends/receives JSON and always includes
 * credentials so the Flask session cookie travels with the request.
 */
async function apiRequest(path, { method = "GET", body } = {}) {
  const options = {
    method,
    credentials: "include",
    headers: {},
  };

  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, options);
  } catch (networkErr) {
    throw new Error("Could not reach the server. Is the backend running?");
  }

  let data = null;
  try {
    data = await response.json();
  } catch (_) {
    // Some endpoints (e.g. a plain 500) may not return JSON.
  }

  if (!response.ok) {
    const message = (data && data.error) || `Request failed (${response.status}).`;
    throw new Error(message);
  }

  return data;
}

const api = {
  get: (path) => apiRequest(path),
  post: (path, body) => apiRequest(path, { method: "POST", body }),
  put: (path, body) => apiRequest(path, { method: "PUT", body }),
  del: (path, body) => apiRequest(path, { method: "DELETE", body }),
};
