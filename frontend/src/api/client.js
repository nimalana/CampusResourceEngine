const BASE = "/api";

async function apiFetch(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(`API error ${res.status}: ${msg}`);
  }
  return res.json();
}

export const api = {
  getCourses: () => apiFetch("/courses"),
  getCourse: (id) => apiFetch(`/courses/${id}`),

  getClubs: () => apiFetch("/clubs"),
  getClub: (id) => apiFetch(`/clubs/${id}`),

  getResearch: () => apiFetch("/research"),
  getResearchProject: (id) => apiFetch(`/research/${id}`),

  getEvents: () => apiFetch("/events"),
  getEvent: (id) => apiFetch(`/events/${id}`),

  getDining: () => apiFetch("/dining"),
  getDiningLocation: (id) => apiFetch(`/dining/${id}`),

  search: (q) => apiFetch(`/search?q=${encodeURIComponent(q)}`),

  getStats: () => apiFetch("/stats"),
  getRing: () => apiFetch("/stats/ring"),
  getHealth: () => apiFetch("/health"),
};
