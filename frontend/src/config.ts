const sanitize = (url: string) => url.replace(/\/$/, "");

const inferBaseUrl = () => {
  if (typeof window !== "undefined" && window.location.hostname) {
    return `http://${window.location.hostname}:8000`;
  }
  return "http://127.0.0.1:8000";
};

const rawBaseUrl = import.meta.env.VITE_BACKEND_URL as string | undefined;

export const BASE_URL = sanitize(rawBaseUrl?.trim() || inferBaseUrl());
