"use client";
import { useEffect, useState } from "react";
import { Sidebar } from "@/components/common/sidebar";
import { Header } from "@/components/common/header";
import { useI18n } from "@/lib/i18n-context";
import { InstructionsSection } from "@/components/video-create/instructions-section";
import { QuickGenerationSection } from "@/components/video-create/quick-generation-section";
import { FullGenerationSection } from "@/components/video-create/full-generation-section";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { useSearchParams } from "next/navigation";

interface PrefillData {
  prompt?: string;
  width?: number;
  height?: number;
  fps?: number;
  video_length?: number;
}

export default function CreateVideoPage() {
  const { t } = useI18n();
  const searchParams = useSearchParams();
  const [openSection, setOpenSection] = useState<
    "instructions" | "quick" | "full" | null
  >("instructions");
  const [prefillData, setPrefillData] = useState<PrefillData>({});

  useEffect(() => {
    const prompt = searchParams.get("prompt");
    const width = searchParams.get("width");
    const height = searchParams.get("height");
    const fps = searchParams.get("fps");
    const videoLength = searchParams.get("video_length");

    const data: PrefillData = {};
    if (prompt) data.prompt = decodeURIComponent(prompt);
    if (width) data.width = Number(width);
    if (height) data.height = Number(height);
    if (fps) data.fps = Number(fps);
    if (videoLength) data.video_length = Number(videoLength);

    if (Object.keys(data).length > 0) {
      setPrefillData(data);
      setOpenSection("full");
    }
  }, [searchParams]);

  return (
    <ProtectedRoute>
      <div className="flex h-screen text-white">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-auto p-8">
            <div className="max-w-7xl mx-auto">
              <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-[#31B7EA] via-[#375DDA] to-[#B949A3] bg-clip-text text-transparent">
                {t("page.createVideo.title")}
              </h1>
              <p className="text-[#8a8aa8] mb-8">
                {t("page.createVideo.description")}
              </p>

              <div className="space-y-4">
                <InstructionsSection
                  isOpen={openSection === "instructions"}
                  onToggle={() =>
                    setOpenSection(
                      openSection === "instructions" ? null : "instructions",
                    )
                  }
                />

                <QuickGenerationSection
                  isOpen={openSection === "quick"}
                  onToggle={() =>
                    setOpenSection(openSection === "quick" ? null : "quick")
                  }
                  prefillData={prefillData}
                />

                <FullGenerationSection
                  isOpen={openSection === "full"}
                  onToggle={() =>
                    setOpenSection(openSection === "full" ? null : "full")
                  }
                  prefillData={prefillData}
                />
              </div>
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
