import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

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
      <body className="antialiased flex flex-col min-h-screen">
        <Navbar />
        <main className="pt-16 flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
