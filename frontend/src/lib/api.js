const IS_SERVER = typeof window === "undefined";
const API_BASE = IS_SERVER
    ? process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    : "/api";

async function apiFetch(endpoint, options = {}) {
    const { revalidate, ...fetchOptions } = options;

    const res = await fetch(`${API_BASE}${endpoint}`, {
        ...fetchOptions,
        headers: {
            "Content-Type": "application/json",
            ...fetchOptions?.headers,
        },
        next: revalidate !== undefined ? { revalidate } : undefined,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ error: res.statusText }));
        throw new Error(error.error || `API error: ${res.status}`);
    }

    return res.json();
}


export async function getRepositories(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") {
            query.set(key, String(value));
        }
    });
    const qs = query.toString();
    return apiFetch(`/v1/repositories${qs ? `?${qs}` : ""}`, {
        revalidate: 900,
    });
}

export async function getRepository(id) {
    return apiFetch(`/v1/repositories/${id}`, { revalidate: 900 });
}

export async function getRepositoryIssues(id, page = 1) {
    return apiFetch(`/v1/repositories/${id}/issues?page=${page}`, {
        revalidate: 900,
    });
}

export async function getMetricsHistory(id) {
    return apiFetch(`/v1/repositories/${id}/metrics-history`, {
        revalidate: 3600,
    });
}


export async function getIssues(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") {
            query.set(key, String(value));
        }
    });
    const qs = query.toString();
    return apiFetch(`/v1/issues${qs ? `?${qs}` : ""}`, { revalidate: 900 });
}


export async function getStats() {
    return apiFetch("/v1/stats", { revalidate: 3600 });
}

export async function getLanguages() {
    return apiFetch("/v1/languages", { revalidate: 86400 });
}


export async function liveSearchRepos(query) {
    return apiFetch(
        `/v1/repositories/live-search?q=${encodeURIComponent(query)}&per_page=10`
    );
}
