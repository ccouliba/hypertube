import { useEffect, useRef } from "react"
import { useAppDispatch, useAppSelector } from "@/hooks/useAppStore"
import { pollStatus } from "@/store/slices/downloadSlice"

const POLL_INTERVAL_MS = 3000

export const useDownloadsPolling = () => {
  const dispatch = useAppDispatch()
  const entries = useAppSelector((state) => Object.values(state.downloads.items))
  const entriesRef = useRef(entries)

  useEffect(() => {
    entriesRef.current = entries
  }, [entries])

  useEffect(() => {
    const poll = () => {
      entriesRef.current
        .filter(
          (entry) =>
            (entry.status === "downloading" || entry.status === "queued") && entry.videoId
        )
        .forEach((entry) => {
        dispatch(pollStatus({
          contentType: entry.contentType,
          videoId: entry.videoId!,
          hash: entry.hash,
        }))
        })
    }

    poll()
    const timer = setInterval(poll, POLL_INTERVAL_MS)
    return () => clearInterval(timer)
  }, [dispatch])
}
