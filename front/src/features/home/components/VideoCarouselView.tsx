import React from "react"
import styled from "styled-components"
import type { VideoResult } from "@/types/search.types"
import VideoCard from "./VideoCard"

interface VideoCarouselViewProps {
  visible: VideoResult[]
  hasPrev: boolean
  hasNext: boolean
  needsCarousel: boolean
  onPrev: () => void
  onNext: () => void
}

const VideoCarouselView: React.FC<VideoCarouselViewProps> = ({
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

export default VideoCarouselView

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
      : `repeat(${$count}, minmax(130px, 1fr))`};
  gap: ${({ theme }) => theme.spacing.md};
  flex: 1;
  min-width: 0;
  overflow: hidden;
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
