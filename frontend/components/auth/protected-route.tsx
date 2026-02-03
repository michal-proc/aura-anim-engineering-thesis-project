"use client";

import type React from "react";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/store/auth-store";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, isInitialized, validateSession } = useAuthStore();
  const [isValidating, setIsValidating] = useState(true);

  useEffect(() => {
    const validateAndCheckSession = async () => {
      console.log("[v0] ProtectedRoute: Validating session for", pathname);

      // Wait for initial auth to initialize
      if (!isInitialized) {
        console.log("[v0] ProtectedRoute: Waiting for initialization");
        return;
      }

      // If not authenticated after initialization, redirect to login
      if (!isAuthenticated) {
        console.log(
          "[v0] ProtectedRoute: Not authenticated, redirecting to login",
        );
        router.push("/login");
        return;
      }

      setIsValidating(true);
      try {
        console.log("[v0] ProtectedRoute: Calling validateSession");
        const isValid = await validateSession();
        console.log("[v0] ProtectedRoute: Session validation result:", isValid);

        if (!isValid) {
          console.log(
            "[v0] ProtectedRoute: Invalid session, redirecting to login",
          );
          router.push("/login");
        }
      } catch (error) {
        console.log("[v0] ProtectedRoute: Session validation error:", error);
        router.push("/login");
      } finally {
        setIsValidating(false);
      }
    };

    validateAndCheckSession();
  }, [pathname, isAuthenticated, isInitialized, router, validateSession]);

  // Show loading while initializing or validating
  if (!isInitialized || isValidating) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#31B7EA]"></div>
      </div>
    );
  }

  // If not authenticated, don't render children
  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
