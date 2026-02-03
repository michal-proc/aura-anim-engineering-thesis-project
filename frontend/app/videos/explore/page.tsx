"use client";

import { useQuery } from "@tanstack/react-query";
import { videoApi } from "@/api/video";
import { useI18n } from "@/lib/i18n-context";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/common/sidebar";
import { Header } from "@/components/common/header";
import { ExploreVideoCard } from "@/components/common/explore-video-card";
import { PulseLoader } from "react-spinners";

export default function ExplorePage() {
  const { t } = useI18n();

  const { data, isLoading, error } = useQuery({
    queryKey: ["explore-videos"],
    queryFn: async () => {
      try {
        const response = await videoApi.getExploreVideos();

        if (!response.data) {
          return [];
        }

        return response.data;
      } catch (error) {
        throw error;
      }
    },
  });

  const videos = data || [];
  console.log("[v0] Rendered videos:", videos);
  console.log("[v0] Videos length:", videos.length);

  return (
    <ProtectedRoute>
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto p-8">
            <div className="max-w-7xl mx-auto">
              <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-[#31B7EA] via-[#375DDA] to-[#B949A3] bg-clip-text text-transparent">
                {t("page.explore.title")}
              </h1>
              <p className="text-[#8a8aa8] mb-8">
                {t("page.explore.description")}
              </p>

              {isLoading && (
                <div className="flex items-center justify-center py-20">
                  <PulseLoader color="#31B7EA" size={15} />
                </div>
              )}

              {error && (
                <div className="text-center py-20">
                  <p className="text-red-400 mb-4">{t("page.explore.error")}</p>
                  <button
                    onClick={() => (window.location.href = "/videos")}
                    className="px-4 py-2 bg-[#31B7EA] text-white rounded-lg hover:bg-[#2a9ed4] transition-colors"
                  >
                    {t("common.backToVideos")}
                  </button>
                </div>
              )}

              {!isLoading && !error && videos.length === 0 && (
                <div className="text-center py-20">
                  <p className="text-[#8a8aa8]">{t("page.explore.empty")}</p>
                </div>
              )}

              {!isLoading && !error && videos.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {videos.map((video, index) => (
                    <ExploreVideoCard
                      key={`${video.url}-${index}`}
                      video={video}
                      index={index}
                    />
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
