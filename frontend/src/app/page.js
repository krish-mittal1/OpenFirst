import Link from "next/link";

export default function HomePage() {
  return (
    <div className="relative overflow-hidden">
      {/* Background glows */}
      <div className="hero-glow hero-glow-1" />
      <div className="hero-glow hero-glow-2" />

      {/* ── Hero ──────────────────────────────────────── */}
      <section className="relative mx-auto max-w-5xl px-4 pt-24 pb-20 text-center sm:pt-32 sm:pb-28">
        {/* Badge */}
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-violet-500/20 bg-violet-500/[0.08] px-4 py-1.5 text-xs font-medium text-violet-300">
          <span className="h-1.5 w-1.5 rounded-full bg-violet-400 animate-pulse" />
          Real-time GitHub data
        </div>

        <h1 className="text-4xl font-extrabold leading-tight tracking-tight text-white sm:text-5xl md:text-6xl">
          Your first open source
          <br />
          <span className="bg-gradient-to-r from-violet-400 via-indigo-400 to-sky-400 bg-clip-text text-transparent">
            contribution starts here.
          </span>
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-base text-gray-400 leading-relaxed sm:text-lg">
          Discover actively maintained repositories with genuine &quot;good first issues.&quot;
          We analyze real metrics — commit frequency, PR merge times, issue response
          rates — so you find projects that actually welcome beginners.
        </p>

        {/* CTA Buttons */}
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/explore"
            className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 hover:brightness-110 transition-all duration-200"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
            </svg>
            Explore Projects
          </Link>
          <Link
            href="/issues"
            className="inline-flex items-center gap-2 rounded-xl border border-white/[0.1] bg-white/[0.03] px-6 py-3 text-sm font-semibold text-gray-300 hover:text-white hover:bg-white/[0.06] hover:border-white/[0.15] transition-all duration-200"
          >
            Find Issues
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </Link>
        </div>
      </section>

      {/* ── Features ──────────────────────────────────── */}
      <section className="mx-auto max-w-6xl px-4 pb-24">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[
            {
              icon: (
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                </svg>
              ),
              title: "Activity Score",
              desc: "Custom-calculated score based on commit frequency, PR merge times, and release cadence.",
              gradient: "from-amber-500/20 to-orange-500/20",
            },
            {
              icon: (
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15.182 15.182a4.5 4.5 0 01-6.364 0M21 12a9 9 0 11-18 0 9 9 0 0118 0zM9.75 9.75c0 .414-.168.75-.375.75S9 10.164 9 9.75 9.168 9 9.375 9s.375.336.375.75zm-.375 0h.008v.015h-.008V9.75zm5.625 0c0 .414-.168.75-.375.75s-.375-.336-.375-.75.168-.75.375-.75.375.336.375.75zm-.375 0h.008v.015h-.008V9.75z" />
                </svg>
              ),
              title: "Beginner Friendliness",
              desc: "Measures docs quality, maintainer response time, and first-timer PR acceptance rate.",
              gradient: "from-emerald-500/20 to-teal-500/20",
            },
            {
              icon: (
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
                </svg>
              ),
              title: "Issue Difficulty",
              desc: "AI-powered difficulty estimation — easy, medium, or hard — so you pick what fits your level.",
              gradient: "from-violet-500/20 to-purple-500/20",
            },
            {
              icon: (
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ),
              title: "PR Merge Time",
              desc: "Know exactly how fast maintainers review and merge pull requests before you start.",
              gradient: "from-sky-500/20 to-blue-500/20",
            },
            {
              icon: (
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
                </svg>
              ),
              title: "No Dead Repos",
              desc: "We filter out archived, inactive, and abandoned repositories automatically.",
              gradient: "from-rose-500/20 to-pink-500/20",
            },
            {
              icon: (
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                </svg>
              ),
              title: "Real Metrics",
              desc: "Stars, forks, open/closed PRs, contributors, and response times — all from live data.",
              gradient: "from-indigo-500/20 to-violet-500/20",
            },
          ].map((feat, i) => (
            <div
              key={i}
              className={`rounded-2xl border border-white/[0.06] bg-gradient-to-br ${feat.gradient} p-5 transition-all duration-300 hover:border-white/[0.12] hover:-translate-y-0.5`}
            >
              <div className="mb-3 inline-flex rounded-lg bg-white/[0.06] p-2 text-gray-300">
                {feat.icon}
              </div>
              <h3 className="text-sm font-semibold text-white mb-1.5">
                {feat.title}
              </h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                {feat.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Bottom CTA ────────────────────────────────── */}
      <section className="relative mx-auto max-w-4xl px-4 pb-24 text-center">
        <div className="rounded-2xl border border-white/[0.06] bg-gradient-to-br from-violet-500/[0.08] to-indigo-500/[0.08] p-10 sm:p-14">
          <h2 className="text-2xl font-bold text-white sm:text-3xl">
            Ready to make your first pull request?
          </h2>
          <p className="mx-auto mt-3 max-w-lg text-sm text-gray-400 leading-relaxed">
            Browse hundreds of vetted repositories, find an issue that matches
            your skill level, and start contributing to open source today.
          </p>
          <Link
            href="/explore"
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3 text-sm font-semibold text-gray-900 shadow-lg hover:bg-gray-100 transition-all duration-200"
          >
            Start Exploring
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </Link>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────── */}
      <footer className="border-t border-white/[0.04] py-8 text-center text-xs text-gray-600">
        <p>
          Built with ❤️ for the open source community.
          Data sourced from the{" "}
          <a
            href="https://docs.github.com/en/rest"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-400 hover:text-white transition-colors"
          >
            GitHub API
          </a>
          .
        </p>
      </footer>
    </div>
  );
}
