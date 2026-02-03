"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { videoApi } from "@/api/video";
import { useI18n } from "@/lib/i18n-context";
import { useAuthStore } from "@/store/auth-store";
import { Sidebar } from "@/components/common/sidebar";
import { Header } from "@/components/common/header";
import { PulseLoader } from "react-spinners";
import { FaCheck, FaClock, FaSpinner, FaTimes, FaBan } from "react-icons/fa";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import type { JobStatus } from "@/types/video.types";
import { ProtectedRoute } from "@/components/auth/protected-route";

export default function JobsPage() {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const router = useRouter();
  const { accessToken, isInitialized } = useAuthStore();

  const { data, isLoading, error } = useQuery({
    queryKey: ["jobs", accessToken],
    queryFn: async () => {
      if (!accessToken) {
        throw new Error("No access token available");
      }
      try {
        const response = await videoApi.getJobs(accessToken);
        return { data: response.data, meta: response.meta };
      } catch (err) {
        throw err;
      }
    },
    enabled: isInitialized && !!accessToken,
    refetchInterval: 5000,
  });

  const cancelJobMutation = useMutation({
    mutationFn: (jobId: string) => videoApi.cancelJob(jobId, accessToken || ""),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });

  const jobs = data?.data
    ? [...data.data].sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      )
    : [];

  const meta = data?.meta;

  const getStatusIcon = (status: JobStatus) => {
    switch (status) {
      case "completed":
        return <FaCheck className="text-green-400" />;
      case "processing":
        return <FaSpinner className="text-blue-400 animate-spin" />;
      case "failed":
        return <FaTimes className="text-red-400" />;
      case "cancelled":
        return <FaBan className="text-gray-400" />;
      default:
        return <FaClock className="text-yellow-400" />;
    }
  };

  const getStatusColor = (status: JobStatus) => {
    switch (status) {
      case "completed":
        return "text-green-400";
      case "processing":
        return "text-blue-400";
      case "failed":
        return "text-red-400";
      case "cancelled":
        return "text-gray-400";
      default:
        return "text-yellow-400";
    }
  };

  const canCancelJob = (status: JobStatus) => {
    return status === "pending" || status === "processing";
  };

  const isJobCompleted = (status: JobStatus) => {
    return status === "completed";
  };

  return (
    <ProtectedRoute>
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto p-8">
            <div className="max-w-7xl mx-auto">
              <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-[#31B7EA] via-[#375DDA] to-[#B949A3] bg-clip-text text-transparent">
                {t("page.jobs.title")}
              </h1>
              <p className="text-[#8a8aa8] mb-6">
                {t("page.jobs.description")}
              </p>

              {isLoading && (
                <div className="flex items-center justify-center py-20">
                  <PulseLoader color="#31B7EA" size={15} />
                </div>
              )}

              {error && (
                <div className="text-center py-20">
                  <p className="text-red-400">{t("page.jobs.error")}</p>
                </div>
              )}

              {!isLoading && !error && jobs.length === 0 && (
                <div className="text-center py-20">
                  <p className="text-[#8a8aa8]">{t("page.jobs.empty")}</p>
                </div>
              )}

              {!isLoading && !error && jobs.length > 0 && (
                <div className="bg-[#1a1a2e] rounded-xl border border-[#2a2a4e] overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-[#2a2a4e]">
                          <th className="text-left p-4 text-[#8a8aa8] font-medium">
                            {t("table.status")}
                          </th>
                          <th className="text-left p-4 text-[#8a8aa8] font-medium">
                            {t("table.prompt")}
                          </th>
                          <th className="text-left p-4 text-[#8a8aa8] font-medium">
                            {t("table.step")}
                          </th>
                          <th className="text-left p-4 text-[#8a8aa8] font-medium">
                            {t("table.progress")}
                          </th>
                          <th className="text-left p-4 text-[#8a8aa8] font-medium">
                            {t("table.created")}
                          </th>
                          <th className="text-left p-4 text-[#8a8aa8] font-medium">
                            {t("table.actions")}
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {jobs.map((job) => (
                          <tr
                            key={job.job_id}
                            className="border-b border-[#2a2a4e] hover:bg-[#252540] transition-colors"
                          >
                            <td className="p-4">
                              <div className="flex items-center gap-2">
                                {getStatusIcon(job.status)}
                                <span
                                  className={`${getStatusColor(job.status)}`}
                                >
                                  {t(`page.jobs.${job.status}`)}
                                </span>
                              </div>
                            </td>
                            <td className="p-4 text-[#8a8aa8] text-sm max-w-xs">
                              <div
                                className="truncate"
                                title={job.parameters.prompt}
                              >
                                {job.parameters.prompt}
                              </div>
                            </td>
                            <td className="p-4 text-[#8a8aa8] text-sm">
                              {job.current_step || "-"}
                            </td>
                            <td className="p-4">
                              <div className="flex items-center gap-3">
                                <div className="flex-1 bg-[#0a0a0f] rounded-full h-2 overflow-hidden min-w-[100px]">
                                  <div
                                    className="h-full bg-gradient-to-r from-[#31B7EA] to-[#375DDA] transition-all duration-300"
                                    style={{
                                      width: `${job.progress_percentage}%`,
                                    }}
                                  />
                                </div>
                                <span className="text-[#8a8aa8] text-sm min-w-[3rem]">
                                  {job.progress_percentage}%
                                </span>
                              </div>
                            </td>
                            <td className="p-4 text-[#8a8aa8] text-sm">
                              {new Date(job.created_at).toLocaleString()}
                            </td>
                            <td className="p-4">
                              <div className="flex items-center gap-2">
                                {canCancelJob(job.status) && (
                                  <Button
                                    onClick={() =>
                                      cancelJobMutation.mutate(job.job_id)
                                    }
                                    disabled={cancelJobMutation.isPending}
                                    variant="outline"
                                    size="sm"
                                    className="border-red-500/50 text-red-400 hover:bg-red-500/10"
                                  >
                                    {t("jobs.cancel")}
                                  </Button>
                                )}
                                {isJobCompleted(job.status) && job.vid_id && (
                                  <Button
                                    onClick={() =>
                                      router.push(`/videos/${job.vid_id}`)
                                    }
                                    variant="outline"
                                    size="sm"
                                    className="border-[#31B7EA]/50 text-[#31B7EA] hover:bg-[#31B7EA]/10 flex items-center gap-2"
                                  >
                                    {t("jobs.show")}
                                  </Button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
