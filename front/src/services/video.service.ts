// Video service — all HTTP calls to /api/video (list, download, status, pause/resume, delete).
import apiClient from "@/api/axios"
import type { VideoResult } from "@/types/search.types"

export interface VideoListResponse {
  videos: VideoResult[]
  total: number
}

export interface DownloadPayload {
  title: string
  torrent_hash: string
  torrent_url: string
  year?: number
  rating?: number
  genres?: string[]
  synopsis?: string
  thumbnail?: string
  cover_image?: string
  provider?: string
}

export interface DownloadResponse {
  message: string
  video_id: number
  task_id: string
  video: {
    id: number
    title: string
    download_status: string
    download_progress: number
    content_type: string
  }
}

export interface StatusResponse {
  video_id: number
  status: string
  progress: number
}

const videoService = {
  startDownload: (contentType: string, payload: DownloadPayload): Promise<DownloadResponse> =>
    apiClient
      .post<DownloadResponse>("/api/video/download", payload, {
        params: { content_type: contentType },
      })
      .then((r) => r.data),

  getStatus: (contentType: string, videoId: number): Promise<StatusResponse> =>
    apiClient
      .get<StatusResponse>(`/api/video/${videoId}/status`, {
        params: { content_type: contentType },
      })
      .then((r) => r.data),

  pauseDownload: (contentType: string, videoId: number): Promise<void> =>
    apiClient
      .post(`/api/video/${videoId}/pause`, {}, { params: { content_type: contentType } })
      .then(() => undefined),

  resumeDownload: (contentType: string, videoId: number): Promise<void> =>
    apiClient
      .post(`/api/video/${videoId}/resume`, {}, { params: { content_type: contentType } })
      .then(() => undefined),

  deleteVideo: (contentType: string, videoId: number): Promise<void> =>
    apiClient
      .delete(`/api/video/${videoId}`, { params: { content_type: contentType } })
      .then(() => undefined),

  getAll: (): Promise<VideoListResponse> =>
    apiClient
      .get<VideoListResponse>("/api/video/", { params: { content_type: "all" } })
      .then((r) => r.data),

  getActiveDownloads: (): Promise<VideoListResponse> =>
    apiClient
      .get<VideoListResponse>("/api/video/active_downloads", { params: { content_type: "all" } })
      .then((r) => r.data),
}

export default videoService
