"use client";

import { useState, useEffect, useCallback } from "react";
import IssueCard from "@/components/IssueCard";
import { getIssues, getLanguages } from "@/lib/api";

export default function IssuesPage() {
    const [issues, setIssues] = useState([]);
    const [pagination, setPagination] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [languages, setLanguages] = useState([]);

    const [search, setSearch] = useState("");
    const [language, setLanguage] = useState("");
    const [difficulty, setDifficulty] = useState("");
    const [page, setPage] = useState(1);

    const fetchIssues = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getIssues({
                search: search || undefined,
                language: language || undefined,
                difficulty: difficulty || undefined,
                is_assigned: false,
                page,
                per_page: 20,
            });
            setIssues(data.data || []);
            setPagination(data.pagination || null);
        } catch (err) {
            setError(err.message);
            setIssues([]);
        } finally {
            setLoading(false);
        }
    }, [search, language, difficulty, page]);

    useEffect(() => {
        fetchIssues();
    }, [fetchIssues]);

    useEffect(() => {
        getLanguages()
            .then((data) => setLanguages(Array.isArray(data) ? data : []))
            .catch(() => setLanguages([]));
    }, []);

    useEffect(() => {
        setPage(1);
    }, [search, language, difficulty]);

    return (
        <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-white sm:text-3xl">
                    Find Issues
                </h1>
                <p className="mt-1.5 text-sm text-gray-500">
                    Browse good-first-issues across all tracked repositories. Only unassigned issues shown.
                </p>
            </div>

            {/* Filters */}
            <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
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
                        placeholder="Search issues..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full rounded-xl border border-white/[0.08] bg-white/[0.03] py-2.5 pl-10 pr-4 text-sm text-white placeholder-gray-500 outline-none focus:border-violet-500/40 focus:ring-1 focus:ring-violet-500/20 transition-all"
                    />
                </div>

                <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="rounded-xl border border-white/[0.08] bg-[#0d0d14] py-2.5 px-3 text-sm text-gray-300 outline-none focus:border-violet-500/40 cursor-pointer"
                >
                    <option value="">All Languages</option>
                    {languages.map((l) => (
                        <option key={l.language} value={l.language}>
                            {l.language}
                        </option>
                    ))}
                </select>

                <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="rounded-xl border border-white/[0.08] bg-[#0d0d14] py-2.5 px-3 text-sm text-gray-300 outline-none focus:border-violet-500/40 cursor-pointer"
                >
                    <option value="">All Difficulty</option>
                    <option value="easy">🟢 Easy</option>
                    <option value="medium">🟡 Medium</option>
                    <option value="hard">🔴 Hard</option>
                </select>
            </div>

            {/* Content */}
            {loading ? (
                <div className="space-y-3">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="skeleton h-28" />
                    ))}
                </div>
            ) : error ? (
                <div className="rounded-2xl border border-red-500/20 bg-red-500/[0.05] p-8 text-center">
                    <p className="text-sm text-red-400">{error}</p>
                    <button
                        onClick={fetchIssues}
                        className="mt-3 rounded-lg bg-red-500/20 px-4 py-1.5 text-xs text-red-300 hover:bg-red-500/30 transition-colors"
                    >
                        Retry
                    </button>
                </div>
            ) : issues.length === 0 ? (
                <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-12 text-center">
                    <p className="text-sm text-gray-500">No issues found. Try adjusting your filters.</p>
                </div>
            ) : (
                <>
                    <div className="space-y-3">
                        {issues.map((issue) => (
                            <IssueCard key={issue.id} issue={issue} showRepo />
                        ))}
                    </div>

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
                                onClick={() => setPage((p) => Math.min(pagination.total_pages, p + 1))}
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
