export type JobStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | "cancelled";

export interface GenerateVideoPayload {
  prompt: string;
  negative_prompt: string;
  aspect_ratio: [number, number];
  resolution: number;
  video_length: number;
  fps: number;
  output_format: string;
  base_model: string;
  motion_adapter: string;
  inference_steps?: number;
}

export interface VideoJobParameters {
  prompt: string;
  width: number;
  height: number;
  video_length: number;
  fps: number;
}

export interface VideoJob {
  job_id: string;
  status: JobStatus;
  progress_percentage: number;
  created_at: string;
  completed_at: string | null;
  parameters: VideoJobParameters;
}

export interface Video {
  id: string;
  user_id: number;
  name: string;
  url: string;
  shared: boolean;
  created_at: string;
  job: VideoJob;
}

export interface GetVideosResponse {
  success: true;
  data: Video[];
}

export interface GetVideoResponse {
  success: true;
  data: Video;
}

export interface VideoExplore {
  name: string;
  prompt: string;
  url: string;
}

export interface GetVideoExploreResponse {
  success: true;
  data: VideoExplore[];
}

export interface Job {
  job_id: string;
  vid_id?: string | null;
  status: JobStatus;
  progress_percentage: number;
  current_step?: string;
  created_at: string;
  completed_at: string | null;
  error_message?: string | null;
  marked_as_read: boolean;
  parameters: VideoJobParameters;
}

export interface JobsMeta {
  total_count: number;
  active_count: number;
  failed_count: number;
  completed_count: number;
  unread_count: number;
}

export interface GetJobsResponse {
  success: true;
  data: Job[];
  meta: JobsMeta;
}
