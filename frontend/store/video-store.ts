"use client";

import { create } from "zustand";
import type { Video } from "@/types/video.types";

interface VideoState {
  videos: Video[] | null;
  singleVideo: Video | null;
  setVideos: (videos: Video[]) => void;
  setSingleVideo: (video: Video) => void;
  clearVideos: () => void;
  clearSingleVideo: () => void;
  addVideo: (video: Video) => void;
  updateVideo: (id: string, video: Video) => void;
  removeVideo: (id: string) => void;
}

export const useVideoStore = create<VideoState>((set) => ({
  videos: null,
  singleVideo: null,

  setVideos: (videos) => set({ videos }),

  setSingleVideo: (video) => set({ singleVideo: video }),

  clearVideos: () => set({ videos: null }),

  clearSingleVideo: () => set({ singleVideo: null }),

  addVideo: (video) =>
    set((state) => ({
      videos: state.videos ? [video, ...state.videos] : [video],
    })),

  updateVideo: (id, video) =>
    set((state) => ({
      videos: state.videos
        ? state.videos.map((v) => (v.id === id ? video : v))
        : null,
      singleVideo: state.singleVideo?.id === id ? video : state.singleVideo,
    })),

  removeVideo: (id) =>
    set((state) => ({
      videos: state.videos ? state.videos.filter((v) => v.id !== id) : null,
      singleVideo: state.singleVideo?.id === id ? null : state.singleVideo,
    })),
}));
