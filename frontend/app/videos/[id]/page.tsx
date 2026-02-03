"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Sidebar } from "@/components/common/sidebar";
import { Header } from "@/components/common/header";
import { videoApi } from "@/api/video";
import { useI18n } from "@/lib/i18n-context";
import { PulseLoader } from "react-spinners";
import {
  FaEdit,
  FaSave,
  FaTimes,
  FaDownload,
  FaTrash,
  FaInstagram,
  FaMagic,
  FaShareAlt,
} from "react-icons/fa";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { useAuthStore } from "@/store/auth-store";

export default function VideoProfilePage() {
  const params = useParams();
  const router = useRouter();
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const videoId = params.id as string;
  const { accessToken, isInitialized } = useAuthStore();

  const [isEditing, setIsEditing] = useState(false);
  const [newName, setNewName] = useState("");
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showInstagramShare, setShowInstagramShare] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ["video", videoId, accessToken],
    queryFn: async () => {
      if (!accessToken) {
        throw new Error("No access token available");
      }
      try {
        return await videoApi.getVideo(videoId, accessToken);
      } catch (err) {
        throw err;
      }
    },
    enabled: isInitialized && !!accessToken && !!videoId,
  });

  const video = data?.data;

  useEffect(() => {
    if (video && accessToken) {
      setNewName(video.name);

      videoApi.getVideoFile(videoId, accessToken).then((blob) => {
        const url = URL.createObjectURL(blob);
        setVideoUrl(url);
      });
    }

    return () => {
      if (videoUrl) {
        URL.revokeObjectURL(videoUrl);
      }
    };
  }, [video, videoId, accessToken]);

  const updateVideoMutation = useMutation({
    mutationFn: async (name: string) => {
      if (!accessToken) throw new Error("No access token");
      return await videoApi.updateVideo(videoId, { name }, accessToken);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["video", videoId] });
      queryClient.invalidateQueries({ queryKey: ["videos"] });
      setIsEditing(false);
    },
  });

  const deleteVideoMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error("No access token");
      await videoApi.deleteVideo(videoId, accessToken);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["videos"] });
      router.push("/videos");
    },
  });

  const markSharedMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error("No access token");
      return await videoApi.markVideoShared(videoId, accessToken);
    },
  });

  const handleShare = async (
    platform?: "facebook" | "x" | "whatsapp" | "linkedin",
  ) => {
    const shareUrl = `${window.location.origin}/shared/${videoId}`;
    const shareTitle = video?.name || "Check out this video";
    const shareText =
      video?.job.parameters.prompt || "Amazing video generated with AI";

    await markSharedMutation.mutateAsync();

    if (platform) {
      const encodedUrl = encodeURIComponent(shareUrl);
      const encodedText = encodeURIComponent(shareText);

      const urls = {
        facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}&quote=${encodedText}`,
        x: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedText}`,
        linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${shareUrl}`,
        whatsapp: `https://wa.me/?text=${encodedText}%20${encodedUrl}`,
      };

      window.open(urls[platform], "_blank", "noopener,noreferrer");
    } else {
      if (!navigator.share) {
        alert("Sharing is not supported in this browser.");
        return;
      }

      try {
        await navigator.share({
          title: shareTitle,
          text: shareText,
          url: shareUrl,
        });
      } catch (err: any) {
        //
      }
    }
  };

  const handleSave = () => {
    if (newName.trim()) {
      updateVideoMutation.mutate(newName.trim());
    }
  };

  const handleDelete = () => {
    deleteVideoMutation.mutate();
  };

  const handleDownloadForSocial = async (platform: string) => {
    if (!video || !accessToken) return;
    try {
      const blob = await videoApi.getVideoFile(videoId, accessToken);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${video.name}_${platform}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      //console.error("Download failed:", error)
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="flex h-screen">
          <Sidebar />
          <div className="flex-1 flex flex-col overflow-hidden">
            <Header />
            <main className="flex-1 overflow-y-auto flex items-center justify-center">
              <PulseLoader color="#31B7EA" size={15} />
            </main>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  if (error || !video) {
    return (
      <ProtectedRoute>
        <div className="flex h-screen">
          <Sidebar />
          <div className="flex-1 flex flex-col overflow-hidden">
            <Header />
            <main className="flex-1 overflow-y-auto p-8">
              <div className="max-w-5xl mx-auto">
                <div className="bg-[#1a1a2e] rounded-xl p-8 border border-[#2a2a4e] text-center">
                  <p className="text-red-400 mb-4">
                    {t("video.notFound") || "Video not found"}
                  </p>
                  <Button
                    onClick={() => router.push("/videos")}
                    variant="outline"
                  >
                    {t("video.backToVideos")}
                  </Button>
                </div>
              </div>
            </main>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto p-8">
            <div className="max-w-5xl mx-auto space-y-6">
              <div className="flex items-center justify-between">
                <Button
                  variant="ghost"
                  onClick={() => router.push("/videos")}
                  className="text-[#8a8aa8] hover:text-white"
                >
                  ← {t("video.backToVideos")}
                </Button>
                <div className="flex items-center gap-3">
                  <Button
                    onClick={() => setShowInstagramShare(true)}
                    variant="outline"
                    className="border-[#2a2a4e] hover:bg-[#2a2a4e] bg-transparent flex items-center gap-2"
                  >
                    <FaDownload className="w-4 h-4" />
                    {t("video.download")}
                  </Button>
                  <Button
                    onClick={() => setShowDeleteConfirm(true)}
                    variant="outline"
                    className="border-red-500/20 text-red-400 hover:bg-red-500/10 flex items-center gap-2"
                  >
                    <FaTrash className="w-4 h-4" />
                    {t("video.delete")}
                  </Button>
                </div>
              </div>

              <div className="bg-[#1a1a2e] rounded-xl overflow-hidden border border-[#2a2a4e]">
                <div className="aspect-video bg-[#0a0a0f] relative">
                  {videoUrl ? (
                    <video src={videoUrl} controls className="w-full h-full" />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <PulseLoader color="#31B7EA" size={15} />
                    </div>
                  )}
                </div>
              </div>

              <div className="bg-[#1a1a2e] rounded-xl p-6 border border-[#2a2a4e]">
                {!isEditing ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h1 className="text-2xl font-bold text-white">
                        {video.name}
                      </h1>
                      <Button
                        onClick={() => setIsEditing(true)}
                        variant="outline"
                        size="sm"
                        className="border-[#2a2a4e] flex items-center gap-2"
                      >
                        <FaEdit className="w-4 h-4" />
                        {t("video.edit")}
                      </Button>
                    </div>
                    <div className="flex items-center gap-6 text-sm">
                      <div>
                        <span className="text-[#6a6a88]">
                          {t("video.created")}:{" "}
                        </span>
                        <span className="text-white">
                          {new Date(video.created_at).toLocaleString()}
                        </span>
                      </div>
                      <div>
                        <span className="text-[#6a6a88]">
                          {t("video.videoId")}:{" "}
                        </span>
                        <span className="text-white font-mono">{video.id}</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-3">
                    <Input
                      value={newName}
                      onChange={(e) => setNewName(e.target.value)}
                      className="flex-1 bg-[#0a0a0f] border-[#2a2a4e]"
                      placeholder={t("video.videoName")}
                    />
                    <Button
                      onClick={handleSave}
                      disabled={updateVideoMutation.isPending}
                      size="sm"
                      className="bg-green-500 hover:bg-green-600 flex items-center gap-2"
                    >
                      <FaSave className="w-4 h-4" />
                      {t("video.save")}
                    </Button>
                    <Button
                      onClick={() => {
                        setIsEditing(false);
                        setNewName(video.name);
                      }}
                      variant="outline"
                      size="sm"
                      className="border-[#2a2a4e] flex items-center gap-2"
                    >
                      <FaTimes className="w-4 h-4" />
                      {t("profile.cancel")}
                    </Button>
                  </div>
                )}
              </div>

              <div className="bg-[#1a1a2e] rounded-xl p-6 border border-[#2a2a4e]">
                <h3 className="text-lg font-semibold text-white mb-4">
                  {t("video.shareVideo")}
                </h3>
                <div className="flex flex-col gap-3">
                  <Button
                    onClick={() => handleShare("facebook")}
                    className="w-full bg-[#1877F2] hover:bg-[#1565D8] flex items-center justify-center gap-2"
                  >
                    <FaShareAlt className="w-5 h-5" />
                    {t("video.shareOnFacebook")}
                  </Button>

                  <Button
                    onClick={() => handleShare("x")}
                    className="w-full bg-black hover:bg-gray-900 flex items-center justify-center gap-2"
                  >
                    <FaShareAlt className="w-5 h-5" />
                    {t("video.shareOnX")}
                  </Button>

                  <Button
                    onClick={() => handleShare("whatsapp")}
                    className="w-full bg-[#25D366] hover:bg-[#20BA5A] flex items-center justify-center gap-2"
                  >
                    <FaShareAlt className="w-5 h-5" />
                    Share on WhatsApp
                  </Button>

                  <Button
                    onClick={() => handleShare("linkedin")}
                    className="w-full bg-[#0077B5] hover:bg-[#006399] flex items-center justify-center gap-2"
                  >
                    <FaShareAlt className="w-5 h-5" />
                    Share on LinkedIn
                  </Button>

                  <Button
                    onClick={() => setShowInstagramShare(true)}
                    className="w-full bg-gradient-to-r from-[#833AB4] via-[#FD1D1D] to-[#F77737] hover:opacity-90 flex items-center justify-center gap-2"
                  >
                    <FaInstagram className="w-5 h-5" />
                    {t("video.shareOnInstagram")}
                  </Button>

                  {navigator.share && (
                    <Button
                      onClick={() => handleShare()}
                      variant="outline"
                      className="w-full border-[#2a2a4e] flex items-center justify-center gap-2"
                    >
                      <FaShareAlt className="w-5 h-5" />
                      Share via...
                    </Button>
                  )}
                </div>
              </div>

              <div className="bg-[#1a1a2e] rounded-xl p-6 border border-[#2a2a4e]">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">
                    {t("video.generationParameters")}
                  </h3>
                  <Button
                    onClick={() =>
                      router.push(
                        `/videos/create?prompt=${encodeURIComponent(video.job?.parameters.prompt ?? "")}&width=${video.job?.parameters.width ?? ""}&height=${video.job?.parameters.height ?? ""}&fps=${video.job?.parameters.fps ?? ""}&video_length=${video.job?.parameters.video_length ?? ""}`,
                      )
                    }
                    variant="outline"
                    size="sm"
                    className="border-[#31B7EA] text-[#31B7EA] hover:bg-[#31B7EA]/10 bg-transparent flex items-center gap-2"
                  >
                    <FaMagic className="w-4 h-4" />
                    {t("video.createFromThis")}
                  </Button>
                </div>
                <div className="space-y-4">
                  <div>
                    <p className="text-xs text-[#6a6a88] mb-1">
                      {t("video.prompt")}
                    </p>
                    <p className="text-white text-sm">
                      {video.job?.parameters.prompt ?? ""}
                    </p>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-xs text-[#6a6a88] mb-1">
                        {t("video.resolution")}
                      </p>
                      <p className="text-white text-sm">
                        {video.job?.parameters.width ?? ""}x
                        {video.job?.parameters.height ?? ""}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-[#6a6a88] mb-1">
                        {t("video.fps")}
                      </p>
                      <p className="text-white text-sm">
                        {video.job?.parameters.fps ?? ""}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-[#6a6a88] mb-1">
                        {t("video.length")}
                      </p>
                      <p className="text-white text-sm">
                        {video.job?.parameters.video_length ?? ""}s
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>

        <Dialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
          <DialogContent className="bg-[#1a1a2e] border-[#2a2a4e]">
            <DialogHeader>
              <DialogTitle className="text-white">
                {t("video.deleteConfirm")}
              </DialogTitle>
              <DialogDescription className="text-[#8a8aa8]">
                {t("video.deleteDescription")}
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setShowDeleteConfirm(false)}
                className="border-[#2a2a4e]"
              >
                {t("profile.cancel")}
              </Button>
              <Button
                onClick={handleDelete}
                disabled={deleteVideoMutation.isPending}
                className="bg-red-500 hover:bg-red-600"
              >
                {deleteVideoMutation.isPending
                  ? t("video.deleting")
                  : t("video.delete")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Dialog open={showInstagramShare} onOpenChange={setShowInstagramShare}>
          <DialogContent className="bg-[#1a1a2e] border-[#2a2a4e]">
            <DialogHeader>
              <DialogTitle className="text-white flex items-center gap-2">
                <FaInstagram className="text-[#E4405F]" />
                {t("video.shareOnInstagram")}
              </DialogTitle>
              <DialogDescription className="text-[#8a8aa8]">
                {t("video.instagramShareDescription")}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <p className="text-sm text-[#8a8aa8]">
                {t("video.instagramShareInstructions")}
              </p>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setShowInstagramShare(false)}
                className="border-[#2a2a4e]"
              >
                {t("profile.cancel")}
              </Button>
              <Button
                onClick={() => {
                  handleDownloadForSocial("instagram");
                  setShowInstagramShare(false);
                }}
                className="bg-gradient-to-r from-[#833AB4] via-[#FD1D1D] to-[#F77737]"
              >
                {t("video.downloadForInstagram")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </ProtectedRoute>
  );
}
