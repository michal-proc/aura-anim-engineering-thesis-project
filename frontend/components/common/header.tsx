"use client";

import { ChevronDown } from "lucide-react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { FaCog, FaSignOutAlt, FaSignInAlt, FaUserPlus } from "react-icons/fa";
import { DropdownMenuWrapper } from "../ui/dropdown-menu-wrapper";
import { useI18n } from "@/lib/i18n-context";
import { useAuthStore } from "@/store/auth-store";
import { useMutation } from "@tanstack/react-query";
import { authApi } from "@/api/auth";

interface HeaderProps {
  title?: string;
}

export function Header({ title }: HeaderProps) {
  const appName = process.env.NEXT_PUBLIC_APP_NAME || "Dashboard";
  const { t } = useI18n();
  const router = useRouter();
  const pathname = usePathname();

  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const user = useAuthStore((state) => state.user);
  const accessToken = useAuthStore((state) => state.accessToken);
  const logout = useAuthStore((state) => state.logout);

  const logoutMutation = useMutation({
    mutationFn: () => authApi.logout(accessToken || ""),
    onSuccess: () => {
      logout();
      router.push("/login");
    },
    onError: () => {
      logout();
      router.push("/login");
    },
  });

  const userOptions = [
    {
      icon: <FaCog className="w-4 h-4" />,
      label: t("user.settings"),
      onClick: () => router.push("/users/me"),
    },
    {
      icon: <FaSignOutAlt className="w-4 h-4" />,
      label: t("user.logout"),
      onClick: () => logoutMutation.mutate(),
    },
  ];

  const isPublicRoute =
    pathname?.startsWith("/(auth)") ||
    pathname === "/login" ||
    pathname === "/register" ||
    pathname === "/forgot-password" ||
    pathname === "/reset-password" ||
    pathname === "/verify-email" ||
    pathname === "/reactivate" ||
    pathname?.startsWith("/shared/");

  console.log(isAuthenticated, user);

  return (
    <header
      className="
        relative 
        bg-gradient-to-r from-[#0f0f1a] via-[#12121f] to-[#0f0f1a]
        px-8 py-6 
        flex items-center justify-between
        border-b border-[#1a1a2e]
        transition-all duration-700
        group
      "
    >
      <div
        className="
          absolute left-1/2 -translate-x-1/2 top-1/2 -translate-y-1/2
          flex items-center gap-4 select-none
        "
      >
        <span
          className="
            h-[2px] w-32 
            bg-gradient-to-r from-transparent via-[#375DDA] to-[#31B7EA]
            opacity-70 
            transition-all duration-700 group-hover:opacity-100 group-hover:w-40
          "
        />
        <h1
          className="
            text-4xl font-bold whitespace-nowrap
            bg-gradient-to-r from-[#31B7EA] via-[#375DDA] to-[#B949A3]
            bg-clip-text text-transparent
            transition-all duration-700 
            bg-[length:200%_100%]
            group-hover:bg-[position:100%_0]
            tracking-wide
          "
        >
          {appName}
        </h1>
        <span
          className="
            h-[2px] w-32 
            bg-gradient-to-l from-transparent via-[#375DDA] to-[#B949A3]
            opacity-70
            transition-all duration-700 group-hover:opacity-100 group-hover:w-40
          "
        />
      </div>

      <div className="w-[200px]" />

      {isAuthenticated && user ? (
        <DropdownMenuWrapper
          trigger={(open) => (
            <button
              className="
                flex items-center gap-4 cursor-pointer 
                hover:opacity-90 transition-all
                group/avatar
              "
            >
              <div className="text-right mr-1">
                <p className="text-sm font-semibold text-white group-hover/avatar:text-[#31B7EA] transition">
                  {user.full_name}
                </p>
                <p className="text-xs text-[#6a6a8a]">{user.email}</p>
              </div>

              <Avatar
                className="
                  w-11 h-11 border-2 border-[#31B7EA] 
                  transition-transform duration-300
                  group-hover/avatar:scale-110
                "
              >
                <AvatarImage src={user.avatar_url || undefined} />
                <AvatarFallback className="bg-gradient-to-br from-[#31B7EA] to-[#B949A3] text-white">
                  {user.full_name?.charAt(0) || "U"}
                </AvatarFallback>
              </Avatar>

              <ChevronDown
                className={`
                  w-4 h-4 text-[#6a6a8a] 
                  transition-all duration-300
                  group-hover/avatar:text-[#31B7EA] 
                  ${open ? "rotate-180" : ""}
                `}
              />
            </button>
          )}
          options={userOptions}
        />
      ) : isPublicRoute ? (
        <div className="flex items-center gap-3">
          <Link href="/login">
            <Button
              variant="blue"
              size="sm"
              className="flex items-center gap-2"
            >
              <FaSignInAlt className="w-4 h-4" />
              {t("auth.login")}
            </Button>
          </Link>
          <Link href="/register">
            <Button
              variant="magenta"
              size="sm"
              className="flex items-center gap-2"
            >
              <FaUserPlus className="w-4 h-4" />
              {t("auth.register")}
            </Button>
          </Link>
        </div>
      ) : null}
    </header>
  );
}
