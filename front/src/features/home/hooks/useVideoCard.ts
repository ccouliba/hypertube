import { useState, type MouseEvent } from "react"
import type { VideoResult } from "@/types/search.types"
import { useDownload } from "@/hooks/useDownload"

const PLACEHOLDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='250' height='370'%3E%3Crect width='250' height='370' fill='%231f1f1f'/%3E%3Ctext x='125' y='185' font-family='sans-serif' font-size='14' fill='%23666' text-anchor='middle' dominant-baseline='middle'%3ENo Poster%3C/text%3E%3C/svg%3E"

export const useVideoCard = (video: VideoResult) => {
  const [open, setOpen] = useState(false)
  const {
    entry,
    hasTorrent,
    startDownload,
    pauseDownload,
    resumeDownload,
    deleteVideo,
    stopDownload,
    canDelete,
  } = useDownload(video)

  const poster = video.thumbnail ?? PLACEHOLDER
  const rating = video.rating != null ? video.rating.toFixed(1) : null
  const isDone = video.downloaded || entry?.status === "completed"
  const isDownloading = entry?.status === "downloading" || entry?.status === "queued"
  const isPaused = entry?.status === "paused"
  const isActive = isDownloading || isPaused
  const progress = entry?.progress ?? 0

  const onDownload = (event: MouseEvent) => {
    event.stopPropagation()
    if (!entry && !video.downloaded) startDownload()
  }

  const onPause = (event: MouseEvent) => {
    event.stopPropagation()
    pauseDownload()
  }

  const onResume = (event: MouseEvent) => {
    event.stopPropagation()
    resumeDownload()
  }

  const onStopOrDelete = (event: MouseEvent) => {
    event.stopPropagation()
    isActive ? stopDownload() : deleteVideo()
  }

  return {
    open,
    setOpen,
    poster,
    rating,
    isDone,
    isDownloading,
    isActive,
    progress,
    hasTorrent,
    canDelete,
    onDownload,
    onPause,
    onResume,
    onStopOrDelete,
  }
}
