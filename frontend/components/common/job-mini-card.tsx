"use client";

import type React from "react";

import {
  FaTimes,
  FaCheck,
  FaExclamationTriangle,
  FaSpinner,
} from "react-icons/fa";
import type { Job } from "@/types/video.types";
import { useTranslations } from "@/lib/i18n-context";
import { videoApi } from "@/api/video";
import { useState } from "react";
import { useRouter } from "next/navigation";

interface JobMiniCardProps {
  job: Job;
  onRemove: (jobId: string) => void;
}

export function JobMiniCard({ job, onRemove }: JobMiniCardProps) {
  const { t } = useTranslations();
  const router = useRouter();
  const [isCanceling, setIsCanceling] = useState(false);

  const handleCancel = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsCanceling(true);
    try {
      await videoApi.cancelJob(job.job_id);
      onRemove(job.job_id);
    } catch (error) {
      // Nothing to do
    } finally {
      setIsCanceling(false);
    }
  };

  const handleClick = () => {
    router.push("/jobs");
  };

  const getStatusColor = () => {
    switch (job.status) {
      case "completed":
        return "text-green-400";
      case "failed":
        return "text-red-400";
      case "cancelled":
        return "text-orange-400";
      case "processing":
        return "text-cyan-400";
      default:
        return "text-gray-400";
    }
  };

  const getStatusIcon = () => {
    switch (job.status) {
      case "completed":
        return <FaCheck className="text-green-400" />;
      case "failed":
        return <FaExclamationTriangle className="text-red-400" />;
      case "processing":
        return <FaSpinner className="text-cyan-400 animate-spin" />;
      default:
        return null;
    }
  };

  const isFinalState =
    job.status === "completed" ||
    job.status === "failed" ||
    job.status === "cancelled";
  const canCancel = job.status === "pending" || job.status === "processing";

  return (
    <div
      onClick={handleClick}
      className={`p-4 border-b border-white/10 hover:bg-white/5 transition-all cursor-pointer ${
        isFinalState ? "bg-white/3" : ""
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          {/* Job Name */}
          <div className="flex items-center gap-2 mb-2">
            {getStatusIcon()}
            <h4 className="font-medium text-white truncate text-sm">
              {job.parameters.prompt.substring(0, 40)}
              {job.parameters.prompt.length > 40 ? "..." : ""}
            </h4>
          </div>

          {/* Progress Bar */}
          <div className="mb-2">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className={`${getStatusColor()}`}>
                {t(`page.jobs.${job.status}`)}
              </span>
              <span className="text-gray-400">{job.progress_percentage}%</span>
            </div>
            <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ease-out ${
                  job.status === "completed"
                    ? "bg-green-400"
                    : job.status === "failed"
                      ? "bg-red-400"
                      : job.status === "cancelled"
                        ? "bg-orange-400"
                        : "bg-gradient-to-r from-cyan-400 to-blue-500"
                }`}
                style={{ width: `${job.progress_percentage}%` }}
              />
            </div>
          </div>

          {/* Current Step */}
          {job.current_step && (
            <p className="text-xs text-gray-400 truncate">{job.current_step}</p>
          )}
        </div>

        {/* Cancel Button */}
        {canCancel && (
          <button
            onClick={handleCancel}
            disabled={isCanceling}
            className="flex-shrink-0 p-1.5 rounded-lg hover:bg-red-500/20 text-red-400 hover:text-red-300 transition-colors disabled:opacity-50 cursor-pointer disabled:cursor-not-allowed"
            aria-label={t("jobs.cancel")}
          >
            {isCanceling ? (
              <FaSpinner className="animate-spin" size={14} />
            ) : (
              <FaTimes size={14} />
            )}
          </button>
        )}
      </div>
    </div>
  );
}
