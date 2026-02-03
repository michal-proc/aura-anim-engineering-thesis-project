"use client";

import { create } from "zustand";
import type { Job } from "@/types/video.types";
import { videoApi } from "@/api/video";
import { USE_MOCK_DATA } from "@/lib/mock-data";

interface JobUpdate {
  job_id: string;
  name?: string;
  status: string;
  progress_percentage: number;
  current_step?: string;
  final: boolean;
  timestamp: string;
}

interface JobMonitorStore {
  activeJobs: Job[];
  websockets: Map<string, WebSocket | NodeJS.Timeout>;
  addJob: (job: Job) => void;
  removeJob: (jobId: string) => void;
  updateJob: (jobId: string, update: Partial<Job>) => void;
  initializeJobs: (token?: string) => Promise<void>;
  connectWebSocket: (jobId: string) => void;
  disconnectWebSocket: (jobId: string) => void;
}

export const useJobMonitor = create<JobMonitorStore>((set, get) => ({
  activeJobs: [],
  websockets: new Map(),

  addJob: (job) => {
    const { activeJobs, connectWebSocket } = get();

    // Check if job already exists
    if (activeJobs.find((j) => j.job_id === job.job_id)) {
      return;
    }

    set({ activeJobs: [...activeJobs, job] });

    // Connect WebSocket for active jobs
    if (job.status === "pending" || job.status === "processing") {
      connectWebSocket(job.job_id);
    }
  },

  removeJob: (jobId) => {
    const { activeJobs, disconnectWebSocket } = get();
    disconnectWebSocket(jobId);
    set({ activeJobs: activeJobs.filter((j) => j.job_id !== jobId) });
  },

  updateJob: (jobId, update) => {
    const { activeJobs, disconnectWebSocket } = get();
    set({
      activeJobs: activeJobs.map((job) =>
        job.job_id === jobId ? { ...job, ...update } : job,
      ),
    });

    // Remove job if it reached final state
    if (
      update.status &&
      ["completed", "failed", "cancelled"].includes(update.status)
    ) {
      disconnectWebSocket(jobId);
      // Auto-remove after 5 seconds
      setTimeout(() => {
        get().removeJob(jobId);
      }, 5000);
    }
  },

  initializeJobs: async (token?: string) => {
    // Don't fetch jobs without a token (unless using mock data)
    if (!USE_MOCK_DATA && !token) {
      return;
    }

    try {
      const response = await videoApi.getJobs(token);
      if (response.success) {
        const activeJobs = response.data.filter(
          (job) => job.status === "pending" || job.status === "processing",
        );

        set({ activeJobs });

        // Connect WebSockets for all active jobs
        activeJobs.forEach((job) => {
          get().connectWebSocket(job.job_id);
        });
      }
    } catch (error) {
      // Nothing to do
    }
  },

  connectWebSocket: (jobId) => {
    const { websockets, updateJob } = get();

    // Don't create duplicate connections
    if (websockets.has(jobId)) {
      return;
    }

    if (USE_MOCK_DATA) {
      // Mock WebSocket with interval updates
      let progress =
        get().activeJobs.find((j) => j.job_id === jobId)?.progress_percentage ||
        0;

      const interval = setInterval(() => {
        const currentJob = get().activeJobs.find((j) => j.job_id === jobId);
        if (!currentJob) {
          clearInterval(interval);
          return;
        }

        progress = Math.min(100, progress + Math.random() * 15);

        const update: Partial<Job> = {
          progress_percentage: Math.floor(progress),
          status: progress >= 100 ? "completed" : "processing",
          current_step:
            progress >= 100
              ? "Rendering complete"
              : `Processing frame ${Math.floor(progress)}%`,
        };

        updateJob(jobId, update);

        if (progress >= 100) {
          clearInterval(interval);
          websockets.delete(jobId);
        }
      }, 2000);

      websockets.set(jobId, interval);
      set({ websockets: new Map(websockets) });
    } else {
      const wsUrl = `${process.env.NEXT_PUBLIC_APP_BACKEND_WEBSOCKET_URL || "ws://localhost:8000"}/videos/jobs/${jobId}/ws`;
      const ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const update: JobUpdate = JSON.parse(event.data);
          updateJob(jobId, {
            progress_percentage: update.progress_percentage,
            status: update.status as any,
            current_step: update.current_step,
          });

          if (update.final) {
            ws.close();
            websockets.delete(jobId);
          }
        } catch (error) {
          // Nothing to do
        }
      };

      ws.onerror = (error) => {
        //console.error("WebSocket error:", error)
        ws.close();
        websockets.delete(jobId);
      };

      ws.onclose = () => {
        websockets.delete(jobId);
      };

      websockets.set(jobId, ws);
      set({ websockets: new Map(websockets) });
    }
  },

  disconnectWebSocket: (jobId) => {
    const { websockets } = get();
    const connection = websockets.get(jobId);

    if (connection) {
      if (typeof connection === "object" && "close" in connection) {
        connection.close();
      } else {
        clearInterval(connection);
      }
      websockets.delete(jobId);
      set({ websockets: new Map(websockets) });
    }
  },
}));
