import { apiRequest } from "./client";
import type {
  Video,
  VideoExplore,
  Job,
  JobsMeta,
  GenerateVideoPayload,
  GetVideosResponse,
  GetVideoResponse,
  GetVideoExploreResponse,
  GetJobsResponse,
} from "@/types/video.types";
import {
  USE_MOCK_DATA,
  mockVideos,
  mockExploreVideos,
  mockJobs,
  mockJobsMeta,
  getMockVideoBlob,
} from "@/lib/mock-data";

export const videoApi = {
  getVideos: async (token?: string): Promise<GetVideosResponse> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 600));
      return {
        success: true,
        data: mockVideos,
      };
    }
    const response = await apiRequest<{ data: Video[] }>("/videos", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return {
      success: true,
      data: response.data,
    };
  },

  getVideo: async (id: string, token?: string): Promise<GetVideoResponse> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 300));
      const video = mockVideos.find((v) => v.id === id);
      if (!video) {
        throw new Error("Video not found");
      }
      return {
        success: true,
        data: video,
      };
    }
    const video = await apiRequest<GetVideoResponse>(`/videos/${id}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return video;
  },

  getVideoFile: async (id: string, token: string): Promise<Blob> => {
    if (USE_MOCK_DATA) {
      return getMockVideoBlob(id);
    }
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_APP_BACKEND_URL || "http://localhost:8000"}/videos/${id}/file`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "ngrok-skip-browser-warning": "true",
        },
      },
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch video file: ${response.statusText}`);
    }

    return await response.blob();
  },

  getExploreVideos: async (): Promise<GetVideoExploreResponse> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      return {
        success: true,
        data: mockExploreVideos,
      };
    }
    const response = await apiRequest<{ data: VideoExplore[] }>(
      "/videos/explore",
      {
        method: "GET",
      },
    );

    console.log(response);
    return {
      success: true,
      data: response.data,
    };
  },

  getJobs: async (token?: string): Promise<GetJobsResponse> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 400));
      return {
        success: true,
        data: mockJobs,
        meta: mockJobsMeta,
      };
    }
    const response = await apiRequest<{ data: Job[]; metadata: JobsMeta }>(
      "/videos/jobs",
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );
    return {
      success: true,
      data: response.data,
      meta: response.metadata,
    };
  },

  cancelJob: async (jobId: string, token: string): Promise<void> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      const job = mockJobs.find((j) => j.job_id === jobId);
      if (!job) {
        throw new Error("Job not found");
      }
      if (job.status !== "pending" && job.status !== "processing") {
        throw new Error("Job cannot be cancelled in current status");
      }
      job.status = "cancelled";
      return;
    }
    return apiRequest<void>(`/videos/jobs/${jobId}/cancel`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  updateVideo: async (
    id: string,
    data: { name?: string; shared?: boolean },
    token: string,
  ): Promise<Video> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      const video = mockVideos.find((v) => v.id === id);
      if (!video) {
        throw new Error("Video not found");
      }
      if (data.name !== undefined) video.name = data.name;
      if (data.shared !== undefined) video.shared = data.shared;
      return video;
    }
    return apiRequest<Video>(`/videos/${id}`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
  },

  deleteVideo: async (id: string, token: string): Promise<void> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      const index = mockVideos.findIndex((v) => v.id === id);
      if (index === -1) {
        throw new Error("Video not found");
      }
      mockVideos.splice(index, 1);
      return;
    }
    return apiRequest<void>(`/videos/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  markVideoShared: async (id: string, token: string): Promise<void> => {
    await videoApi.updateVideo(id, { shared: true }, token);
  },

  getSharedVideo: async (id: string): Promise<GetVideoResponse> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 400));
      const video = mockVideos.find((v) => v.id === id);
      if (!video) {
        throw new Error("Video not found");
      }
      return {
        success: true,
        data: video,
      };
    }
    return apiRequest<GetVideoResponse>(`/videos/shared/${id}`, {
      method: "GET",
    });
  },

  generateVideo: async (
    payload: GenerateVideoPayload,
    token: string,
  ): Promise<{ job_id: string }> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const newJobId = `job-${Date.now()}`;
      return { job_id: newJobId };
    }
    return apiRequest<{ job_id: string }>("/videos/generate", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
  },
};
