export default function MetricCard({ icon, value, label, subtext }) {
    return (
        <div className="flex items-start gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3.5">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white/[0.04] text-gray-400">
                {icon}
            </div>
            <div className="min-w-0">
                <p className="text-sm font-semibold text-white truncate">{value}</p>
                <p className="text-xs text-gray-500">{label}</p>
                {subtext && (
                    <p className="text-[10px] text-gray-600 mt-0.5">{subtext}</p>
                )}
            </div>
        </div>
    );
}
