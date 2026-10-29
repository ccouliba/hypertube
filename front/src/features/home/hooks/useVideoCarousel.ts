import { useEffect, useState } from "react"
import type { VideoResult } from "@/types/search.types"

export const CAROUSEL_PAGE_SIZE = 5

export const useVideoCarousel = (videos: VideoResult[]) => {
  const [offset, setOffset] = useState(0)
  const maxOffset = Math.max(0, videos.length - CAROUSEL_PAGE_SIZE)

  useEffect(() => {
    setOffset((current) => Math.min(current, maxOffset))
  }, [maxOffset])

  return {
    visible: videos.slice(offset, offset + CAROUSEL_PAGE_SIZE),
    hasPrev: offset > 0,
    hasNext: offset < maxOffset,
    needsCarousel: videos.length > CAROUSEL_PAGE_SIZE,
    onPrev: () => setOffset((current) => Math.max(0, current - 1)),
    onNext: () => setOffset((current) => Math.min(maxOffset, current + 1)),
  }
}
