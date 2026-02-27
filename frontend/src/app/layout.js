import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata = {
  title: "OpenFirst — Find Beginner-Friendly Open Source Projects",
  description:
    "Discover active, welcoming open source repositories with real metrics. Find good-first-issues, check maintainer responsiveness, and start contributing today.",
  keywords: [
    "open source",
    "good first issue",
    "beginner",
    "contribute",
    "github",
  ],
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased">
        <Navbar />
        <main className="pt-16 min-h-screen">{children}</main>
      </body>
    </html>
  );
}
