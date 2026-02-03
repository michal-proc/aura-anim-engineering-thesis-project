import type { Video, VideoExplore, Job } from "@/types/video.types";
import type { User } from "@/types/auth.types";

export const USE_MOCK_DATA = process.env.NEXT_PUBLIC_USE_MOCK_DATA === "true";

export const mockUser: User = {
  id: 1,
  email: "test@example.com",
  username: "demouser",
  full_name: "Name Surname"
};

const videoUrls = {
  rocket:
    "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/rocket-yiuCCa4UiO2pJEyeg6ge2skdtXzHvH.mp4",
  dale: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/corgi-LxIFr1dXqlnFEQLV9FvibfRphZYUmC.mp4",
  neonCity:
    "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/assets_task_01k899qfkme2k86x7fmzw0qn6m_task_01k899qfkme2k86x7fmzw0qn6m_genid_d387d5b6-1fa3-4e0b-97a6-24e010eca8db_25_10_23_19_47_310576_videos_00000_63372040_source-KSinGkLjVSJb3Iikx5dRglPVS1DLS6.mp4",
  cork: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/sea-PX7hSETUr5r4kSTkP3uLa8lgzr4D6l.mp4",
  vibration:
    "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/_MConverter.eu_image-MxSjBG1Gb76Nhv37HnsvYBjgM7FrxQ.mp4",
};

export const mockVideos: Video[] = [
  {
    id: "vid-1",
    user_id: 1,
    name: "Rocket",
    url: videoUrls.rocket,
    shared: false,
    created_at: "2024-03-20T14:30:00Z",
    job: {
      job_id: "job-1",
      status: "completed",
      progress_percentage: 100,
      created_at: "2024-03-20T14:25:00Z",
      completed_at: "2024-03-20T14:30:00Z",
      parameters: {
        prompt: "Spectacular rocket launch with smoke and flames",
        width: 1920,
        height: 1080,
        video_length: 12,
        fps: 30,
      },
    },
  },
  {
    id: "vid-2",
    user_id: 1,
    name: "Dale",
    url: videoUrls.dale,
    shared: false,
    created_at: "2024-03-19T09:15:00Z",
    job: {
      job_id: "job-2",
      status: "completed",
      progress_percentage: 100,
      created_at: "2024-03-19T09:10:00Z",
      completed_at: "2024-03-19T09:15:00Z",
      parameters: {
        prompt: "A cute corgi running and playing in the park",
        width: 1920,
        height: 1080,
        video_length: 8,
        fps: 30,
      },
    },
  },
  {
    id: "vid-3",
    user_id: 1,
    name: "Neon City",
    url: videoUrls.neonCity,
    shared: false,
    created_at: "2024-03-18T18:00:00Z",
    job: {
      job_id: "job-3",
      status: "completed",
      progress_percentage: 100,
      created_at: "2024-03-18T17:55:00Z",
      completed_at: "2024-03-18T18:00:00Z",
      parameters: {
        prompt: "Futuristic neon city with dynamic animations",
        width: 1920,
        height: 1080,
        video_length: 20,
        fps: 30,
      },
    },
  },
  {
    id: "vid-4",
    user_id: 1,
    name: "Cork",
    url: videoUrls.cork,
    shared: false,
    created_at: "2024-03-17T12:00:00Z",
    job: {
      job_id: "job-4",
      status: "completed",
      progress_percentage: 100,
      created_at: "2024-03-17T11:55:00Z",
      completed_at: "2024-03-17T12:00:00Z",
      parameters: {
        prompt: "Peaceful ocean waves with blue water",
        width: 1920,
        height: 1080,
        video_length: 10,
        fps: 30,
      },
    },
  },
  {
    id: "vid-5",
    user_id: 1,
    name: "Vibration",
    url: videoUrls.vibration,
    shared: false,
    created_at: "2024-03-16T15:30:00Z",
    job: {
      job_id: "job-5",
      status: "completed",
      progress_percentage: 100,
      created_at: "2024-03-16T15:25:00Z",
      completed_at: "2024-03-16T15:30:00Z",
      parameters: {
        prompt: "Colorful abstract motion graphics with vibrations",
        width: 1920,
        height: 1080,
        video_length: 15,
        fps: 30,
      },
    },
  },
];

export const mockExploreVideos: VideoExplore[] = [
  {
    name: "Rocket",
    prompt: "Dramatic rocket launch with fire and smoke",
    url: videoUrls.rocket,
  },
  {
    name: "Dale",
    prompt: "Adorable corgi having fun outdoors",
    url: videoUrls.dale,
  },
  {
    name: "Neon City",
    prompt: "Futuristic neon city with dynamic animations",
    url: videoUrls.neonCity,
  },
  {
    name: "Cork",
    prompt: "Serene ocean waves on the shore",
    url: videoUrls.cork,
  },
  {
    name: "Vibration",
    prompt: "Colorful abstract motion design with vibrations",
    url: videoUrls.vibration,
  },
];

export const mockJobs: Job[] = [
  {
    job_id: "job-1",
    vid_id: "vid-1",
    status: "completed",
    progress_percentage: 100,
    current_step: "Rendering complete",
    created_at: "2024-03-20T14:25:00Z",
    completed_at: "2024-03-20T14:30:00Z",
    marked_as_read: true,
    parameters: {
      prompt: "Spectacular rocket launch with smoke and flames",
      width: 1920,
      height: 1080,
      video_length: 12,
      fps: 30,
      output_format: "mp4",
    },
  },
  {
    job_id: "job-2",
    vid_id: "vid-2",
    status: "completed",
    progress_percentage: 100,
    current_step: "Rendering complete",
    created_at: "2024-03-19T09:10:00Z",
    completed_at: "2024-03-19T09:15:00Z",
    marked_as_read: true,
    parameters: {
      prompt: "A cute corgi running and playing in the park",
      width: 1920,
      height: 1080,
      video_length: 8,
      fps: 30,
      output_format: "mp4",
    },
  },
  {
    job_id: "job-3",
    vid_id: "vid-3",
    status: "completed",
    progress_percentage: 100,
    current_step: "Rendering complete",
    created_at: "2024-03-18T17:55:00Z",
    completed_at: "2024-03-18T18:00:00Z",
    marked_as_read: true,
    parameters: {
      prompt: "Futuristic neon city with dynamic animations",
      width: 1920,
      height: 1080,
      video_length: 20,
      fps: 30,
      output_format: "mp4",
    },
  },
  {
    job_id: "job-4",
    vid_id: "vid-4",
    status: "completed",
    progress_percentage: 100,
    current_step: "Rendering complete",
    created_at: "2024-03-17T11:55:00Z",
    completed_at: "2024-03-17T12:00:00Z",
    marked_as_read: true,
    parameters: {
      prompt: "Peaceful ocean waves with blue water",
      width: 1920,
      height: 1080,
      video_length: 10,
      fps: 30,
      output_format: "mp4",
    },
  },
  {
    job_id: "job-5",
    vid_id: "vid-5",
    status: "completed",
    progress_percentage: 100,
    current_step: "Rendering complete",
    created_at: "2024-03-16T15:25:00Z",
    completed_at: "2024-03-16T15:30:00Z",
    marked_as_read: false,
    parameters: {
      prompt: "Colorful abstract motion graphics with vibrations",
      width: 1920,
      height: 1080,
      video_length: 15,
      fps: 30,
      output_format: "mp4",
    },
  },
  {
    job_id: "job-6",
    vid_id: null,
    status: "processing",
    progress_percentage: 65,
    current_step: "Generating frames",
    created_at: "2024-03-21T10:00:00Z",
    completed_at: null,
    marked_as_read: false,
    parameters: {
      prompt: "Fireworks exploding over city skyline at night",
      width: 1920,
      height: 1080,
      video_length: 18,
      fps: 30,
      output_format: "mp4",
    },
  },
  {
    job_id: "job-7",
    vid_id: null,
    status: "pending",
    progress_percentage: 0,
    current_step: "Waiting in queue",
    created_at: "2024-03-21T11:30:00Z",
    completed_at: null,
    marked_as_read: false,
    parameters: {
      prompt: "Underwater coral reef with tropical fish swimming",
      width: 1920,
      height: 1080,
      video_length: 25,
      fps: 30,
      output_format: "mp4",
    },
  },
];

export const mockJobsMeta = {
  total_count: mockJobs.length,
  active_count: mockJobs.filter(
    (j) => j.status === "pending" || j.status === "processing",
  ).length,
  failed_count: mockJobs.filter((j) => j.status === "failed").length,
  completed_count: mockJobs.filter((j) => j.status === "completed").length,
  unread_count: mockJobs.filter((j) => !j.marked_as_read).length,
};

export async function getMockVideoBlob(id: string): Promise<Blob> {
  const video = mockVideos.find((v) => v.id === id);
  if (!video) {
    throw new Error(`Video ${id} not found`);
  }

  const response = await fetch(video.url);
  if (!response.ok) {
    throw new Error(`Failed to fetch video: ${response.statusText}`);
  }

  return await response.blob();
}
