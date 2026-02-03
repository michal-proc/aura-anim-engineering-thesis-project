"use client";

import type React from "react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  FaEnvelope,
  FaLock,
  FaUser,
  FaCheckCircle,
  FaTimesCircle,
} from "react-icons/fa";
import { Button } from "@/components/ui/button";
import type { RegisterUserPayload } from "@/types/auth.types";
import { useMutation } from "@tanstack/react-query";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/store/auth-store";
import { useI18n } from "@/lib/i18n-context";

const validatePassword = (password: string) => {
  return {
    minLength: password.length >= 8,
    hasUppercase: /[A-Z]/.test(password),
    hasLowercase: /[a-z]/.test(password),
    hasNumber: /[0-9]/.test(password),
  };
};

export default function RegisterPage() {
  const { t } = useI18n();
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [formData, setFormData] = useState<
    RegisterUserPayload & { confirmPassword: string }
  >({
    email: "",
    username: "",
    password: "",
    full_name: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [passwordValidation, setPasswordValidation] = useState(
    validatePassword(""),
  );
  const [showValidation, setShowValidation] = useState(false);

  useEffect(() => {
    setPasswordValidation(validatePassword(formData.password));
  }, [formData.password]);

  const registerMutation = useMutation({
    mutationFn: authApi.register,
    onSuccess: (response) => {
      router.push("/verify-email");
    },
    onError: (error: any) => {
      const errorMessage =
        error?.error?.message || "Registration failed. Please try again.";
      setError(errorMessage);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const allRequirementsMet = Object.values(passwordValidation).every(Boolean);
    if (!allRequirementsMet) {
      setError(t("auth.invalidPassword"));
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError(t("profile.passwordMismatch"));
      return;
    }

    const { confirmPassword, ...payload } = formData;
    registerMutation.mutate(payload);
  };

  const isFormValid = () => {
    return (
      formData.email &&
      formData.username &&
      formData.full_name &&
      formData.password &&
      formData.confirmPassword &&
      Object.values(passwordValidation).every(Boolean) &&
      formData.password === formData.confirmPassword
    );
  };

  return (
    <div className="bg-[#0f0f1a] rounded-2xl p-8 border border-[#1a1a2e] shadow-2xl">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-[#31B7EA] via-[#375DDA] to-[#B949A3] bg-clip-text text-transparent mb-2">
          {t("auth.createAccount")}
        </h1>
        <p className="text-[#6a6a8a]">{t("auth.createAccountDescription")}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {error && (
          <div className="bg-[#fe7070]/10 border border-[#fe7070] text-[#fe7070] px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-white mb-2">
            {t("auth.fullName")}
          </label>
          <div className="relative">
            <FaUser className="absolute left-3 top-1/2 -translate-y-1/2 text-[#6a6a8a]" />
            <input
              type="text"
              value={formData.full_name}
              onChange={(e) =>
                setFormData({ ...formData, full_name: e.target.value })
              }
              className="w-full bg-[#1a1a2e] border border-[#2a2a3e] rounded-lg pl-10 pr-4 py-3 text-white focus:border-[#31B7EA] transition-colors"
              placeholder={t("auth.enterFullName")}
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-white mb-2">
            {t("auth.username")}
          </label>
          <div className="relative">
            <FaUser className="absolute left-3 top-1/2 -translate-y-1/2 text-[#6a6a8a]" />
            <input
              type="text"
              value={formData.username}
              onChange={(e) =>
                setFormData({ ...formData, username: e.target.value })
              }
              className="w-full bg-[#1a1a2e] border border-[#2a2a3e] rounded-lg pl-10 pr-4 py-3 text-white focus:border-[#31B7EA] transition-colors"
              placeholder={t("auth.chooseUsername")}
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-white mb-2">
            {t("auth.email")}
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
              placeholder={t("auth.enterEmail")}
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-white mb-2">
            {t("auth.password")}
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
              placeholder={t("auth.createPassword")}
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
              placeholder={t("auth.confirmPasswordPlaceholder")}
              required
            />
          </div>
        </div>

        <Button
          type="submit"
          variant="blue"
          className="w-full"
          disabled={registerMutation.isPending || !isFormValid()}
        >
          {registerMutation.isPending
            ? t("auth.creatingAccount")
            : t("auth.signUp")}
        </Button>

        <p className="text-center text-sm text-[#6a6a8a]">
          {t("auth.haveAccount")}{" "}
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
