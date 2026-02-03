"use client";

import type React from "react";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { FaEnvelope, FaLock, FaEye, FaEyeSlash } from "react-icons/fa";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { useAuthStore } from "@/store/auth-store";
import { authApi } from "@/api/auth";
import { useI18n } from "@/lib/i18n-context";
import type { LoginUserPayload } from "@/types/auth.types";

export default function LoginPage() {
  const router = useRouter();
  const { t } = useI18n();
  const { setAuth, isAuthenticated, isInitialized } = useAuthStore();
  const [formData, setFormData] = useState<LoginUserPayload>({
    email: "",
    password: "",
    remember_me: false,
  });
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [passwordValidation, setPasswordValidation] = useState({
    minLength: false,
    hasUppercase: false,
    hasLowercase: false,
    hasNumber: false,
  });

  useEffect(() => {
    const password = formData.password;
    setPasswordValidation({
      minLength: password.length >= 8,
      hasUppercase: /[A-Z]/.test(password),
      hasLowercase: /[a-z]/.test(password),
      hasNumber: /[0-9]/.test(password),
    });
  }, [formData.password]);

  const loginMutation = useMutation({
    mutationFn: async (payload: LoginUserPayload) => {
      return await authApi.login(payload);
    },
    onSuccess: async (response) => {
      let user = response.user;

      // If user not in response, fetch it (real API flow)
      if (!user && response.access_token) {
        try {
          user = await authApi.getCurrentUser(response.access_token);
        } catch (error) {
          return;
        }
      }

      if (user) {
        setAuth(user, response.access_token, response.refresh_token);
        router.push("/");
      }
    },
  });

  if (!isInitialized) {
    return (
      <div className="bg-[#0f0f1a] rounded-2xl p-8 border border-[#1a1a2e] shadow-2xl">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#31B7EA] mx-auto"></div>
          <p className="text-[#6a6a8a] mt-4">{t("dashboard.loading")}</p>
        </div>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const allRequirementsMet = Object.values(passwordValidation).every(Boolean);
    if (!allRequirementsMet) {
      return; // Don't submit if password doesn't meet requirements
    }

    loginMutation.mutate(formData);
  };

  const getErrorMessage = () => {
    if (!loginMutation.isError || !loginMutation.error) return "";

    const error = loginMutation.error as any;
    if (error.error?.code === "INVALID_CREDENTIALS") {
      return t("auth.invalidCredentials");
    }
    return t("auth.errorOccurred");
  };

  return (
    <div className="bg-[#0f0f1a] rounded-2xl p-8 border border-[#1a1a2e] shadow-2xl">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-[#31B7EA] via-[#375DDA] to-[#B949A3] bg-clip-text text-transparent mb-2">
          {t("auth.welcomeBack")}
        </h1>
        <p className="text-[#6a6a8a]">{t("auth.signInDescription")}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {loginMutation.isError && (
          <div className="bg-[#fe7070]/10 border border-[#fe7070] text-[#fe7070] px-4 py-3 rounded-lg text-sm">
            {getErrorMessage()}
          </div>
        )}

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
              type={showPassword ? "text" : "password"}
              value={formData.password}
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
              onFocus={() => setIsPasswordFocused(true)}
              onBlur={() => setIsPasswordFocused(false)}
              className="w-full bg-[#1a1a2e] border border-[#2a2a3e] rounded-lg pl-10 pr-12 py-3 text-white focus:border-[#31B7EA] transition-colors"
              placeholder={t("auth.enterPassword")}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#6a6a8a] hover:text-white transition-colors cursor-pointer"
            >
              {showPassword ? (
                <FaEyeSlash className="w-5 h-5" />
              ) : (
                <FaEye className="w-5 h-5" />
              )}
            </button>
          </div>
          {isPasswordFocused && (
            <div className="mt-2 p-3 bg-[#1a1a2e] border border-[#2a2a3e] rounded-lg text-sm space-y-1">
              <p className="text-[#6a6a8a] mb-2">
                {t("auth.passwordRequirements")}
              </p>
              <div className="space-y-1">
                <div
                  className={`flex items-center gap-2 ${passwordValidation.minLength ? "text-green-500" : "text-[#6a6a8a]"}`}
                >
                  <span>{passwordValidation.minLength ? "✓" : "○"}</span>
                  <span>{t("auth.minLength")}</span>
                </div>
                <div
                  className={`flex items-center gap-2 ${passwordValidation.hasUppercase ? "text-green-500" : "text-[#6a6a8a]"}`}
                >
                  <span>{passwordValidation.hasUppercase ? "✓" : "○"}</span>
                  <span>{t("auth.hasUppercase")}</span>
                </div>
                <div
                  className={`flex items-center gap-2 ${passwordValidation.hasLowercase ? "text-green-500" : "text-[#6a6a8a]"}`}
                >
                  <span>{passwordValidation.hasLowercase ? "✓" : "○"}</span>
                  <span>{t("auth.hasLowercase")}</span>
                </div>
                <div
                  className={`flex items-center gap-2 ${passwordValidation.hasNumber ? "text-green-500" : "text-[#6a6a8a]"}`}
                >
                  <span>{passwordValidation.hasNumber ? "✓" : "○"}</span>
                  <span>{t("auth.hasNumber")}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 cursor-pointer group">
            <Checkbox
              checked={formData.remember_me}
              onCheckedChange={(checked) =>
                setFormData({ ...formData, remember_me: checked === true })
              }
            />
            <span className="text-sm text-[#6a6a8a] group-hover:text-white transition-colors">
              {t("auth.rememberMe")}
            </span>
          </label>
          <Link
            href="/forgot-password"
            className="text-sm text-[#31B7EA] hover:text-[#358EE3]"
          >
            {t("auth.forgotPassword")}
          </Link>
        </div>

        <Button
          type="submit"
          variant="blue"
          className="w-full"
          disabled={
            loginMutation.isPending ||
            !Object.values(passwordValidation).every(Boolean)
          }
        >
          {loginMutation.isPending ? t("auth.signingIn") : t("auth.signIn")}
        </Button>

        <p className="text-center text-sm text-[#6a6a8a]">
          {t("auth.noAccount")}{" "}
          <Link
            href="/register"
            className="text-[#31B7EA] hover:text-[#358EE3] font-medium"
          >
            {t("auth.signUp")}
          </Link>
        </p>

        <p className="text-center text-sm text-[#6a6a8a]">
          {t("auth.accountDeactivated")}{" "}
          <Link
            href="/reactivate"
            className="text-[#31B7EA] hover:text-[#358EE3] font-medium"
          >
            {t("auth.reactivateHere")}
          </Link>
        </p>
      </form>
    </div>
  );
}
