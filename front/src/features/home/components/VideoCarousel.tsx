import React, { useState, useEffect } from "react"
import styled from "styled-components"
import type { VideoResult } from "@/types/search.types"
import VideoCard from "./VideoCard"

const PAGE_SIZE = 3

interface VideoCarouselProps {
  videos: VideoResult[]
}


const VideoCarousel: React.FC<VideoCarouselProps> = ({ videos }) => {
  const [offset, setOffset] = useState(0)

  const maxOffset = Math.max(0, videos.length - PAGE_SIZE)

  // Recale l'offset si des vidéos sont supprimées et qu'il dépasse le max
  useEffect(() => {
    setOffset((o) => Math.min(o, maxOffset))
  }, [maxOffset])

  const visible = videos.slice(offset, offset + PAGE_SIZE)
  const hasPrev = offset > 0
  const hasNext = offset < maxOffset

  return (
    <VideoCarouselView
      visible={visible}
      hasPrev={hasPrev}
      hasNext={hasNext}
      needsCarousel={videos.length > PAGE_SIZE}
      onPrev={() => setOffset((o) => Math.max(0, o - 1))}
      onNext={() => setOffset((o) => Math.min(maxOffset, o + 1))}
    />
  )
}

export default VideoCarousel


interface VideoCarouselViewProps {
  visible: VideoResult[]
  hasPrev: boolean
  hasNext: boolean
  needsCarousel: boolean
  onPrev: () => void
  onNext: () => void
}

export const VideoCarouselView: React.FC<VideoCarouselViewProps> = ({
  visible,
  hasPrev,
  hasNext,
  needsCarousel,
  onPrev,
  onNext,
}) => (
  <Wrapper>
    {needsCarousel && (
      <NavBtn onClick={onPrev} disabled={!hasPrev} aria-label="Previous">
        ‹
      </NavBtn>
    )}
    <Track $count={visible.length} $natural={!needsCarousel}>
      {visible.map((video, idx) => (
        <VideoCard key={video.id ?? `${video.title}-${idx}`} video={video} />
      ))}
    </Track>
    {needsCarousel && (
      <NavBtn onClick={onNext} disabled={!hasNext} aria-label="Next">
        ›
      </NavBtn>
    )}
  </Wrapper>
)


const Wrapper = styled.div`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};
`

const Track = styled.div<{ $count: number; $natural: boolean }>`
  display: grid;
  grid-template-columns: ${({ $count, $natural }) =>
    $natural
      ? "repeat(auto-fill, minmax(130px, 1fr))"
      : `repeat(${$count}, 1fr)`};
  gap: ${({ theme }) => theme.spacing.md};
  flex: 1;
  min-width: 0;
`

const NavBtn = styled.button`
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 50%;
  color: ${({ theme }) => theme.colors.text};
  font-size: 20px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;

  &:disabled {
    opacity: 0.25;
    cursor: default;
  }

  &:not(:disabled):hover {
    background: ${({ theme }) => theme.colors.surfaceHover};
  }
`
