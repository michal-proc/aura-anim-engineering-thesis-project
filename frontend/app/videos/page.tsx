"use client";

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/common/sidebar";
import { Header } from "@/components/common/header";
import { VideoCard } from "@/components/common/video-card";
import { useI18n } from "@/lib/i18n-context";
import { useVideoStore } from "@/store/video-store";
import { videoApi } from "@/api/video";
import { useAuthStore } from "@/store/auth-store";
import { PulseLoader } from "react-spinners";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ProtectedRoute } from "@/components/auth/protected-route";

export default function VideosPage() {
  const { t } = useI18n();
  const router = useRouter();
  const { videos, setVideos } = useVideoStore();
  const { accessToken, isInitialized } = useAuthStore();

  const { data, isLoading, error } = useQuery({
    queryKey: ["videos", accessToken],
    queryFn: async () => {
      try {
        if (!accessToken) {
          throw new Error("No access token available");
        }
        const response = await videoApi.getVideos(accessToken);
        // Ensure we always return the expected structure
        if (!response || !response.data) {
          return [];
        }
        return response.data;
      } catch (err) {
        //console.error("[v0] Error fetching videos:", err)
        throw err;
      }
    },
    enabled: isInitialized && !!accessToken,
    retry: 1,
  });

  useEffect(() => {
    if (data) {
      console.log(data);
      setVideos(data);
    }
  }, [data, setVideos]);

  const completedVideos =
    videos?.filter((video) => video.job?.status === "completed") || [];

  return (
    <ProtectedRoute>
      <div className="flex h-screen text-white">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-auto p-8">
            <div className="max-w-7xl mx-auto">
              <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-[#31B7EA] via-[#375DDA] to-[#B949A3] bg-clip-text text-transparent">
                {t("page.videos.title")}
              </h1>
              <p className="text-[#8a8aa8] mb-8">
                {t("page.videos.description")}
              </p>

              {isLoading && (
                <div className="flex items-center justify-center py-20">
                  <PulseLoader color="#31B7EA" size={15} />
                </div>
              )}

              {error && (
                <div className="text-center py-20">
                  <p className="text-red-400">{t("page.videos.error")}</p>
                </div>
              )}

              {!isLoading && !error && completedVideos.length === 0 && (
                <div className="flex flex-col items-center justify-center py-20 space-y-6">
                  <div className="text-center space-y-2">
                    <h3 className="text-xl font-semibold text-[#8a8aa8]">
                      {t("page.videos.emptyTitle")}
                    </h3>
                    <p className="text-[#6a6a88]">
                      {t("page.videos.emptyDescription")}
                    </p>
                  </div>
                  <Button
                    onClick={() => router.push("/videos/create")}
                    size="lg"
                    className="bg-gradient-to-r from-[#31B7EA] to-[#375DDA] hover:opacity-90 transition-opacity flex items-center gap-2 cursor-pointer"
                  >
                    <Plus className="w-5 h-5 mr-2" />
                    {t("page.videos.createButton")}
                  </Button>
                </div>
              )}

              {!isLoading && !error && completedVideos.length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {completedVideos.map((video) => (
                    <VideoCard key={video.id} video={video} />
                  ))}
                </div>
              )}
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
