
export function formatNumber(num) {
    if (num === null || num === undefined) return "0";
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
    if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
    return num.toString();
}

export function timeAgo(dateStr) {
    if (!dateStr) return "Unknown";
    const date = new Date(dateStr);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return "just now";
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 2592000) return `${Math.floor(seconds / 86400)}d ago`;
    if (seconds < 31536000) return `${Math.floor(seconds / 2592000)}mo ago`;
    return `${Math.floor(seconds / 31536000)}y ago`;
}

export function getScoreInfo(score) {
    if (score >= 80)
        return { label: "Excellent", color: "text-emerald-400", bg: "bg-emerald-500/20", ring: "ring-emerald-500/30" };
    if (score >= 60)
        return { label: "Good", color: "text-sky-400", bg: "bg-sky-500/20", ring: "ring-sky-500/30" };
    if (score >= 40)
        return { label: "Moderate", color: "text-amber-400", bg: "bg-amber-500/20", ring: "ring-amber-500/30" };
    if (score >= 20)
        return { label: "Low", color: "text-orange-400", bg: "bg-orange-500/20", ring: "ring-orange-500/30" };
    return { label: "Very Low", color: "text-red-400", bg: "bg-red-500/20", ring: "ring-red-500/30" };
}

export function getDifficultyInfo(difficulty) {
    switch (difficulty) {
        case "easy":
            return { label: "Easy", color: "text-emerald-400", bg: "bg-emerald-500/15" };
        case "medium":
            return { label: "Medium", color: "text-amber-400", bg: "bg-amber-500/15" };
        case "hard":
            return { label: "Hard", color: "text-red-400", bg: "bg-red-500/15" };
        default:
            return { label: "Unknown", color: "text-gray-400", bg: "bg-gray-500/15" };
    }
}
