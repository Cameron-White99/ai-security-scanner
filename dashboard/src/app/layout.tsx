import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Nav } from "@/components/nav";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Security Scanner",
  description: "Prompt injection and LLM threat detection dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body suppressHydrationWarning className={`${inter.className} bg-gray-950 text-white min-h-screen`}>
        <div className="bg-yellow-500/10 border-b border-yellow-500/20 px-4 py-2.5 text-center text-xs text-yellow-300">
          <strong>Demo mode</strong> — No Anthropic API key is connected. LLM
          fallback classification is disabled; detections rely on rule-based and
          heuristic analysis only.
        </div>
        <Nav />
        {children}
      </body>
    </html>
  );
}
