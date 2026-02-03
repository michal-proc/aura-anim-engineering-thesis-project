"use client";

import type React from "react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { FaCog, FaChevronDown, FaInfoCircle } from "react-icons/fa";
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

type AspectRatio = [number, number];
type ResolutionClass = 128 | 256 | 480 | 512 | 720 | 1024 | 2048 | 4096;
type VideoFPS = 8 | 16 | 24 | 32;
type BaseGenerationModel =
  | "sd15"
  | "epicrealism"
  | "realistic_vision"
  | "dreamshaper"
  | "juggernaut"
  | "rev_animated";

const ASPECT_RATIOS: { value: AspectRatio; label: string }[] = [
  { value: [16, 9], label: "16:9 Landscape" },
  { value: [3, 2], label: "3:2 Landscape" },
  { value: [1, 1], label: "1:1 Square" },
  { value: [2, 3], label: "2:3 Portrait" },
  { value: [9, 16], label: "9:16 Portrait" },
];

const RESOLUTION_OPTIONS: { value: ResolutionClass; label: string }[] = [
  { value: 128, label: "128p" },
  { value: 256, label: "256p" },
  { value: 480, label: "480p" },
  { value: 512, label: "512p" },
  { value: 720, label: "720p" },
  { value: 1024, label: "1024p" },
  { value: 2048, label: "2048p" },
  { value: 4096, label: "4096p" },
];

const FPS_OPTIONS: { value: VideoFPS; label: string }[] = [
  { value: 8, label: "8 FPS" },
  { value: 16, label: "16 FPS" },
  { value: 24, label: "24 FPS" },
  { value: 32, label: "32 FPS" },
];

const BASE_MODELS: { value: BaseGenerationModel; label: string }[] = [
  { value: "sd15", label: "Stable Diffusion 1.5" },
  { value: "epicrealism", label: "Epic Realism" },
  { value: "realistic_vision", label: "Realistic Vision" },
  { value: "dreamshaper", label: "DreamShaper" },
  { value: "juggernaut", label: "Juggernaut" },
  { value: "rev_animated", label: "ReV Animated" },
];

interface FullGenerationSectionProps {
  isOpen: boolean;
  onToggle: () => void;
  prefillData?: {
    prompt?: string;
    width?: number;
    height?: number;
    fps?: number;
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

export function FullGenerationSection({
  isOpen,
  onToggle,
  prefillData,
}: FullGenerationSectionProps) {
  const { t } = useI18n();
  const router = useRouter();
  const { accessToken } = useAuthStore();
  const { initializeJobs } = useJobMonitor();

  const [prompt, setPrompt] = useState("");
  const [length, setLength] = useState(5);
  const [negativePrompt, setNegativePrompt] = useState("");
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>([16, 9]);
  const [resolution, setResolution] = useState<ResolutionClass>(720);
  const [fps, setFps] = useState<VideoFPS>(24);
  const [baseModel, setBaseModel] = useState<BaseGenerationModel>("sd15");
  const [inferenceSteps, setInferenceSteps] = useState(25);
  const [guidanceScale, setGuidanceScale] = useState(7.5);
  const [seed, setSeed] = useState<number | "">(
    Math.floor(Math.random() * 1000000),
  );
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    if (prefillData?.prompt) {
      setPrompt(prefillData.prompt);
    }
    if (prefillData?.video_length) {
      setLength(prefillData.video_length);
    }
    if (prefillData?.fps && [8, 16, 24, 32].includes(prefillData.fps)) {
      setFps(prefillData.fps as VideoFPS);
    }

    if (prefillData?.width && prefillData?.height) {
      const width = prefillData.width;
      const height = prefillData.height;

      const ratio = width / height;
      if (Math.abs(ratio - 16 / 9) < 0.1) {
        setAspectRatio([16, 9]);
      } else if (Math.abs(ratio - 3 / 2) < 0.1) {
        setAspectRatio([3, 2]);
      } else if (Math.abs(ratio - 1) < 0.1) {
        setAspectRatio([1, 1]);
      } else if (Math.abs(ratio - 2 / 3) < 0.1) {
        setAspectRatio([2, 3]);
      } else if (Math.abs(ratio - 9 / 16) < 0.1) {
        setAspectRatio([9, 16]);
      }

      const maxDimension = height;
      const validResolutions: ResolutionClass[] = [
        128, 256, 480, 512, 720, 1024, 2048, 4096,
      ];
      const closestResolution = validResolutions.reduce((prev, curr) =>
        Math.abs(curr - maxDimension) < Math.abs(prev - maxDimension)
          ? curr
          : prev,
      );
      setResolution(closestResolution);
    }
  }, [prefillData]);

  const randomizeSeed = () => {
    setSeed(Math.floor(Math.random() * 2147483647));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: Record<string, string> = {};
    if (!prompt.trim()) {
      newErrors.prompt = t("create.full.promptRequired");
    }
    if (length < 1) {
      newErrors.length = t("create.full.lengthMin");
    }
    if (inferenceSteps < 1 || inferenceSteps > 100) {
      newErrors.inferenceSteps = t("create.full.inferenceStepsRange");
    }
    if (seed !== "" && (seed < 0 || seed > 2147483647)) {
      newErrors.seed = t("create.full.seedRange");
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
        negative_prompt: negativePrompt || "",
        aspect_ratio: [aspectRatio[0], aspectRatio[1]],
        resolution: resolution,
        video_length: length,
        fps: fps,
        output_format: "mp4",
        base_model: baseModel,
        motion_adapter: "default",
        inference_steps: inferenceSteps,
      };

      const response = await videoApi.generateVideo(payload, accessToken);

      toast.success("Video generation started successfully!");
      await initializeJobs(accessToken);
      router.push("/jobs");
    } catch (error) {
      //console.error("Failed to generate video:", error)
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
          <FaCog className="text-[#B949A3] text-xl" />
          <h2 className="text-xl font-semibold text-white">
            {t("create.full.title")}
          </h2>
        </div>
        <FaChevronDown
          className={`text-[#8a8aa8] transition-transform duration-300 ${isOpen ? "rotate-180" : ""}`}
        />
      </button>

      <div
        className={`transition-all duration-300 ease-in-out overflow-hidden ${
          isOpen ? "max-h-[3000px] opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <form
          onSubmit={handleSubmit}
          className="p-4 pt-2 border-t border-[#2a2a4e]"
        >
          <div className="space-y-2">
            {/* Prompt */}
            <div className="flex flex-col gap-0">
              <label className="flex items-center text-base font-medium text-white mb-2">
                {t("create.full.promptLabel")}{" "}
                <span className="text-red-400 ml-1">*</span>
                <InfoTooltip content={t("create.full.promptTooltip")} />
              </label>
              <textarea
                value={prompt}
                onChange={(e) => {
                  setPrompt(e.target.value);
                  if (errors.prompt) setErrors({ ...errors, prompt: "" });
                }}
                placeholder={t("create.full.promptPlaceholder")}
                rows={4}
                className={`w-full bg-[#0f0f1e] border rounded-lg px-4 py-3 text-white placeholder-[#5a5a78] focus:outline-none focus:border-[#31B7EA] resize-none ${
                  errors.prompt ? "border-red-500" : "border-[#2a2a4e]"
                }`}
              />
              {errors.prompt && (
                <p className="text-red-400 text-sm mt-1">{errors.prompt}</p>
              )}
            </div>

            {/* Video Length */}
            <div className="flex flex-col gap-0">
              <label className="flex items-center text-base font-medium text-white mb-2">
                {t("create.full.lengthLabel")}{" "}
                <span className="text-red-400 ml-1">*</span>
                <InfoTooltip content={t("create.full.lengthTooltip")} />
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

            {/* Negative Prompt */}
            <div className="flex flex-col gap-0">
              <label className="flex items-center text-base font-medium text-white mb-2">
                {t("create.full.negativePromptLabel")}
                <InfoTooltip content={t("create.full.negativePromptTooltip")} />
              </label>
              <textarea
                value={negativePrompt}
                onChange={(e) => setNegativePrompt(e.target.value)}
                placeholder={t("create.full.negativePromptPlaceholder")}
                rows={3}
                className="w-full bg-[#0f0f1e] border border-[#2a2a4e] rounded-lg px-4 py-3 text-white placeholder-[#5a5a78] focus:outline-none focus:border-[#31B7EA] resize-none"
              />
            </div>

            {/* Aspect Ratio */}
            <div>
              <label className="flex items-center text-base font-medium text-white mb-2">
                {t("create.full.aspectRatioLabel")}{" "}
                <span className="text-red-400 ml-1">*</span>
                <InfoTooltip content={t("create.full.aspectRatioTooltip")} />
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {ASPECT_RATIOS.map((ratio) => (
                  <button
                    key={ratio.label}
                    type="button"
                    onClick={() => setAspectRatio(ratio.value)}
                    className={`p-2 rounded-lg border transition-all ${
                      aspectRatio[0] === ratio.value[0] &&
                      aspectRatio[1] === ratio.value[1]
                        ? "bg-[#31B7EA] border-[#31B7EA] text-white"
                        : "bg-[#0f0f1e] border-[#2a2a4e] text-[#b0b0c8] hover:border-[#3a3a5e]"
                    }`}
                  >
                    {ratio.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Resolution */}
            <div>
              <label className="flex items-center text-base font-medium text-white mb-2">
                {t("create.full.resolutionLabel")}{" "}
                <span className="text-red-400 ml-1">*</span>
                <InfoTooltip content={t("create.full.resolutionTooltip")} />
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {RESOLUTION_OPTIONS.map((res) => (
                  <button
                    key={res.value}
                    type="button"
                    onClick={() => setResolution(res.value)}
                    className={`p-2 rounded-lg border transition-all ${
                      resolution === res.value
                        ? "bg-[#31B7EA] border-[#31B7EA] text-white"
                        : "bg-[#0f0f1e] border-[#2a2a4e] text-[#b0b0c8] hover:border-[#3a3a5e]"
                    }`}
                  >
                    {res.label}
                  </button>
                ))}
              </div>
            </div>

            {/* FPS */}
            <div>
              <label className="flex items-center text-base font-medium text-white mb-2">
                {t("create.full.fpsLabel")}{" "}
                <span className="text-red-400 ml-1">*</span>
                <InfoTooltip content={t("create.full.fpsTooltip")} />
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {FPS_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setFps(option.value)}
                    className={`p-2 rounded-lg border transition-all ${
                      fps === option.value
                        ? "bg-[#31B7EA] border-[#31B7EA] text-white"
                        : "bg-[#0f0f1e] border-[#2a2a4e] text-[#b0b0c8] hover:border-[#3a3a5e]"
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Base Model */}
            <div>
              <label className="flex items-center text-base font-medium text-white mb-2">
                {t("create.full.baseModelLabel")}{" "}
                <span className="text-red-400 ml-1">*</span>
                <InfoTooltip content={t("create.full.baseModelTooltip")} />
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {BASE_MODELS.map((model) => (
                  <button
                    key={model.value}
                    type="button"
                    onClick={() => setBaseModel(model.value)}
                    className={`p-2 rounded-lg border transition-all ${
                      baseModel === model.value
                        ? "bg-[#31B7EA] border-[#31B7EA] text-white"
                        : "bg-[#0f0f1e] border-[#2a2a4e] text-[#b0b0c8] hover:border-[#3a3a5e]"
                    }`}
                  >
                    {model.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Inference Steps with custom styled range */}
            <div>
              <label className="flex items-center text-base font-medium text-white mb-2">
                {t("create.full.inferenceStepsLabel")}{" "}
                <span className="text-red-400 ml-1">*</span>
                <InfoTooltip content={t("create.full.inferenceStepsTooltip")} />
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  value={inferenceSteps}
                  onChange={(e) => {
                    setInferenceSteps(Number(e.target.value));
                    if (errors.inferenceSteps)
                      setErrors({ ...errors, inferenceSteps: "" });
                  }}
                  min={1}
                  max={100}
                  className="flex-1 h-2 bg-[#0f0f1e] rounded-lg appearance-none cursor-pointer
                                        [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                                        [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-[#31B7EA]
                                        [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:hover:bg-[#2a9fd0]
                                        [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:rounded-full
                                        [&::-moz-range-thumb]:bg-[#31B7EA] [&::-moz-range-thumb]:border-0
                                        [&::-moz-range-thumb]:cursor-pointer [&::-moz-range-thumb]:hover:bg-[#2a9fd0]"
                />
                <span className="text-white font-medium min-w-[3ch] text-right">
                  {inferenceSteps}
                </span>
              </div>
              {errors.inferenceSteps && (
                <p className="text-red-400 text-sm mt-1">
                  {errors.inferenceSteps}
                </p>
              )}
            </div>

            {/* Guidance Scale with custom styled range */}
            <div>
              <label className="flex items-center text-base font-medium text-white mb-2">
                {t("create.full.guidanceScaleLabel")}{" "}
                <span className="text-red-400 ml-1">*</span>
                <InfoTooltip content={t("create.full.guidanceScaleTooltip")} />
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  value={guidanceScale}
                  onChange={(e) => {
                    const value = Number(e.target.value);
                    setGuidanceScale(value);
                    if (errors.guidanceScale) {
                      setErrors({ ...errors, guidanceScale: "" });
                    }
                  }}
                  min={0}
                  max={10}
                  step={0.1}
                  className="flex-1 h-2 bg-[#0f0f1e] rounded-lg appearance-none cursor-pointer
                                        [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                                        [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-[#31B7EA]
                                        [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:hover:bg-[#2a9fd0]
                                        [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:rounded-full
                                        [&::-moz-range-thumb]:bg-[#31B7EA] [&::-moz-range-thumb]:border-0
                                        [&::-moz-range-thumb]:cursor-pointer [&::-moz-range-thumb]:hover:bg-[#2a9fd0]"
                />
                <span className="text-white font-medium min-w-[4ch] text-right">
                  {guidanceScale.toFixed(1)}
                </span>
              </div>
              {errors.guidanceScale && (
                <p className="text-red-400 text-sm mt-1">
                  {t("create.full.guidanceScaleRange")}
                </p>
              )}
            </div>

            {/* Seed */}
            {/*    <div>*/}
            {/*        <label className="flex items-center text-base font-medium text-white mb-2">*/}
            {/*            {t("create.full.seedLabel")}*/}
            {/*            <InfoTooltip content={t("create.full.seedTooltip")}/>*/}
            {/*        </label>*/}
            {/*        <div className="flex items-center gap-2">*/}
            {/*            <input*/}
            {/*                type="number"*/}
            {/*                value={seed}*/}
            {/*                onChange={(e) => {*/}
            {/*                    setSeed(e.target.value === "" ? "" : Number(e.target.value))*/}
            {/*                    if (errors.seed) setErrors({...errors, seed: ""})*/}
            {/*                }}*/}
            {/*                placeholder={t("create.full.seedPlaceholder")}*/}
            {/*                min={0}*/}
            {/*                max={2147483647}*/}
            {/*                className={`flex-1 bg-[#0f0f1e] border rounded-lg px-4 py-2 text-white placeholder-[#5a5a78] focus:outline-none focus:border-[#31B7EA]*/}
            {/*[&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none [-moz-appearance:textfield] ${*/}
            {/*                    errors.seed ? "border-red-500" : "border-[#2a2a4e]"*/}
            {/*                }`}*/}
            {/*            />*/}
            {/*            <Button*/}
            {/*                type="button"*/}
            {/*                onClick={randomizeSeed}*/}
            {/*                variant="outline"*/}
            {/*                size="md"*/}
            {/*                className="shrink-0 bg-transparent"*/}
            {/*            >*/}
            {/*                {t("create.full.randomizeButton")}*/}
            {/*            </Button>*/}
            {/*        </div>*/}
            {/*        {errors.seed && <p className="text-red-400 text-sm mt-1">{errors.seed}</p>}*/}
            {/*    </div>*/}

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={isGenerating}
              variant="blue"
              size="md"
              className="w-full"
            >
              {isGenerating
                ? t("create.full.generating")
                : t("create.full.generateButton")}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
