export default function Badge({
    children,
    color = "text-gray-300",
    bg = "bg-white/[0.06]",
    className = "",
}) {
    return (
        <span
            className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ${color} ${bg} ${className}`}
        >
            {children}
        </span>
    );
}
