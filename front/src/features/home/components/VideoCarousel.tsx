import React from "react"
import type { VideoResult } from "@/types/search.types"
import { useVideoCarousel } from "../hooks/useVideoCarousel"
import VideoCarouselView from "./VideoCarouselView"

interface VideoCarouselProps {
  videos: VideoResult[]
}


const VideoCarousel: React.FC<VideoCarouselProps> = ({ videos }) => {
  const { visible, hasPrev, hasNext, needsCarousel, onPrev, onNext } = useVideoCarousel(videos)

  return (
    <VideoCarouselView
      visible={visible}
      hasPrev={hasPrev}
      hasNext={hasNext}
      needsCarousel={needsCarousel}
      onPrev={onPrev}
      onNext={onNext}
    />
  )
}

export default VideoCarousel
