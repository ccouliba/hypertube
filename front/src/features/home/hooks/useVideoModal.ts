import { useEffect, type MouseEvent } from "react"
import type { VideoResult } from "@/types/search.types"
import { useDownload } from "@/hooks/useDownload"
import { useVideoPlayer } from "@/hooks/useVideoPlayer"

const PLACEHOLDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='600'%3E%3Crect width='400' height='600' fill='%231f1f1f'/%3E%3Ctext x='200' y='300' font-family='sans-serif' font-size='16' fill='%23666' text-anchor='middle' dominant-baseline='middle'%3ENo Poster%3C/text%3E%3C/svg%3E"

export const useVideoModal = (video: VideoResult, onClose: () => void) => {
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
  const player = useVideoPlayer()

  const poster = video.large_cover ?? video.thumbnail ?? PLACEHOLDER
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

  const onWatch = (event: MouseEvent) => {
    event.stopPropagation()
    player.open(video)
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

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose()
    }
    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [onClose])

  useEffect(() => {
    document.body.style.overflow = "hidden"
    return () => { document.body.style.overflow = "" }
  }, [])

  return {
    entry,
    player,
    poster,
    rating,
    isDone,
    isDownloading,
    isPaused,
    isActive,
    progress,
    hasTorrent,
    canDelete,
    onDownload,
    onWatch,
    onPause,
    onResume,
    onStopOrDelete,
  }
}
