// config.js
// -----------
// Defines where the frontend should send API requests.
//
// For local (non-Docker) development, the default below (pointing at the
// Flask dev server on 127.0.0.1:5000) is correct as-is.
//
// In the Docker/Kubernetes image, docker-entrypoint.sh overwrites this
// value at container startup using the API_BASE_URL environment variable,
// so the same image works against any backend address without a rebuild.
window.API_BASE_URL = "http://127.0.0.1:5000/api";
