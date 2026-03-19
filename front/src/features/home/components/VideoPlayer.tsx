// Full-screen video player overlay — renders on top of everything (z-index 1100).
// Handles Escape key, body scroll lock, and crossOrigin credentials for the stream cookie.
import React, { useEffect, useRef } from "react"
import styled, { keyframes } from "styled-components"
import type { VideoResult } from "@/types/search.types"

interface VideoPlayerProps {
  video: VideoResult
  streamUrl: string
  onClose: () => void
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ video, streamUrl, onClose }) => {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose()
    }
    document.addEventListener("keydown", onKey)
    return () => document.removeEventListener("keydown", onKey)
  }, [onClose])

  useEffect(() => {
    document.body.style.overflow = "hidden"
    return () => {
      document.body.style.overflow = ""
    }
  }, [])

  return (
    <Overlay
      role="dialog"
      aria-modal="true"
      aria-label={`Now playing: ${video.title}`}
      onClick={onClose}
    >
      <PlayerWrapper onClick={(e) => e.stopPropagation()}>
        <Header>
          <VideoTitle>{video.title}</VideoTitle>
          <CloseBtn onClick={onClose} aria-label="Close player">
            ✕
          </CloseBtn>
        </Header>
        <StyledVideo
          ref={videoRef}
          src={streamUrl}
          controls
          autoPlay
          playsInline
          crossOrigin="use-credentials"
        />
      </PlayerWrapper>
    </Overlay>
  )
}

export default VideoPlayer


const fadeIn = keyframes`
  from { opacity: 0 }
  to   { opacity: 1 }
`

const Overlay = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 24px;
  animation: ${fadeIn} 0.2s ease;
`

const PlayerWrapper = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1100px;
  gap: 12px;
`

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
`

const VideoTitle = styled.h2`
  font-size: ${({ theme }) => theme.fontSizes.lg};
  color: ${({ theme }) => theme.colors.text};
  margin: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
`

const CloseBtn = styled.button`
  background: rgba(255, 255, 255, 0.12);
  border: none;
  color: ${({ theme }) => theme.colors.text};
  font-size: 18px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s;

  &:hover {
    background: rgba(255, 255, 255, 0.25);
  }
`

const StyledVideo = styled.video`
  width: 100%;
  max-height: 75vh;
  border-radius: ${({ theme }) => theme.radii.md};
  background: #000;
  display: block;
`
