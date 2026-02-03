"use client";

import type React from "react";
import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { FaLock } from "react-icons/fa";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { authApi } from "@/api/auth";
import type { ResetPasswordPayload } from "@/types/auth.types";
import { useI18n } from "@/lib/i18n-context";

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const { t } = useI18n();

  const [formData, setFormData] = useState({
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      setError("Invalid or missing reset token");
    }
  }, [token]);

  const resetPasswordMutation = useMutation({
    mutationFn: (payload: ResetPasswordPayload) =>
      authApi.resetPassword(payload),
    onSuccess: () => {
      router.push("/login");
    },
    onError: (error: any) => {
      setError("Failed to reset password. Please try again.");
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (!token) {
      setError("Invalid reset token");
      return;
    }

    const payload: ResetPasswordPayload = {
      token,
      password: formData.password,
    };

    resetPasswordMutation.mutate(payload);
  };

  return (
    <div className="bg-[#0f0f1a] rounded-2xl p-8 border border-[#1a1a2e] shadow-2xl">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-[#31B7EA] via-[#375DDA] to-[#B949A3] bg-clip-text text-transparent mb-2">
          {t("auth.resetPasswordTitle")}
        </h1>
        <p className="text-[#6a6a8a]">{t("auth.resetPasswordDescription")}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-[#fe7070]/10 border border-[#fe7070] text-[#fe7070] px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-white mb-2">
            {t("auth.newPassword")}
          </label>
          <div className="relative">
            <FaLock className="absolute left-3 top-1/2 -translate-y-1/2 text-[#6a6a8a]" />
            <input
              type="password"
              value={formData.password}
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
              className="w-full bg-[#1a1a2e] border border-[#2a2a3e] rounded-lg pl-10 pr-4 py-3 text-white focus:border-[#31B7EA] transition-colors"
              placeholder={t("auth.enterNewPassword")}
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-white mb-2">
            {t("auth.confirmPassword")}
          </label>
          <div className="relative">
            <FaLock className="absolute left-3 top-1/2 -translate-y-1/2 text-[#6a6a8a]" />
            <input
              type="password"
              value={formData.confirmPassword}
              onChange={(e) =>
                setFormData({ ...formData, confirmPassword: e.target.value })
              }
              className="w-full bg-[#1a1a2e] border border-[#2a2a3e] rounded-lg pl-10 pr-4 py-3 text-white focus:border-[#31B7EA] transition-colors"
              placeholder={t("auth.confirmNewPassword")}
              required
            />
          </div>
        </div>

        <Button
          type="submit"
          variant="blue"
          className="w-full"
          disabled={resetPasswordMutation.isPending || !token}
        >
          {resetPasswordMutation.isPending
            ? t("auth.resetting")
            : t("auth.resetPasswordButton")}
        </Button>

        <p className="text-center text-sm text-[#6a6a8a]">
          {t("auth.rememberPassword")}{" "}
          <Link
            href="/login"
            className="text-[#31B7EA] hover:text-[#358EE3] font-medium"
          >
            {t("auth.signIn")}
          </Link>
        </p>
      </form>
    </div>
  );
}
