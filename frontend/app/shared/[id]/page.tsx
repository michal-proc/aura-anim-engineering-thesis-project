"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { videoApi } from "@/api/video";
import { PulseLoader } from "react-spinners";
import { FaHome, FaPlay } from "react-icons/fa";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import Image from "next/image";
import { LanguageSwitcher } from "@/components/common/language-switcher";
import {useI18n} from "@/lib/i18n-context";

export default function SharedVideoPage() {
  const params = useParams();
  const videoId = params.id as string;
  const { t } = useI18n();
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ["shared-video", videoId],
    queryFn: () => videoApi.getSharedVideo(videoId),
  });

  const video = data?.data;

  useEffect(() => {
    if (video) {
      videoApi.getVideoFile(videoId).then((blob) => {
        const url = URL.createObjectURL(blob);
        setVideoUrl(url);
      });
    }

    return () => {
      if (videoUrl) {
        URL.revokeObjectURL(videoUrl);
      }
    };
  }, [video, videoId]);

  if (isLoading) {
    return (
      <div className="min-h-screen relative flex items-center justify-center p-4">
        <Link
          href="/"
          className="absolute top-6 left-6 z-20 hover:scale-110 transition-transform duration-200"
        >
          <Image
            src="/logo.png"
            alt="Logo"
            width={48}
            height={48}
            className="drop-shadow-[0_0_15px_rgba(49,183,234,0.5)]"
          />
        </Link>

        <div className="absolute bottom-6 left-6 z-20">
          <LanguageSwitcher />
        </div>

        <div className="w-full max-w-6xl relative z-10 flex items-center justify-center">
          <PulseLoader color="#31B7EA" size={15} />
        </div>
      </div>
    );
  }

  if (error || !video) {
    return (
      <div className="min-h-screen relative flex items-center justify-center p-4">
        <Link
          href="/"
          className="absolute top-6 left-6 z-20 hover:scale-110 transition-transform duration-200"
        >
          <Image
            src="/logo.png"
            alt="Logo"
            width={48}
            height={48}
            className="drop-shadow-[0_0_15px_rgba(49,183,234,0.5)]"
          />
        </Link>

        <div className="absolute bottom-6 left-6 z-20">
          <LanguageSwitcher />
        </div>

        <div className="w-full max-w-6xl relative z-10 flex flex-col items-center justify-center space-y-4">
          <h1 className="text-2xl font-bold text-white">{ t("shared.notFound") }</h1>
          <p className="text-[#8a8aa8]">
            { t("shared.notFoundDescription") }
          </p>
          <Link href="/">
            <Button className="bg-gradient-to-r from-[#31B7EA] to-[#6366F1] flex items-center gap-2">
              <FaHome />
              <span>Go to Homepage</span>
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative flex items-center justify-center p-4">
      <Link
        href="/"
        className="absolute top-6 left-6 z-20 hover:scale-110 transition-transform duration-200"
      >
        <Image
          src="/logo.png"
          alt="Logo"
          width={48}
          height={48}
          className="drop-shadow-[0_0_15px_rgba(49,183,234,0.5)]"
        />
      </Link>

      <div className="absolute bottom-6 left-6 z-20">
        <LanguageSwitcher />
      </div>

      <main className="max-w-6xl w-full relative z-10 space-y-8">
        <div className="bg-[#1a1a2e]/80 backdrop-blur-md rounded-2xl overflow-hidden border border-[#2a2a4e] shadow-2xl">
          <div className="aspect-video bg-[#0a0a0f] relative">
            {videoUrl ? (
              <video
                src={videoUrl}
                controls
                autoPlay
                className="w-full h-full"
              />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center">
                <PulseLoader color="#31B7EA" size={15} />
              </div>
            )}
          </div>
        </div>

        <div className="bg-[#1a1a2e]/80 backdrop-blur-md rounded-2xl p-8 border border-[#2a2a4e]">
          <h2 className="text-3xl font-bold text-white mb-4">{video.name}</h2>
          <p className="text-[#8a8aa8] text-base mb-6">
            {video.job.parameters.prompt}
          </p>
          <div className="flex flex-wrap gap-6 text-base">
            <div className="flex items-center gap-2">
              <span className="text-[#6a6a88]">{t("video.resolution")}:</span>
              <span className="text-white font-mono">
                {video.job.parameters.width}x{video.job.parameters.height}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[#6a6a88]">{t("video.fps")}:</span>
              <span className="text-white font-mono">
                {video.job.parameters.fps}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[#6a6a88]">{t("video.length")}:</span>
              <span className="text-white font-mono">
                {video.job.parameters.video_length}s
              </span>
            </div>
          </div>
        </div>

        <div className="flex justify-center">
          <Link href="/">
            <Button
              size="lg"
              className="bg-gradient-to-r from-[#31B7EA] to-[#6366F1] hover:opacity-90 flex items-center gap-2 cursor-pointer"
            >
              <FaPlay />
              <span>{ t("shared.createYourOwn") }</span>
            </Button>
          </Link>
        </div>
      </main>
    </div>
  );
}
