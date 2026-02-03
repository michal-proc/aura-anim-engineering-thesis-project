"use client";

import { useState, useEffect } from "react";
import { FaBriefcase } from "react-icons/fa";
import { useJobMonitor } from "@/hooks/use-job-monitor";
import { useAuthStore } from "@/store/auth-store";
import { JobMiniCard } from "./job-mini-card";
import { useRouter } from "next/navigation";
import { useTranslations } from "@/lib/i18n-context";

export function JobFloatingPanel() {
  const { activeJobs, removeJob, initializeJobs } = useJobMonitor();
  const { accessToken, isInitialized } = useAuthStore();
  const router = useRouter();
  const { t } = useTranslations();
  const [isMinimized, setIsMinimized] = useState(false);

  useEffect(() => {
    if (isInitialized && accessToken) {
      initializeJobs(accessToken);
    }
  }, [isInitialized, accessToken, initializeJobs]);

  if (activeJobs.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 w-96 max-w-[calc(100vw-3rem)]">
      <div className="rounded-lg border border-white/10 bg-gradient-to-br from-[#1a1a2e]/95 via-[#0f0f1a]/95 to-[#0b0219]/95 backdrop-blur-xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div
          className="flex items-center justify-between px-4 py-3 border-b border-white/10 cursor-pointer hover:bg-white/5 transition-colors"
          onClick={() => setIsMinimized(!isMinimized)}
        >
          <div className="flex items-center gap-2">
            <FaBriefcase className="text-cyan-400" />
            <h3 className="font-semibold text-white">
              {t("jobs.activeJobs")} ({activeJobs.length})
            </h3>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation();
              router.push("/jobs");
            }}
            className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors cursor-pointer"
            aria-label={t("jobs.viewAll")}
          >
            {t("jobs.viewAll")}
          </button>
        </div>

        {/* Job List */}
        <div
          className={`transition-all duration-300 ease-in-out overflow-hidden ${
            !isMinimized ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
          }`}
        >
          <div className="overflow-y-auto">
            {activeJobs.map((job) => (
              <JobMiniCard key={job.job_id} job={job} onRemove={removeJob} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
