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
        <Nav />
        {children}
      </body>
    </html>
  );
}
