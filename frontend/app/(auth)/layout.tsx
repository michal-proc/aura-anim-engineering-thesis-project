import type React from "react";
import type { Metadata } from "next";
import { Genos } from "next/font/google";
import Link from "next/link";
import Image from "next/image";
import "@/app/globals.css";
import { LanguageSwitcher } from "@/components/common/language-switcher";

const genos = Genos({ subsets: ["latin"] });

export const metadata: Metadata = {
  description: "Authentication pages",
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen relative flex items-center justify-center p-4">
      <Link
        href="/"
        className="absolute top-6 left-6 z-20 hover:scale-110 transition-transform duration-200"
      >
        <Image
          src="/logo.png"
          alt="Logo"
          width={48}
          height={48}
          className="drop-shadow-[0_0_15px_rgba(49,183,234,0.5)]"
        />
      </Link>

      <div className="absolute bottom-6 left-6 z-20">
        <LanguageSwitcher />
      </div>

      <div className="w-full max-w-lg relative z-10">{children}</div>
    </div>
  );
}
