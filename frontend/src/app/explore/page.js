"use client";

import { useState, useEffect, useCallback } from "react";
import RepoCard from "@/components/RepoCard";
import { getRepositories, getLanguages, liveSearchRepos } from "@/lib/api";

const SORT_OPTIONS = [
    { value: "combined_score", label: "Best Match" },
    { value: "activity_score", label: "Most Active" },
    { value: "beginner_friendliness_score", label: "Most Friendly" },
    { value: "stars", label: "Most Stars" },
    { value: "last_commit_at", label: "Recently Updated" },
];

export default function ExplorePage() {
    const [repos, setRepos] = useState([]);
    const [pagination, setPagination] = useState(null);
    const [loading, setLoading] = useState(true);
    const [liveSearching, setLiveSearching] = useState(false);
    const [liveSource, setLiveSource] = useState(false);
    const [error, setError] = useState(null);
    const [languages, setLanguages] = useState([]);

    const [search, setSearch] = useState("");
    const [language, setLanguage] = useState("");
    const [sortBy, setSortBy] = useState("combined_score");
    const [hasIssues, setHasIssues] = useState(true);
    const [activelyMerging, setActivelyMerging] = useState(false);
    const [page, setPage] = useState(1);

    const fetchRepos = useCallback(async () => {
        setLoading(true);
        setError(null);
        setLiveSource(false);
        try {
            const data = await getRepositories({
                search: search || undefined,
                language: language || undefined,
                sort_by: sortBy,
                has_issues: hasIssues || undefined,
                actively_merging: activelyMerging || undefined,
                page,
                per_page: 12,
            });
            const results = data.data || [];
            setRepos(results);
            setPagination(data.pagination || null);

            if (results.length === 0 && search && search.length >= 2) {
                setLiveSearching(true);
                try {
                    const liveData = await liveSearchRepos(search);
                    const liveResults = liveData.data || [];
                    if (liveResults.length > 0) {
                        setRepos(liveResults);
                        setLiveSource(true);
                        setPagination(null);
                    }
                } catch (liveErr) {
                    console.warn("Live search failed:", liveErr);
                } finally {
                    setLiveSearching(false);
                }
            }
        } catch (err) {
            setError(err.message);
            setRepos([]);
        } finally {
            setLoading(false);
        }
    }, [search, language, sortBy, hasIssues, activelyMerging, page]);

    useEffect(() => {
        fetchRepos();
    }, [fetchRepos]);

    useEffect(() => {
        getLanguages()
            .then((data) => setLanguages(Array.isArray(data) ? data : []))
            .catch(() => setLanguages([]));
    }, []);

    useEffect(() => {
        setPage(1);
    }, [search, language, sortBy, hasIssues, activelyMerging]);

    return (
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-white sm:text-3xl">
                    Explore Projects
                </h1>
                <p className="mt-1.5 text-sm text-gray-500">
                    Discover beginner-friendly open source repositories with real metrics.
                </p>
            </div>

            {/* Filters */}
            <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
                {/* Search */}
                <div className="relative flex-1">
                    <svg
                        className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
                        />
                    </svg>
                    <input
                        type="text"
                        placeholder="Search projects... (searches GitHub if not found locally)"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full rounded-xl border border-white/[0.08] bg-white/[0.03] py-2.5 pl-10 pr-4 text-sm text-white placeholder-gray-500 outline-none focus:border-violet-500/40 focus:ring-1 focus:ring-violet-500/20 transition-all"
                    />
                </div>

                {/* Language */}
                <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="rounded-xl border border-white/[0.08] bg-[#0d0d14] py-2.5 px-3 text-sm text-gray-300 outline-none focus:border-violet-500/40 cursor-pointer"
                >
                    <option value="">All Languages</option>
                    {languages.map((l) => (
                        <option key={l.language} value={l.language}>
                            {l.language} ({l.repo_count})
                        </option>
                    ))}
                </select>

                {/* Sort */}
                <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="rounded-xl border border-white/[0.08] bg-[#0d0d14] py-2.5 px-3 text-sm text-gray-300 outline-none focus:border-violet-500/40 cursor-pointer"
                >
                    {SORT_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                            {opt.label}
                        </option>
                    ))}
                </select>

                {/* GFI toggle */}
                <label className="flex items-center gap-2 text-sm text-gray-400 cursor-pointer whitespace-nowrap">
                    <input
                        type="checkbox"
                        checked={hasIssues}
                        onChange={(e) => setHasIssues(e.target.checked)}
                        className="h-4 w-4 rounded border-white/20 bg-transparent accent-violet-500"
                    />
                    Has GFIs
                </label>

                {/* Active & Merging toggle */}
                <label className="flex items-center gap-2 text-sm text-gray-400 cursor-pointer whitespace-nowrap">
                    <input
                        type="checkbox"
                        checked={activelyMerging}
                        onChange={(e) => setActivelyMerging(e.target.checked)}
                        className="h-4 w-4 rounded border-white/20 bg-transparent accent-emerald-500"
                    />
                    Active &amp; Merging
                </label>
            </div>

            {/* Content */}
            {loading || liveSearching ? (
                <div>
                    {liveSearching && (
                        <div className="mb-4 flex items-center gap-2 rounded-xl border border-violet-500/20 bg-violet-500/[0.05] px-4 py-3">
                            <svg className="h-4 w-4 animate-spin text-violet-400" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                            <span className="text-sm text-violet-300">
                                Not found locally, searching GitHub...
                            </span>
                        </div>
                    )}
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                        {Array.from({ length: 6 }).map((_, i) => (
                            <div key={i} className="skeleton h-72" />
                        ))}
                    </div>
                </div>
            ) : error ? (
                <div className="rounded-2xl border border-red-500/20 bg-red-500/[0.05] p-8 text-center">
                    <p className="text-sm text-red-400">{error}</p>
                    <button
                        onClick={fetchRepos}
                        className="mt-3 rounded-lg bg-red-500/20 px-4 py-1.5 text-xs text-red-300 hover:bg-red-500/30 transition-colors"
                    >
                        Retry
                    </button>
                </div>
            ) : repos.length === 0 ? (
                <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-12 text-center">
                    <p className="text-sm text-gray-500">
                        No repositories found. Try adjusting your filters.
                    </p>
                </div>
            ) : (
                <>
                    {/* Live source banner */}
                    {liveSource && (
                        <div className="mb-4 flex items-center gap-2 rounded-xl border border-emerald-500/20 bg-emerald-500/[0.05] px-4 py-3">
                            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                            <span className="text-sm text-emerald-300">
                                Fetched live from GitHub — these repos are now saved to your database!
                            </span>
                        </div>
                    )}

                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                        {repos.map((repo) => (
                            <RepoCard key={repo.id} repo={repo} />
                        ))}
                    </div>

                    {/* Pagination */}
                    {pagination && pagination.total_pages > 1 && (
                        <div className="mt-8 flex items-center justify-center gap-2">
                            <button
                                onClick={() => setPage((p) => Math.max(1, p - 1))}
                                disabled={page <= 1}
                                className="rounded-lg border border-white/[0.08] bg-white/[0.03] px-3.5 py-2 text-xs text-gray-400 hover:text-white hover:bg-white/[0.06] disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                            >
                                Previous
                            </button>
                            <span className="px-3 text-xs text-gray-500">
                                Page {pagination.page} of {pagination.total_pages}
                            </span>
                            <button
                                onClick={() =>
                                    setPage((p) => Math.min(pagination.total_pages, p + 1))
                                }
                                disabled={page >= pagination.total_pages}
                                className="rounded-lg border border-white/[0.08] bg-white/[0.03] px-3.5 py-2 text-xs text-gray-400 hover:text-white hover:bg-white/[0.06] disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                            >
                                Next
                            </button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
