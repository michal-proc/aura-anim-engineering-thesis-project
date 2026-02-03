"use client";

import { FaLightbulb, FaChevronDown } from "react-icons/fa";
import { useI18n } from "@/lib/i18n-context";

interface InstructionsSectionProps {
  isOpen: boolean;
  onToggle: () => void;
}

export function InstructionsSection({
  isOpen,
  onToggle,
}: InstructionsSectionProps) {
  const { t } = useI18n();

  return (
    <div className="bg-[#1a1a2e] rounded-xl border border-[#2a2a4e] overflow-hidden">
      <button
        type="button"
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-[#1f1f3a] transition-colors cursor-pointer"
      >
        <div className="flex items-center gap-3">
          <FaLightbulb className="text-yellow-400 text-xl" />
          <h2 className="text-xl font-semibold text-white">
            {t("create.instructions.title")}
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
        <div className="p-4 pt-2 border-t border-[#2a2a4e]">
          <div className="space-y-4 text-[#b0b0c8] text-sm leading-relaxed">
            {/* Intro paragraph */}
            <p className="text-[#c5c5d8]">{t("create.instructions.intro")}</p>

            {/* How to write effective prompts */}
            <div className="space-y-2">
              <h3 className="text-white font-semibold text-base">
                {t("create.instructions.promptsTitle")}
              </h3>
              <p className="text-[#c5c5d8]">
                {t("create.instructions.promptsIntro")}
              </p>
              <ul className="list-disc list-inside space-y-1 ml-1 text-[#b0b0c8]">
                <li>{t("create.instructions.promptsTip1")}</li>
                <li>{t("create.instructions.promptsTip2")}</li>
                <li>{t("create.instructions.promptsTip3")}</li>
                <li>{t("create.instructions.promptsTip4")}</li>
              </ul>
              <p className="text-[#c5c5d8]">
                {t("create.instructions.negativePromptInfo")}
              </p>
            </div>

            {/* Technical parameters */}
            <div className="space-y-2">
              <h3 className="text-white font-semibold text-base">
                {t("create.instructions.parametersTitle")}
              </h3>
              <p className="text-[#c5c5d8]">
                {t("create.instructions.parametersIntro")}
              </p>

              <div className="space-y-2 pl-2">
                {/* Video Length */}
                <div>
                  <h4 className="text-white font-medium text-sm mb-0.5">
                    {t("create.instructions.videoLengthTitle")}
                  </h4>
                  <p className="text-[#b0b0c8]">
                    {t("create.instructions.videoLengthDesc")}
                  </p>
                </div>

                {/* Aspect Ratio */}
                <div>
                  <h4 className="text-white font-medium text-sm mb-0.5">
                    {t("create.instructions.aspectRatioTitle")}
                  </h4>
                  <p className="text-[#b0b0c8] mb-1">
                    {t("create.instructions.aspectRatioIntro")}
                  </p>
                  <ul className="list-disc list-inside ml-1 space-y-0.5 text-[#b0b0c8]">
                    <li>{t("create.instructions.aspectRatioHorizontal")}</li>
                    <li>{t("create.instructions.aspectRatioSquare")}</li>
                    <li>{t("create.instructions.aspectRatioVertical")}</li>
                  </ul>
                </div>

                {/* Resolution */}
                <div>
                  <h4 className="text-white font-medium text-sm mb-0.5">
                    {t("create.instructions.resolutionTitle")}
                  </h4>
                  <p className="text-[#b0b0c8] mb-1">
                    {t("create.instructions.resolutionIntro")}
                  </p>
                  <ul className="list-disc list-inside ml-1 space-y-0.5 text-[#b0b0c8]">
                    <li>{t("create.instructions.resolutionLow")}</li>
                    <li>{t("create.instructions.resolutionMedium")}</li>
                    <li>{t("create.instructions.resolutionHigh")}</li>
                    <li>{t("create.instructions.resolution4K")}</li>
                  </ul>
                </div>

                {/* FPS */}
                <div>
                  <h4 className="text-white font-medium text-sm mb-0.5">
                    {t("create.instructions.fpsTitle")}
                  </h4>
                  <p className="text-[#b0b0c8] mb-1">
                    {t("create.instructions.fpsIntro")}
                  </p>
                  <ul className="list-disc list-inside ml-1 space-y-0.5 text-[#b0b0c8]">
                    <li>{t("create.instructions.fpsLow")}</li>
                    <li>{t("create.instructions.fpsCinematic")}</li>
                    <li>{t("create.instructions.fpsHigh")}</li>
                  </ul>
                </div>

                {/* Inference Steps */}
                <div>
                  <h4 className="text-white font-medium text-sm mb-0.5">
                    {t("create.instructions.guidanceScaleTitle")}
                  </h4>
                  <p className="text-[#b0b0c8] mb-1">
                    {t("create.instructions.guidanceScaleIntro")}
                  </p>
                  <ul className="list-disc list-inside ml-1 space-y-0.5 text-[#b0b0c8]">
                    <li>{t("create.instructions.guidanceScaleLow")}</li>
                    <li>{t("create.instructions.guidanceScaleMedium")}</li>
                    <li>{t("create.instructions.guidanceScaleHigh")}</li>
                  </ul>
                </div>

                {/* Guidance Scale */}
                <div>
                  <h4 className="text-white font-medium text-sm mb-0.5">
                    {t("create.instructions.guidanceScaleTitle")}
                  </h4>
                  <p className="text-[#b0b0c8] mb-1">
                    {t("create.instructions.guidanceScaleIntro")}
                  </p>
                  <ul className="list-disc list-inside ml-1 space-y-0.5 text-[#b0b0c8]">
                    <li>{t("create.instructions.guidanceScaleLow")}</li>
                    <li>{t("create.instructions.guidanceScaleMedium")}</li>
                    <li>{t("create.instructions.guidanceScaleHigh")}</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Base Generation Models */}
            <div className="space-y-2">
              <h3 className="text-white font-semibold text-base">
                {t("create.instructions.modelsTitle")}
              </h3>
              <p className="text-[#c5c5d8]">
                {t("create.instructions.modelsIntro")}
              </p>

              <div className="space-y-2 pl-2">
                <div>
                  <h4 className="text-white font-medium text-sm mb-0.5">
                    {t("create.instructions.modelSD15Title")}
                  </h4>
                  <p className="text-[#b0b0c8]">
                    {t("create.instructions.modelSD15Desc")}
                  </p>
                </div>

                <div>
                  <h4 className="text-white font-medium text-sm mb-0.5">
                    {t("create.instructions.modelEpicRealismTitle")}
                  </h4>
                  <p className="text-[#b0b0c8]">
                    {t("create.instructions.modelEpicRealismDesc")}
                  </p>
                </div>

                <div>
                  <h4 className="text-white font-medium text-sm mb-0.5">
                    {t("create.instructions.modelRealisticVisionTitle")}
                  </h4>
                  <p className="text-[#b0b0c8]">
                    {t("create.instructions.modelRealisticVisionDesc")}
                  </p>
                </div>

                <div>
                  <h4 className="text-white font-medium text-sm mb-0.5">
                    {t("create.instructions.modelDreamShaperTitle")}
                  </h4>
                  <p className="text-[#b0b0c8]">
                    {t("create.instructions.modelDreamShaperDesc")}
                  </p>
                </div>

                <div>
                  <h4 className="text-white font-medium text-sm mb-0.5">
                    {t("create.instructions.modelJuggernautTitle")}
                  </h4>
                  <p className="text-[#b0b0c8]">
                    {t("create.instructions.modelJuggernautDesc")}
                  </p>
                </div>

                <div>
                  <h4 className="text-white font-medium text-sm mb-0.5">
                    {t("create.instructions.modelRevAnimatedTitle")}
                  </h4>
                  <p className="text-[#b0b0c8]">
                    {t("create.instructions.modelRevAnimatedDesc")}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
