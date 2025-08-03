// src/apiBase.js

export const getApiBase = () => {
  const isLocalhost = window.location.hostname === "localhost";

  return isLocalhost
    ? "http://localhost:8086"         // For local development
    : "http://43.204.171.199:8086";   // For deployed live backend
};
