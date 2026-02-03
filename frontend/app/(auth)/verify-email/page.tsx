"use client";

import Link from "next/link";
import { FaEnvelopeOpen } from "react-icons/fa";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n-context";

export default function VerifyEmailPage() {
  const { t } = useI18n();

  return (
    <div className="bg-[#0f0f1a] rounded-2xl p-8 border border-[#1a1a2e] shadow-2xl text-center">
      <div className="mb-6">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-[#31B7EA] to-[#B949A3] mb-4">
          <FaEnvelopeOpen className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-[#31B7EA] via-[#375DDA] to-[#B949A3] bg-clip-text text-transparent mb-2">
          {t("auth.verifyEmailTitle")}
        </h1>
        <p className="text-[#6a6a8a] max-w-sm mx-auto">
          {t("auth.verifyEmailDescription")}
        </p>
      </div>

      <div className="space-y-4 mb-4">
        <Link href="/login">
          <Button variant="blue" className="w-full">
            {t("auth.backToLoginButton")}
          </Button>
        </Link>
      </div>

      <p className="text-sm text-[#6a6a8a]">
        {t("auth.didntReceiveEmail")}{" "}
        <button className="text-[#31B7EA] hover:text-[#358EE3] font-medium">
          {t("auth.resend")}
        </button>
      </p>
    </div>
  );
}
