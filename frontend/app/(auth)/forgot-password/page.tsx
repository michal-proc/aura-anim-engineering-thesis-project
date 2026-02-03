"use client";

import type React from "react";
import { useState } from "react";
import Link from "next/link";
import { FaEnvelope } from "react-icons/fa";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { authApi } from "@/api/auth";
import type { ForgotPasswordPayload } from "@/types/auth.types";
import { useI18n } from "@/lib/i18n-context";

export default function ForgotPasswordPage() {
  const { t } = useI18n();
  const [formData, setFormData] = useState<ForgotPasswordPayload>({
    email: "",
  });
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const forgotPasswordMutation = useMutation({
    mutationFn: (payload: ForgotPasswordPayload) =>
      authApi.forgotPassword(payload),
    onSuccess: () => {
      setSuccess(true);
      setError("");
    },
    onError: (error: any) => {
      setError("Failed to send reset email. Please try again.");
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    forgotPasswordMutation.mutate(formData);
  };

  return (
    <div className="bg-[#0f0f1a] rounded-2xl p-8 border border-[#1a1a2e] shadow-2xl">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-[#31B7EA] via-[#375DDA] to-[#B949A3] bg-clip-text text-transparent mb-2">
          {t("auth.forgotPasswordTitle")}
        </h1>
        <p className="text-[#6a6a8a]">{t("auth.forgotPasswordDescription")}</p>
      </div>

      {success ? (
        <div className="text-center space-y-4">
          <div className="bg-[#21bb85]/10 border border-[#21bb85] text-[#21bb85] px-4 py-3 rounded-lg">
            {t("auth.resetLinkSent")}
          </div>
          <Link href="/login">
            <Button variant="blue" className="w-full">
              {t("auth.backToLoginButton")}
            </Button>
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-[#fe7070]/10 border border-[#fe7070] text-[#fe7070] px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-white mb-2">
              {t("auth.emailAddress")}
            </label>
            <div className="relative">
              <FaEnvelope className="absolute left-3 top-1/2 -translate-y-1/2 text-[#6a6a8a]" />
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ email: e.target.value })}
                className="w-full bg-[#1a1a2e] border border-[#2a2a3e] rounded-lg pl-10 pr-4 py-3 text-white focus:border-[#31B7EA] transition-colors"
                placeholder={t("auth.enterEmail")}
                required
              />
            </div>
          </div>

          <Button
            type="submit"
            variant="blue"
            className="w-full"
            disabled={forgotPasswordMutation.isPending}
          >
            {forgotPasswordMutation.isPending
              ? t("auth.sending")
              : t("auth.sendResetLink")}
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
      )}
    </div>
  );
}
