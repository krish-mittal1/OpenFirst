"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getRepository } from "@/lib/api";
import { formatNumber, getScoreInfo, timeAgo } from "@/lib/utils";
import ScoreGauge from "@/components/ui/ScoreGauge";
import MetricCard from "@/components/ui/MetricCard";
import IssueCard from "@/components/IssueCard";

export default function RepoDetailPage() {
    const params = useParams();
    const [repo, setRepo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!params.id) return;
        setLoading(true);
        getRepository(Number(params.id))
            .then((data) => setRepo(data))
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false));
    }, [params.id]);

    if (loading) {
        return (
            <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
                <div className="skeleton h-8 w-64 mb-4" />
                <div className="skeleton h-4 w-96 mb-8" />
                <div className="grid grid-cols-3 gap-4 mb-8">
                    <div className="skeleton h-32" />
                    <div className="skeleton h-32" />
                    <div className="skeleton h-32" />
                </div>
                <div className="space-y-3">
                    <div className="skeleton h-20" />
                    <div className="skeleton h-20" />
                    <div className="skeleton h-20" />
                </div>
            </div>
        );
    }

    if (error || !repo) {
        return (
            <div className="mx-auto max-w-5xl px-4 py-16 text-center">
                <p className="text-sm text-red-400">{error || "Repository not found"}</p>
                <Link
                    href="/explore"
                    className="mt-4 inline-block text-sm text-violet-400 hover:text-violet-300"
                >
                    ← Back to Explore
                </Link>
            </div>
        );
    }

    const combinedInfo = getScoreInfo(repo.scores?.combined || 0);

    return (
        <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
            {/* Breadcrumb */}
            <div className="mb-6 flex items-center gap-2 text-xs text-gray-500">
                <Link href="/explore" className="hover:text-white transition-colors">
                    Explore
                </Link>
                <span>/</span>
                <span className="text-gray-300">{repo.full_name}</span>
            </div>

            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-white sm:text-3xl">
                        {repo.full_name}
                    </h1>
                    <p className="mt-2 text-sm text-gray-400 max-w-2xl leading-relaxed">
                        {repo.description || "No description available."}
                    </p>
                    {/* Tags */}
                    <div className="flex flex-wrap items-center gap-2 mt-3">
                        {repo.primary_language && (
                            <span className="inline-flex items-center gap-1.5 rounded-md bg-violet-500/10 px-2.5 py-1 text-xs text-violet-300">
                                <span className="h-2 w-2 rounded-full bg-violet-400" />
                                {repo.primary_language}
                            </span>
                        )}
                        {repo.license && (
                            <span className="rounded-md bg-white/[0.06] px-2.5 py-1 text-xs text-gray-400">
                                {repo.license}
                            </span>
                        )}
                        {repo.topics?.map((t) => (
                            <span
                                key={t}
                                className="rounded-md bg-white/[0.04] px-2 py-0.5 text-[11px] text-gray-500"
                            >
                                {t}
                            </span>
                        ))}
                    </div>
                </div>

                <a
                    href={`https://github.com/${repo.full_name}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="shrink-0 inline-flex items-center gap-2 rounded-xl border border-white/[0.1] bg-white/[0.03] px-4 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-white/[0.06] transition-all"
                >
                    <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                    </svg>
                    View on GitHub
                </a>
            </div>

            {/* Scores */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
                <div className="rounded-2xl border border-white/[0.06] bg-[#0d0d14] p-6 flex flex-col items-center">
                    <ScoreGauge score={repo.scores?.activity || 0} label="Activity Score" size={90} />
                    <p className="mt-2 text-xs text-gray-500">How actively maintained</p>
                </div>
                <div className="rounded-2xl border border-white/[0.06] bg-[#0d0d14] p-6 flex flex-col items-center">
                    <ScoreGauge
                        score={repo.scores?.beginner_friendliness || 0}
                        label="Beginner Friendly"
                        size={90}
                    />
                    <p className="mt-2 text-xs text-gray-500">How welcoming to newcomers</p>
                </div>
                <div className="rounded-2xl border border-white/[0.06] bg-[#0d0d14] p-6 flex flex-col items-center">
                    <div
                        className={`text-3xl font-bold ${combinedInfo.color}`}
                    >
                        {Math.round(repo.scores?.combined || 0)}
                    </div>
                    <p className="text-sm font-medium text-gray-300 mt-1">Combined Score</p>
                    <p className={`text-xs ${combinedInfo.color} mt-0.5`}>{combinedInfo.label}</p>
                </div>
            </div>

            {/* Metrics grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 mb-8">
                <MetricCard
                    icon={
                        <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                        </svg>
                    }
                    value={formatNumber(repo.stars)}
                    label="Stars"
                />
                <MetricCard
                    icon={
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M7.217 10.907a2.25 2.25 0 100 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186l9.566-5.314m-9.566 7.5l9.566 5.314m0 0a2.25 2.25 0 103.935 2.186 2.25 2.25 0 00-3.935-2.186zm0-12.814a2.25 2.25 0 103.933-2.185 2.25 2.25 0 00-3.933 2.185z" />
                        </svg>
                    }
                    value={formatNumber(repo.forks)}
                    label="Forks"
                />
                <MetricCard
                    icon={
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
                        </svg>
                    }
                    value={formatNumber(repo.metrics?.contributor_count || 0)}
                    label="Contributors"
                />
                <MetricCard
                    icon={<span className="text-sm">🏷</span>}
                    value={repo.metrics?.good_first_issue_count || 0}
                    label="Good First Issues"
                />
                <MetricCard
                    icon={
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    }
                    value={
                        repo.metrics?.avg_pr_merge_hours
                            ? `${Math.round(repo.metrics.avg_pr_merge_hours)}h`
                            : "N/A"
                    }
                    label="Avg PR Merge Time"
                />
                <MetricCard
                    icon={
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
                        </svg>
                    }
                    value={
                        repo.metrics?.avg_issue_response_hours
                            ? `${Math.round(repo.metrics.avg_issue_response_hours)}h`
                            : "N/A"
                    }
                    label="Avg Issue Response"
                />
                <MetricCard
                    icon={
                        <svg className="h-4 w-4 text-emerald-500" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                        </svg>
                    }
                    value={formatNumber(repo.metrics?.merged_pr_count || 0)}
                    label="Merged PRs"
                />
                <MetricCard
                    icon={
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
                        </svg>
                    }
                    value={timeAgo(repo.metrics?.last_commit_at)}
                    label="Last Commit"
                />
            </div>

            {/* Documentation flags */}
            <div className="mb-8">
                <h2 className="text-sm font-semibold text-gray-300 mb-3">Documentation & Community</h2>
                <div className="flex flex-wrap gap-2">
                    {[
                        { key: "has_readme", label: "README", has: repo.has_readme },
                        { key: "has_contributing_guide", label: "CONTRIBUTING", has: repo.has_contributing_guide },
                        { key: "has_code_of_conduct", label: "Code of Conduct", has: repo.has_code_of_conduct },
                        { key: "has_issue_templates", label: "Issue Templates", has: repo.has_issue_templates },
                        { key: "has_pr_templates", label: "PR Templates", has: repo.has_pr_templates },
                    ].map((item) => (
                        <span
                            key={item.key}
                            className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium ${item.has
                                    ? "bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20"
                                    : "bg-white/[0.03] text-gray-600 ring-1 ring-white/[0.06]"
                                }`}
                        >
                            {item.has ? "✓" : "✗"} {item.label}
                        </span>
                    ))}
                </div>
            </div>

            {/* Languages */}
            {repo.languages?.length > 0 && (
                <div className="mb-8">
                    <h2 className="text-sm font-semibold text-gray-300 mb-3">Languages</h2>
                    {/* Bar */}
                    <div className="flex h-2.5 rounded-full overflow-hidden bg-white/[0.04] mb-2">
                        {repo.languages.map((lang, i) => {
                            const colors = [
                                "bg-violet-500",
                                "bg-sky-500",
                                "bg-emerald-500",
                                "bg-amber-500",
                                "bg-rose-500",
                                "bg-indigo-500",
                            ];
                            return (
                                <div
                                    key={lang.language}
                                    className={`${colors[i % colors.length]} transition-all`}
                                    style={{ width: `${lang.percentage}%` }}
                                    title={`${lang.language}: ${lang.percentage}%`}
                                />
                            );
                        })}
                    </div>
                    <div className="flex flex-wrap gap-3">
                        {repo.languages.map((lang, i) => {
                            const dotColors = [
                                "bg-violet-500",
                                "bg-sky-500",
                                "bg-emerald-500",
                                "bg-amber-500",
                                "bg-rose-500",
                                "bg-indigo-500",
                            ];
                            return (
                                <span key={lang.language} className="flex items-center gap-1.5 text-xs text-gray-400">
                                    <span className={`h-2 w-2 rounded-full ${dotColors[i % dotColors.length]}`} />
                                    {lang.language} {lang.percentage}%
                                </span>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Good First Issues */}
            {repo.recent_good_first_issues?.length > 0 && (
                <div>
                    <h2 className="text-sm font-semibold text-gray-300 mb-3">
                        Good First Issues ({repo.recent_good_first_issues.length})
                    </h2>
                    <div className="space-y-3">
                        {repo.recent_good_first_issues.map((issue) => (
                            <IssueCard key={issue.id} issue={issue} />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
