"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ClipLoader } from "react-spinners";
import { videoApi } from "@/api/video";
import type { Video } from "@/types/video.types";
import { Clock, VideoIcon } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";

interface VideoCardProps {
  video: Video;
}

export function VideoCard({ video }: VideoCardProps) {
  const router = useRouter();
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { accessToken } = useAuthStore();

  useEffect(() => {
    if (!containerRef.current) return;

    const observer = new IntersectionObserver(
      async (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting && !videoUrl && !error) {
          try {
            setIsLoading(true);
            const blob = await videoApi.getVideoFile(video.id, accessToken);
            console.log(blob);
            const url = URL.createObjectURL(blob);
            setVideoUrl(url);
          } catch (err) {
            setError(true);
          } finally {
            setIsLoading(false);
          }
        }
      },
      {
        threshold: 0.1,
        rootMargin: "50px",
      },
    );

    observer.observe(containerRef.current);

    return () => {
      observer.disconnect();
      if (videoUrl) {
        URL.revokeObjectURL(videoUrl);
      }
    };
  }, [video.id, videoUrl, error]);

  const duration = video.job?.parameters?.video_length || 0;
  const quality = video.job?.parameters
    ? `${video.job.parameters.width}x${video.job.parameters.height}`
    : "Unknown";

  return (
    <div
      ref={containerRef}
      onClick={() => router.push(`/videos/${video.id}`)}
      className="bg-[#1a1a2e] rounded-xl overflow-hidden border border-[#252540] hover:border-[#31B7EA] transition-all duration-300 group cursor-pointer"
    >
      <div className="aspect-video bg-[#0f0f1e] relative flex items-center justify-center overflow-hidden">
        {isLoading && !error && <ClipLoader color="#31B7EA" size={40} />}
        {error && (
          <div className="text-red-400 text-sm">Failed to load video</div>
        )}
        {videoUrl && !error && (
          <video
            ref={videoRef}
            src={videoUrl}
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
            onLoadedData={() => setIsLoading(false)}
          />
        )}
      </div>
      <div className="p-4">
        <h3 className="text-white font-medium truncate group-hover:text-[#31B7EA] transition-colors">
          {video.name}
        </h3>
        <div className="mt-2 flex items-center gap-3 text-xs text-[#8a8aa8]">
          <div className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            <span>{duration}s</span>
          </div>
          <div className="flex items-center gap-1">
            <VideoIcon className="w-3.5 h-3.5" />
            <span>{quality}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
