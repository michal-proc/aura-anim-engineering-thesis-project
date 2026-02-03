"use client";

import { useEffect, useRef, useState } from "react";
import { FaDownload } from "react-icons/fa";
import { PulseLoader } from "react-spinners";
import type { VideoExplore } from "@/types/video.types";

interface ExploreVideoCardProps {
  video: VideoExplore;
  index?: number;
}

export function ExploreVideoCard({ video, index = 0 }: ExploreVideoCardProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [shouldLoad, setShouldLoad] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting) {
          setShouldLoad(true);
          observer.disconnect();
        }
      },
      {
        threshold: 0.1,
        rootMargin: "100px",
      },
    );

    observer.observe(containerRef.current);

    return () => {
      observer.disconnect();
    };
  }, []);

  const handleDownload = async () => {
    try {
      const response = await fetch(video.url);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${video.name}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      //
    }
  };

  const animationDelay = (index % 4) * 0.1;
  const scaleVariation = 1 + (index % 3) * 0.02;

  return (
    <div
      ref={containerRef}
      className="bg-[#1a1a2e] rounded-xl overflow-hidden border border-[#2a2a4e] hover:border-[#375DDA] transition-all duration-300 group"
      style={{
        animationDelay: `${animationDelay}s`,
        transform: `scale(${scaleVariation})`,
      }}
    >
      <div className="aspect-square relative bg-[#0a0a0f] overflow-hidden">
        {shouldLoad && isLoading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <PulseLoader color="#31B7EA" size={10} />
          </div>
        )}
        {shouldLoad && (
          <video
            src={video.url}
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
            onLoadedData={() => setIsLoading(false)}
          />
        )}
      </div>

      <div className="p-4 flex items-center justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-white text-lg">{video.name}</h3>
          <p className="text-sm text-[#8a8aa8] line-clamp-2 leading-snug mt-2">
            {video.prompt}
          </p>
        </div>
        <button
          onClick={handleDownload}
          className="flex-shrink-0 p-3 hover:bg-[#252540] text-[#31B7EA] hover:text-white transition-colors rounded-lg cursor-pointer"
          aria-label="Download video"
        >
          <FaDownload className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
