import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ghost — Hiring Bias Audit",
  description:
    "See what ATS systems do to your resume based on your name. Grounded in Bertrand & Mullainathan (2004).",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-zinc-950 antialiased">{children}</body>
    </html>
  );
}
