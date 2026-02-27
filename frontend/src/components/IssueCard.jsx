import { getDifficultyInfo, timeAgo } from "@/lib/utils";
import Badge from "@/components/ui/Badge";

export default function IssueCard({ issue, showRepo = false }) {
    const difficulty = getDifficultyInfo(issue.difficulty_estimate);

    return (
        <a
            href={issue.html_url || "#"}
            target="_blank"
            rel="noopener noreferrer"
            className="group block h-full"
        >
            <div className="relative flex h-full flex-col overflow-hidden rounded-xl border border-white/[0.06] bg-[#0d0d14] p-4 transition-all duration-200 hover:border-white/[0.12] hover:bg-[#0f0f18]">
                <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                        {/* Repo name */}
                        {showRepo && issue.repo_full_name && (
                            <p className="text-[11px] text-violet-400/70 font-medium mb-1 truncate">
                                {issue.repo_full_name}
                            </p>
                        )}

                        {/* Title */}
                        <h4 className="text-sm font-medium text-gray-200 group-hover:text-white transition-colors line-clamp-2 leading-snug">
                            {issue.title}
                        </h4>

                        {/* Labels */}
                        <div className="flex flex-wrap items-center gap-1.5 mt-2.5">
                            <Badge color={difficulty.color} bg={difficulty.bg}>
                                {difficulty.label}
                            </Badge>
                            {issue.labels?.slice(0, 3).map((label) => (
                                <Badge key={label}>{label}</Badge>
                            ))}
                        </div>
                    </div>

                    {/* Assignment status */}
                    <div
                        className={`shrink-0 mt-0.5 h-2.5 w-2.5 rounded-full ${issue.is_assigned ? "bg-amber-500/60" : "bg-emerald-500/60"
                            }`}
                        title={issue.is_assigned ? "Assigned" : "Open"}
                    />
                </div>

                {/* Footer */}
                <div className="mt-auto flex items-center gap-3 pt-4 text-[11px] text-gray-500">
                    <span className="flex items-center gap-1">
                        <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 011.037-.443 48.282 48.282 0 005.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
                        </svg>
                        {issue.comment_count} comments
                    </span>
                    <span>{timeAgo(issue.created_at)}</span>
                    {issue.is_assigned && (
                        <span className="text-amber-500/80">• Assigned</span>
                    )}
                </div>
            </div>
        </a>
    );
}
