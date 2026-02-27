import Link from "next/link";
import { formatNumber, getScoreInfo, timeAgo } from "@/lib/utils";
import ScoreGauge from "@/components/ui/ScoreGauge";

export default function RepoCard({ repo }) {
    const combinedInfo = getScoreInfo(repo.scores?.combined || 0);

    return (
        <Link href={`/repo/${repo.id}`} className="group block h-full">
            <div className="relative flex h-full flex-col overflow-hidden rounded-2xl border border-white/[0.06] bg-[#0d0d14] p-5 transition-all duration-300 hover:border-white/[0.12] hover:bg-[#0f0f18] hover:shadow-xl hover:shadow-black/20 hover:-translate-y-0.5">
                {/* Top: Name + Language */}
                <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="min-w-0">
                        <h3 className="text-sm font-semibold text-white truncate group-hover:text-violet-300 transition-colors">
                            {repo.full_name}
                        </h3>
                        {repo.primary_language && (
                            <span className="inline-flex items-center gap-1.5 mt-1">
                                <span className="h-2.5 w-2.5 rounded-full bg-violet-500/60" />
                                <span className="text-xs text-gray-500">
                                    {repo.primary_language}
                                </span>
                            </span>
                        )}
                    </div>
                    <div
                        className={`shrink-0 rounded-lg px-2.5 py-1 text-xs font-bold ${combinedInfo.bg} ${combinedInfo.color} ring-1 ${combinedInfo.ring}`}
                    >
                        {Math.round(repo.scores?.combined || 0)}
                    </div>
                </div>

                {/* Description */}
                <p className="text-xs text-gray-500 leading-relaxed line-clamp-2 mb-4 min-h-[2rem]">
                    {repo.description || "No description available."}
                </p>

                {/* Score gauges */}
                <div className="mt-auto flex items-center justify-center gap-6 mb-4 py-2">
                    <ScoreGauge
                        score={repo.scores?.activity || 0}
                        label="Activity"
                        size={60}
                    />
                    <ScoreGauge
                        score={repo.scores?.beginner_friendliness || 0}
                        label="Beginner"
                        size={60}
                    />
                </div>

                {/* Bottom metrics row */}
                <div className="flex items-center justify-between text-xs text-gray-500 border-t border-white/[0.04] pt-3">
                    <span className="flex items-center gap-1">
                        <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                        </svg>
                        {formatNumber(repo.stars)}
                    </span>
                    <span className="flex items-center gap-1">
                        <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M7.217 10.907a2.25 2.25 0 100 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186l9.566-5.314m-9.566 7.5l9.566 5.314m0 0a2.25 2.25 0 103.935 2.186 2.25 2.25 0 00-3.935-2.186zm0-12.814a2.25 2.25 0 103.933-2.185 2.25 2.25 0 00-3.933 2.185z" />
                        </svg>
                        {formatNumber(repo.forks)}
                    </span>
                    <span className="flex items-center gap-1 text-emerald-500/70">
                        🏷 {repo.metrics?.good_first_issue_count || 0} GFIs
                    </span>
                    <span>{timeAgo(repo.metrics?.last_commit_at)}</span>
                </div>

                {/* Topics */}
                {repo.topics?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                        {repo.topics.slice(0, 4).map((topic) => (
                            <span
                                key={topic}
                                className="rounded-md bg-white/[0.04] px-2 py-0.5 text-[10px] text-gray-500"
                            >
                                {topic}
                            </span>
                        ))}
                        {repo.topics.length > 4 && (
                            <span className="text-[10px] text-gray-600">
                                +{repo.topics.length - 4}
                            </span>
                        )}
                    </div>
                )}
            </div>
        </Link>
    );
}
