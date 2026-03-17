// Downloads slice — Redux state for active downloads (start, poll, pause, resume, delete).
import { createSlice, createAsyncThunk, type PayloadAction } from "@reduxjs/toolkit"
import videoService, { type DownloadPayload } from "@/services/video.service"
import type { VideoResult } from "@/types/search.types"

export type DownloadStatus = "queued" | "downloading" | "paused" | "completed" | "error"

export interface DownloadEntry {
  hash: string
  contentType: string
  status: DownloadStatus
  progress: number
  videoId?: number
  video: VideoResult
}

interface DownloadsState {
  items: Record<string, DownloadEntry>
}

const initialState: DownloadsState = { items: {} }

const normalize = (s?: string): DownloadStatus => {
  if (!s) return "downloading"
  const l = s.toLowerCase()
  if (l.includes("complet")) return "completed"
  if (l.includes("pause")) return "paused"
  if (l.includes("error") || l.includes("fail")) return "error"
  if (l.includes("queue") || l.includes("pending")) return "queued"
  return "downloading"
}

export const startDownload = createAsyncThunk(
  "downloads/start",
  async (
    { contentType, payload, video }: { contentType: string; payload: DownloadPayload; video: VideoResult },
    { rejectWithValue }
  ) => {
    try {
      const result = await videoService.startDownload(contentType, payload)
      return { hash: payload.torrent_hash, contentType, video, result }
    } catch (err) {
      return rejectWithValue((err as Error).message)
    }
  }
)

export const pollStatus = createAsyncThunk(
  "downloads/poll",
  async ({ contentType, videoId, hash }: { contentType: string; videoId: number; hash: string }) => {
    const result = await videoService.getStatus(contentType, videoId)
    return { hash, result }
  }
)

export const pauseDownload = createAsyncThunk(
  "downloads/pause",
  async ({ contentType, videoId, hash }: { contentType: string; videoId: number; hash: string }) => {
    await videoService.pauseDownload(contentType, videoId)
    return hash
  }
)

export const resumeDownload = createAsyncThunk(
  "downloads/resume",
  async ({ contentType, videoId, hash }: { contentType: string; videoId: number; hash: string }) => {
    await videoService.resumeDownload(contentType, videoId)
    return hash
  }
)

export const deleteVideo = createAsyncThunk(
  "downloads/delete",
  async (
    { contentType, videoId, hash }: { contentType: string; videoId: number; hash: string },
    { rejectWithValue }
  ) => {
    try {
      await videoService.deleteVideo(contentType, videoId)
      return hash
    } catch (err) {
      return rejectWithValue((err as Error).message)
    }
  }
)

const downloadSlice = createSlice({
  name: "downloads",
  initialState,
  reducers: {
    restoreDownload(state, action: PayloadAction<{ hash: string; contentType: string; video: VideoResult }>) {
      const { hash, contentType, video } = action.payload
      if (state.items[hash]) return
      state.items[hash] = {
        hash,
        contentType,
        status: normalize(video.download_status),
        progress: video.download_progress ?? 0,
        videoId: video.id,
        video,
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(startDownload.pending, (state, action) => {
        const { contentType, payload, video } = action.meta.arg
        const hash = payload.torrent_hash
        state.items[hash] = { hash, contentType, status: "queued", progress: 0, video }
      })
      .addCase(startDownload.fulfilled, (state, action) => {
        const { hash, contentType, video, result } = action.payload
        state.items[hash] = {
          hash,
          contentType,
          status: normalize(result.video?.download_status),
          progress: result.video?.download_progress ?? 0,
          videoId: result.video_id,
          video: { ...video, id: result.video_id },
        }
      })
      .addCase(startDownload.rejected, (state, action) => {
        const hash = action.meta.arg.payload.torrent_hash
        if (state.items[hash]) state.items[hash].status = "error"
      })
      .addCase(pollStatus.fulfilled, (state, action) => {
        const { hash, result } = action.payload
        if (!state.items[hash]) return
        state.items[hash].status = normalize(result.status)
        state.items[hash].progress = result.progress ?? state.items[hash].progress
      })
      .addCase(pauseDownload.fulfilled, (state, action) => {
        const hash = action.payload
        if (state.items[hash]) state.items[hash].status = "paused"
      })
      .addCase(resumeDownload.fulfilled, (state, action) => {
        const hash = action.payload
        if (state.items[hash]) state.items[hash].status = "downloading"
      })
      .addCase(deleteVideo.fulfilled, (state, action) => {
        delete state.items[action.payload]
      })
  },
})

export const { restoreDownload } = downloadSlice.actions
export default downloadSlice.reducer
