import type React from "react";
import type { Metadata } from "next";
import { Genos } from "next/font/google";
import { Analytics } from "@vercel/analytics/next";
import { I18nProvider } from "@/lib/i18n-context";
import { ReactQueryProvider } from "@/lib/react-query-provider";
import Image from "next/image";
import { JobFloatingPanel } from "@/components/common/job-floating-panel";
import { Toaster } from "@/components/ui/toaster";
import "./globals.css";

const genos = Genos({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-genos",
});

export const metadata: Metadata = {
  title: process.env.NEXT_PUBLIC_APP_NAME || "Dashboard",
  description: "Modern analytics dashboard",
  generator: "v0.app",
  icons: {
    icon: "/favicon.png",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={genos.variable}>
      <body className={`${genos.className} antialiased`}>
        <div className="fixed inset-0 z-0">
          <Image
            src="/background.gif"
            alt="Background"
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-br from-[#0b0219]/90 via-[#0f0f1a]/85 to-[#1a1a2e]/90 backdrop-blur-lg" />
        </div>

        <div className="relative z-10 min-h-screen transition-opacity duration-200">
          <ReactQueryProvider>
            <I18nProvider>
              {children}
              <JobFloatingPanel />
              <Toaster />
            </I18nProvider>
          </ReactQueryProvider>
        </div>
        <Analytics />
      </body>
    </html>
  );
}
