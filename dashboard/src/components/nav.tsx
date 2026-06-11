"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/scans", label: "Scans" },
  { href: "/reports", label: "Reports" },
];

export function Nav() {
  const pathname = usePathname();
  return (
    <nav className="border-b border-gray-800 bg-gray-900">
      <div className="mx-auto max-w-7xl px-4 flex items-center h-14 gap-6">
        <span className="font-semibold text-white text-sm tracking-wide">
          AI Security Scanner
        </span>
        <div className="flex gap-1">
          {links.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={`text-sm px-3 py-1.5 rounded transition-colors ${
                pathname === href
                  ? "bg-gray-800 text-white"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
