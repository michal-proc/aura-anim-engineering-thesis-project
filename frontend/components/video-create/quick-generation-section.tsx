"use client";

import type React from "react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { FaRocket, FaChevronDown, FaInfoCircle } from "react-icons/fa";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useI18n } from "@/lib/i18n-context";
import { videoApi } from "@/api/video";
import { useAuthStore } from "@/store/auth-store";
import { toast } from "sonner";
import { useJobMonitor } from "@/hooks/use-job-monitor";

interface QuickGenerationSectionProps {
  isOpen: boolean;
  onToggle: () => void;
  prefillData?: {
    prompt?: string;
    video_length?: number;
  };
}

function InfoTooltip({ content }: { content: string }) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            type="button"
            className="ml-1 text-[#8a8aa8] hover:text-white transition-colors cursor-pointer"
          >
            <FaInfoCircle className="w-3.5 h-3.5" />
          </button>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-xs">
          <p className="text-sm">{content}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

export function QuickGenerationSection({
  isOpen,
  onToggle,
  prefillData,
}: QuickGenerationSectionProps) {
  const { t } = useI18n();
  const router = useRouter();
  const { accessToken } = useAuthStore();
  const { initializeJobs } = useJobMonitor();

  const [prompt, setPrompt] = useState("");
  const [length, setLength] = useState(5);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    if (prefillData?.prompt) {
      setPrompt(prefillData.prompt);
    }
    if (prefillData?.video_length) {
      setLength(prefillData.video_length);
    }
  }, [prefillData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: Record<string, string> = {};
    if (!prompt.trim()) {
      newErrors.prompt = t("create.quick.promptRequired");
    }
    if (length < 1) {
      newErrors.length = t("create.quick.lengthMin");
    }

    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) return;

    if (!accessToken) {
      toast.error("You must be logged in to generate videos");
      return;
    }

    setIsGenerating(true);
    try {
      const payload = {
        prompt: prompt,
        negative_prompt: "",
        aspect_ratio: [16, 9],
        resolution: 720,
        video_length: length,
        fps: 24,
        output_format: "mp4",
        base_model: "sd15",
        motion_adapter: "default",
        inference_steps: 25,
      };

      const response = await videoApi.generateVideo(payload, accessToken);

      toast.success("Video generation started successfully!");
      await initializeJobs(accessToken);
      router.push("/jobs");
    } catch (error) {
      toast.error("Failed to start video generation. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="bg-[#1a1a2e] rounded-xl border border-[#2a2a4e] overflow-hidden">
      <button
        type="button"
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-[#1f1f3a] transition-colors cursor-pointer"
      >
        <div className="flex items-center gap-3">
          <FaRocket className="text-[#31B7EA] text-xl" />
          <h2 className="text-xl font-semibold text-white">
            {t("create.quick.title")}
          </h2>
        </div>
        <FaChevronDown
          className={`text-[#8a8aa8] transition-transform duration-300 ${isOpen ? "rotate-180" : ""}`}
        />
      </button>

      <div
        className={`transition-all duration-300 ease-in-out overflow-hidden ${
          isOpen ? "max-h-[1000px] opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <form
          onSubmit={handleSubmit}
          className="p-4 pt-2 border-t border-[#2a2a4e]"
        >
          <div className="space-y-2">
            <div className="flex flex-col gap-0">
              <label className="flex items-center text-base font-medium text-white mb-2">
                {t("create.quick.promptLabel")}{" "}
                <span className="text-red-400 ml-1">*</span>
                <InfoTooltip content={t("create.quick.promptTooltip")} />
              </label>
              <textarea
                value={prompt}
                onChange={(e) => {
                  setPrompt(e.target.value);
                  if (errors.prompt) setErrors({ ...errors, prompt: "" });
                }}
                placeholder={t("create.quick.promptPlaceholder")}
                rows={4}
                className={`w-full bg-[#0f0f1e] border rounded-lg px-4 py-3 text-white placeholder-[#5a5a78] focus:outline-none focus:border-[#31B7EA] resize-none ${
                  errors.prompt ? "border-red-500" : "border-[#2a2a4e]"
                }`}
              />
              {errors.prompt && (
                <p className="text-red-400 text-sm mt-1">{errors.prompt}</p>
              )}
            </div>

            <div>
              <label className="flex items-center text-base font-medium text-white mb-2">
                {t("create.quick.lengthLabel")}{" "}
                <span className="text-red-400 ml-1">*</span>
                <InfoTooltip content={t("create.quick.lengthTooltip")} />
              </label>
              <input
                type="number"
                value={length}
                onChange={(e) => {
                  setLength(Number(e.target.value));
                  if (errors.length) setErrors({ ...errors, length: "" });
                }}
                min={1}
                className={`w-full bg-[#0f0f1e] border rounded-lg px-4 py-2 text-white focus:outline-none focus:border-[#31B7EA] ${
                  errors.length ? "border-red-500" : "border-[#2a2a4e]"
                }`}
              />
              {errors.length && (
                <p className="text-red-400 text-sm mt-1">{errors.length}</p>
              )}
            </div>

            <Button
              type="submit"
              disabled={isGenerating}
              variant="blue"
              size="md"
              className="w-full"
            >
              {isGenerating
                ? t("create.quick.generating")
                : t("create.quick.generateButton")}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
