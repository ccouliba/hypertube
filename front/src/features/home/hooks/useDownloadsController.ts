import { useEffect, useState } from "react"
import { useAppDispatch, useAppSelector } from "@/hooks/useAppStore"
import {
  deleteVideo,
  pauseDownload,
  restoreDownload,
  resumeDownload,
  type DownloadEntry,
} from "@/store/slices/downloadSlice"
import videoService from "@/services/video.service"

export const useDownloadsController = () => {
  const dispatch = useAppDispatch()
  const entries = useAppSelector((state) =>
    Object.values(state.downloads.items).filter((entry) => entry.status !== "completed")
  )
  const [modalVideo, setModalVideo] = useState<DownloadEntry["video"] | null>(null)

  useEffect(() => {
    let mounted = true
    videoService
      .getActiveDownloads()
      .then(({ videos }) => {
        if (!mounted) return
        videos.forEach((video) => {
          const hash = video.selected_torrent_hash
            ?? video.torrents?.[0]?.hash
            ?? (video.id != null ? `video:${video.id}` : null)
          if (!hash) return
          dispatch(restoreDownload({
            hash,
            contentType: video.content_type.toLowerCase(),
            video,
          }))
        })
      })
      .catch(() => {
        // The table remains usable with the state already held in Redux.
      })
    return () => { mounted = false }
  }, [dispatch])

  const pause = (entry: DownloadEntry) => {
    if (entry.videoId) {
      dispatch(pauseDownload({
        contentType: entry.contentType,
        videoId: entry.videoId,
        hash: entry.hash,
      }))
    }
  }

  const resume = (entry: DownloadEntry) => {
    if (entry.videoId) {
      dispatch(resumeDownload({
        contentType: entry.contentType,
        videoId: entry.videoId,
        hash: entry.hash,
      }))
    }
  }

  const stop = (entry: DownloadEntry) => {
    if (entry.videoId) {
      dispatch(deleteVideo({
        contentType: entry.contentType,
        videoId: entry.videoId,
        hash: entry.hash,
      }))
    }
  }

  return {
    entries,
    modalVideo,
    setModalVideo,
    pause,
    resume,
    stop,
  }
}
