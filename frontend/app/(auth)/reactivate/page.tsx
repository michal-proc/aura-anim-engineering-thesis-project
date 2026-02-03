"use client";

import type React from "react";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  FaEnvelope,
  FaLock,
  FaCheckCircle,
  FaTimesCircle,
} from "react-icons/fa";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/store/auth-store";
import { authApi } from "@/api/auth";
import type { ReactivateAccountPayload } from "@/types/auth.types";
import { useI18n } from "@/lib/i18n-context";

const validatePassword = (password: string) => {
  return {
    minLength: password.length >= 8,
    hasUppercase: /[A-Z]/.test(password),
    hasLowercase: /[a-z]/.test(password),
    hasNumber: /[0-9]/.test(password),
  };
};

export default function ReactivatePage() {
  const router = useRouter();
  const { t } = useI18n();
  const [formData, setFormData] = useState<ReactivateAccountPayload>({
    email: "",
    password: "",
  });
  const [passwordValidation, setPasswordValidation] = useState(
    validatePassword(""),
  );
  const [showValidation, setShowValidation] = useState(false);

  useEffect(() => {
    setPasswordValidation(validatePassword(formData.password));
  }, [formData.password]);

  const reactivateMutation = useMutation({
    mutationFn: authApi.reactivate,
    onSuccess: (response) => {
      if (response.success) {
        router.push("/verify-email");
      }
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const allRequirementsMet = Object.values(passwordValidation).every(Boolean);
    if (!allRequirementsMet) {
      return; // Don't submit if password doesn't meet requirements
    }

    reactivateMutation.mutate(formData);
  };

  if (reactivateMutation.isSuccess) {
    return (
      <div className="bg-[#0f0f1a] rounded-2xl p-8 border border-[#1a1a2e] shadow-2xl">
        <div className="text-center">
          <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <FaCheckCircle className="w-8 h-8 text-green-500" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">
            {t("auth.reactivateSuccess")}
          </h1>
          <p className="text-[#6a6a8a]">
            {t("auth.reactivateSuccessDescription")}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#0f0f1a] rounded-2xl p-8 border border-[#1a1a2e] shadow-2xl">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-[#31B7EA] via-[#375DDA] to-[#B949A3] bg-clip-text text-transparent mb-2">
          {t("auth.reactivateAccount")}
        </h1>
        <p className="text-[#6a6a8a]">{t("auth.reactivateDescription")}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {reactivateMutation.isError && (
          <div className="bg-[#fe7070]/10 border border-[#fe7070] text-[#fe7070] px-4 py-3 rounded-lg text-sm">
            {t("auth.reactivateError")}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-white mb-2">
            {t("profile.email")}
          </label>
          <div className="relative">
            <FaEnvelope className="absolute left-3 top-1/2 -translate-y-1/2 text-[#6a6a8a]" />
            <input
              type="email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              className="w-full bg-[#1a1a2e] border border-[#2a2a3e] rounded-lg pl-10 pr-4 py-3 text-white focus:border-[#31B7EA] transition-colors"
              placeholder={t("profile.email")}
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-white mb-2">
            {t("profile.oldPassword")}
          </label>
          <div className="relative">
            <FaLock className="absolute left-3 top-1/2 -translate-y-1/2 text-[#6a6a8a]" />
            <input
              type="password"
              value={formData.password}
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
              onFocus={() => setShowValidation(true)}
              className="w-full bg-[#1a1a2e] border border-[#2a2a3e] rounded-lg pl-10 pr-4 py-3 text-white focus:border-[#31B7EA] transition-colors"
              placeholder={t("profile.oldPassword")}
              required
            />
          </div>

          {showValidation && formData.password && (
            <div className="mt-3 space-y-2 bg-[#1a1a2e] border border-[#2a2a3e] rounded-lg p-4">
              <p className="text-xs font-medium text-[#6a6a8a] mb-2">
                {t("auth.passwordRequirements")}
              </p>
              <div className="space-y-1.5">
                <div className="flex items-center gap-2 text-sm">
                  {passwordValidation.minLength ? (
                    <FaCheckCircle className="text-green-500 flex-shrink-0" />
                  ) : (
                    <FaTimesCircle className="text-[#6a6a8a] flex-shrink-0" />
                  )}
                  <span
                    className={
                      passwordValidation.minLength
                        ? "text-green-500"
                        : "text-[#6a6a8a]"
                    }
                  >
                    {t("auth.minLength")}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  {passwordValidation.hasUppercase ? (
                    <FaCheckCircle className="text-green-500 flex-shrink-0" />
                  ) : (
                    <FaTimesCircle className="text-[#6a6a8a] flex-shrink-0" />
                  )}
                  <span
                    className={
                      passwordValidation.hasUppercase
                        ? "text-green-500"
                        : "text-[#6a6a8a]"
                    }
                  >
                    {t("auth.hasUppercase")}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  {passwordValidation.hasLowercase ? (
                    <FaCheckCircle className="text-green-500 flex-shrink-0" />
                  ) : (
                    <FaTimesCircle className="text-[#6a6a8a] flex-shrink-0" />
                  )}
                  <span
                    className={
                      passwordValidation.hasLowercase
                        ? "text-green-500"
                        : "text-[#6a6a8a]"
                    }
                  >
                    {t("auth.hasLowercase")}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  {passwordValidation.hasNumber ? (
                    <FaCheckCircle className="text-green-500 flex-shrink-0" />
                  ) : (
                    <FaTimesCircle className="text-[#6a6a8a] flex-shrink-0" />
                  )}
                  <span
                    className={
                      passwordValidation.hasNumber
                        ? "text-green-500"
                        : "text-[#6a6a8a]"
                    }
                  >
                    {t("auth.hasNumber")}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        <Button
          type="submit"
          variant="blue"
          className="w-full"
          disabled={
            reactivateMutation.isPending ||
            !Object.values(passwordValidation).every(Boolean)
          }
        >
          {reactivateMutation.isPending
            ? t("auth.reactivating")
            : t("auth.reactivateButton")}
        </Button>

        <p className="text-center text-sm text-[#6a6a8a]">
          {t("auth.backToLogin")}{" "}
          <Link
            href="/login"
            className="text-[#31B7EA] hover:text-[#358EE3] font-medium"
          >
            {t("auth.login")}
          </Link>
        </p>
      </form>
    </div>
  );
}
