import "../app/styles/globals.css";
import "../styles/sol.css";
import "../styles/system.css";
import "../app/tools/tools.css";
import "../app/prompt-kits/prompt-kits.css";
import "../app/learn/learn.css";
import "../app/jobs/jobs.css";

import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Open · Radar — Operational Console",
  description: "English AI Career + Tools Radar.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}