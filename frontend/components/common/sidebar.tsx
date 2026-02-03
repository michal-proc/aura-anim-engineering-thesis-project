"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { FaVideo, FaCompass, FaTasks, FaPlus } from "react-icons/fa";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useI18n } from "@/lib/i18n-context";
import { LanguageSwitcher } from "./language-switcher";

export function Sidebar() {
  const pathname = usePathname();
  const { t } = useI18n();

  const navItems = [
    { icon: FaVideo, label: t("nav.videos"), href: "/videos" },
    { icon: FaCompass, label: t("nav.explore"), href: "/videos/explore" },
    { icon: FaTasks, label: t("nav.jobs"), href: "/jobs" },
    {
      icon: FaPlus,
      label: t("nav.createVideo"),
      href: "/videos/create",
      special: true,
    },
  ];

  return (
    <aside className="w-20 bg-[#0a0a0f] flex flex-col items-center py-6 space-y-8 border-r border-[#1a1a2e]">
      <Link
        href="/"
        className="w-12 h-12 flex items-center justify-center transition-all duration-300 hover:scale-110"
        style={{
          filter: "drop-shadow(0 4px 12px rgba(49, 183, 234, 0.5))",
        }}
      >
        <Image
          src="/logo.png"
          alt="Logo"
          width={48}
          height={48}
          className="object-contain"
        />
      </Link>

      <TooltipProvider delayDuration={0}>
        <nav className="flex flex-col items-center space-y-4 flex-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            if (item.special) {
              return (
                <Tooltip key={item.href}>
                  <TooltipTrigger asChild>
                    <Link
                      href={item.href}
                      className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300 bg-gradient-to-br from-[#31B7EA] via-[#375DDA] to-[#B949A3] text-white ${
                        isActive
                          ? "scale-110 shadow-xl shadow-[#B949A3]/40"
                          : "hover:shadow-lg hover:shadow-[#B949A3]/30 hover:scale-110"
                      }`}
                    >
                      <Icon
                        className={`w-5 h-5 ${isActive ? "rotate-90" : ""} transition-transform duration-300`}
                      />
                    </Link>
                  </TooltipTrigger>
                  <TooltipContent
                    side="right"
                    className="bg-[#1a1a2e] border-[#375DDA] text-white"
                  >
                    <p className="font-medium">{item.label}</p>
                  </TooltipContent>
                </Tooltip>
              );
            }

            return (
              <Tooltip key={item.href}>
                <TooltipTrigger asChild>
                  <Link
                    href={item.href}
                    className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300 ${
                      isActive
                        ? "bg-gradient-to-br from-[#31B7EA] to-[#375DDA] glow-ocean text-white"
                        : "bg-[#1a1a2e] hover:bg-[#252540] hover:glow-royal text-[#8a8aa8] hover:text-white"
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                  </Link>
                </TooltipTrigger>
                <TooltipContent
                  side="right"
                  className="bg-[#1a1a2e] border-[#375DDA] text-white"
                >
                  <p className="font-medium">{item.label}</p>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </nav>
      </TooltipProvider>

      <div className="mt-auto">
        <LanguageSwitcher />
      </div>
    </aside>
  );
}
