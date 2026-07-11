import "../styles/tailwind.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AccentProvider } from "@/lib/accent-context";

export const metadata: Metadata = {
  title: "OpenRadar Web V2",
  description:
    "OpenRadar — an English AI Career + Tools Radar. Stage 0-3 foundation only: repository, reference, design-token system, ThemeDial, /system laboratory.",
  robots: {
    // /system is noindex individually; default for everything else is index.
    index: true,
    follow: true,
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" data-accent="green">
      <body>
        <AccentProvider>{children}</AccentProvider>
      </body>
    </html>
  );
}