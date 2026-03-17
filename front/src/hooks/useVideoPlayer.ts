// useVideoPlayer — manages player open/close state and issues the stream token cookie before playback.
import { useState, useCallback } from "react"
import authService from "@/services/auth.service"
import type { VideoResult } from "@/types/search.types"

const BASE_URL = import.meta.env.VITE_API_URL ?? ""


export const useVideoPlayer = () => {
  const [video, setVideo] = useState<VideoResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const open = useCallback(async (v: VideoResult) => {
    setLoading(true)
    setError(null)
    try {
      await authService.issueStreamToken()
      setVideo(v)
    } catch {
      setError("Unable to start playback. Please try again.")
    } finally {
      setLoading(false)
    }
  }, [])

  const close = useCallback(() => {
    setVideo(null)
    setError(null)
  }, [])

  const streamUrl =
    video?.id != null
      ? `${BASE_URL}/api/video/${video.id}/stream?content_type=${video.content_type}`
      : null

  return { video, streamUrl, isOpen: video !== null, loading, error, open, close }
}
