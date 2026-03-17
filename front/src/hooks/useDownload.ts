// useDownload — all download-related state and actions for a single video (start, pause, resume, delete, poll).
import { useEffect, useCallback, useMemo } from "react"
import { useAppDispatch, useAppSelector } from "@/hooks/useAppStore"
import {
  startDownload as startDownloadThunk,
  pauseDownload as pauseDownloadThunk,
  resumeDownload as resumeDownloadThunk,
  deleteVideo as deleteVideoThunk,
  restoreDownload,
  pollStatus,
} from "@/store/slices/downloadSlice"
import type { DownloadPayload } from "@/services/video.service"
import type { VideoResult } from "@/types/search.types"

export const useDownload = (video: VideoResult) => {
  const dispatch = useAppDispatch()

  const bestTorrent = useMemo(() => {
    if (!video.torrents?.length) return null
    return video.torrents.reduce(
      (best, t) => ((t.seeds ?? 0) > (best.seeds ?? 0) ? t : best),
      video.torrents[0]
    )
  }, [video.torrents])

  const hash = bestTorrent?.hash ?? ""

  const entry = useAppSelector((state) => {
    if (hash && state.downloads.items[hash]) return state.downloads.items[hash]
    if (video.id) return Object.values(state.downloads.items).find((e) => e.videoId === video.id)
    return undefined
  })

  useEffect(() => {
    if (entry || !hash || !video.id) return
    const { download_status: dbStatus } = video
    if (dbStatus === "downloading" || dbStatus === "paused") {
      dispatch(restoreDownload({ hash, contentType: video.content_type, video }))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hash, video.id])

  useEffect(() => {
    if (entry?.status !== "downloading" || !entry.videoId) return
    const activeHash = entry.hash
    const id = setInterval(() => {
      dispatch(pollStatus({ contentType: entry.contentType, videoId: entry.videoId!, hash: activeHash }))
    }, 3000)
    return () => clearInterval(id)
  }, [entry?.status, entry?.videoId, entry?.contentType, entry?.hash, dispatch])

  const startDownload = useCallback(() => {
    if (!bestTorrent?.hash || !bestTorrent?.url) return
    const payload: DownloadPayload = {
      title: video.title,
      torrent_hash: bestTorrent.hash,
      torrent_url: bestTorrent.url,
      // Without this part below, i get 422
      ...(video.year != null && { year: video.year }),
      ...(video.rating != null && { rating: video.rating }),
      ...(video.genres?.length && { genres: video.genres }),
      ...(video.synopsis && { synopsis: video.synopsis }),
      ...(video.thumbnail && { thumbnail: video.thumbnail }),
      ...(video.large_cover && { cover_image: video.large_cover }), 
      provider: typeof video.provider === "string" ? video.provider : "search",
    }
    dispatch(startDownloadThunk({ contentType: video.content_type, payload, video }))
  }, [dispatch, video, bestTorrent])

  const pauseDownload = useCallback(() => {
    if (!entry?.videoId) return
    dispatch(pauseDownloadThunk({ contentType: entry.contentType, videoId: entry.videoId, hash: entry.hash }))
  }, [dispatch, entry])

  const resumeDownload = useCallback(() => {
    if (!entry?.videoId) return
    dispatch(resumeDownloadThunk({ contentType: entry.contentType, videoId: entry.videoId, hash: entry.hash }))
  }, [dispatch, entry])


  const videoId = entry?.videoId ?? (video.downloaded ? video.id : undefined)
  const contentTypeForDelete = entry?.contentType ?? video.content_type

  const deleteVideo = useCallback(() => {
    if (!videoId) return
    const h = (entry?.hash ?? hash) || (video.torrents?.[0]?.hash ?? "")
    dispatch(deleteVideoThunk({ contentType: contentTypeForDelete, videoId, hash: h }))
  }, [dispatch, videoId, contentTypeForDelete, hash, video.torrents, entry?.hash])

  const stopDownload = deleteVideo

  return {
    entry,
    hasTorrent: !!(bestTorrent?.hash && bestTorrent?.url),
    startDownload,
    pauseDownload,
    resumeDownload,
    deleteVideo,
    stopDownload,
    canDelete: !!(videoId),
  }
}
