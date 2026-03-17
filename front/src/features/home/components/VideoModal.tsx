// VideoModal — full detail modal for a video: poster, metadata, download controls, and Watch button.
import React, { useEffect } from "react"
import styled, { keyframes } from "styled-components"
import type { VideoResult } from "@/types/search.types"
import { useDownload } from "@/hooks/useDownload"
import { useVideoPlayer } from "@/hooks/useVideoPlayer"
import VideoPlayer from "./VideoPlayer"

const PLACEHOLDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='600'%3E%3Crect width='400' height='600' fill='%231f1f1f'/%3E%3Ctext x='200' y='300' font-family='sans-serif' font-size='16' fill='%23666' text-anchor='middle' dominant-baseline='middle'%3ENo Poster%3C/text%3E%3C/svg%3E"
const LARGE_RADIUS = 27
const LARGE_CIRC = +(2 * Math.PI * LARGE_RADIUS).toFixed(2)


interface VideoModalProps {
  video: VideoResult
  onClose: () => void
}

const VideoModal: React.FC<VideoModalProps> = ({ video, onClose }) => {
  const { entry, hasTorrent, startDownload, pauseDownload, resumeDownload, deleteVideo, stopDownload, canDelete } = useDownload(video)
  const player = useVideoPlayer()

  const poster = video.large_cover ?? video.thumbnail ?? PLACEHOLDER
  const rating = video.rating != null ? video.rating.toFixed(1) : null
  const isDone = video.downloaded || entry?.status === "completed"
  const isDownloading = entry?.status === "downloading" || entry?.status === "queued"
  const isPaused = entry?.status === "paused"
  const isActive = isDownloading || isPaused
  const progress = entry?.progress ?? 0

  const handleDownloadClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (!entry && !video.downloaded) startDownload()
  }

  const handleWatchClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    player.open(video)
  }

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose() }
    document.addEventListener("keydown", onKey)
    return () => document.removeEventListener("keydown", onKey)
  }, [onClose])

  useEffect(() => {
    document.body.style.overflow = "hidden"
    return () => { document.body.style.overflow = "" }
  }, [])

  return (
    <>
      <VideoModalView
        video={video}
        poster={poster}
        rating={rating}
        isDone={isDone}
        isDownloading={isDownloading}
        isPaused={isPaused}
        isActive={isActive}
        progress={progress}
        hasTorrent={hasTorrent}
        canDelete={canDelete}
        playerLoading={player.loading}
        playerError={player.error}
        onClose={onClose}
        onDownload={handleDownloadClick}
        onWatch={handleWatchClick}
        onPause={(e) => { e.stopPropagation(); pauseDownload() }}
        onResume={(e) => { e.stopPropagation(); resumeDownload() }}
        onStopOrDelete={(e) => { e.stopPropagation(); isActive ? stopDownload() : deleteVideo() }}
      />
      {player.isOpen && player.streamUrl && (
        <VideoPlayer
          video={video}
          streamUrl={player.streamUrl}
          onClose={player.close}
        />
      )}
    </>
  )
}

export default VideoModal

interface VideoModalViewProps {
  video: VideoResult
  poster: string
  rating: string | null
  isDone: boolean
  isDownloading: boolean
  isPaused: boolean
  isActive: boolean
  progress: number
  hasTorrent: boolean
  canDelete: boolean
  playerLoading: boolean
  playerError: string | null
  onClose: () => void
  onDownload: (e: React.MouseEvent) => void
  onWatch: (e: React.MouseEvent) => void
  onPause: (e: React.MouseEvent) => void
  onResume: (e: React.MouseEvent) => void
  onStopOrDelete: (e: React.MouseEvent) => void
}

export const VideoModalView: React.FC<VideoModalViewProps> = ({
  video,
  poster,
  rating,
  isDone,
  isDownloading,
  isPaused,
  isActive,
  progress,
  hasTorrent,
  canDelete,
  playerLoading,
  playerError,
  onClose,
  onDownload,
  onWatch,
  onPause,
  onResume,
  onStopOrDelete,
}) => (
  <Backdrop onClick={onClose}>
    <Dialog onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-label={video.title}>
      <CloseBtn onClick={onClose} aria-label="Close">✕</CloseBtn>
      <PosterCol>
        <Poster src={poster} alt={video.title} />
      </PosterCol>
      <InfoCol>
        <Title>{video.title}</Title>
        <Meta>
          {video.year && <MetaItem>{video.year}</MetaItem>}
          {rating && <MetaItem><Star>★</Star> {rating}</MetaItem>}
          {video.content_type && (
            <TypePill>{video.content_type === "movie" ? "Movie" : "TV Show"}</TypePill>
          )}
        </Meta>
        {video.genres && video.genres.length > 0 && (
          <Genres>{video.genres.join(" · ")}</Genres>
        )}
        {video.synopsis
          ? <Synopsis>{video.synopsis}</Synopsis>
          : <NoSynopsis>No synopsis available.</NoSynopsis>
        }
        <ModalActions>
          {(isDone || isDownloading) && (
            <WatchBtn onClick={onWatch} disabled={playerLoading} aria-label="Watch">
              {playerLoading ? "Loading…" : "▶ Watch"}
            </WatchBtn>
          )}
          {playerError && <PlayerError>{playerError}</PlayerError>}
          {isActive && (
            <ModalCtrlArea>
              {isDownloading && (
                <ModalCtrlBtn onClick={onPause} title="Pause">
                  ⏸ Pause
                </ModalCtrlBtn>
              )}
              {isPaused && (
                <ModalCtrlBtn onClick={onResume} title="Resume">
                  ▶ Resume
                </ModalCtrlBtn>
              )}
              <ModalProgressText>{Math.round(progress)}%</ModalProgressText>
            </ModalCtrlArea>
          )}
          {canDelete && (
            <ModalRingWrapper>
              <ModalRingSvg viewBox="0 0 60 60">
                <ModalTrackCircle cx="30" cy="30" r={LARGE_RADIUS} />
              </ModalRingSvg>
              <ModalDownloadBtn
                onClick={onStopOrDelete}
                aria-label={isActive ? "Cancel" : "Remove"}
                title={isActive ? "Cancel download" : "Remove from board"}
              >
                {isActive ? (
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <rect x="5" y="5" width="14" height="14" rx="1" />
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <line x1="4" y1="12" x2="20" y2="12" />
                  </svg>
                )}
              </ModalDownloadBtn>
            </ModalRingWrapper>
          )}
          {(hasTorrent || isDone) && (
            <ModalRingWrapper>
              <ModalRingSvg viewBox="0 0 60 60">
                <ModalTrackCircle cx="30" cy="30" r={LARGE_RADIUS} />
                <ModalProgressArc
                  cx="30" cy="30" r={LARGE_RADIUS}
                  $circ={LARGE_CIRC} $pct={progress} $active={isActive} $done={isDone}
                />
              </ModalRingSvg>
              {isDone ? (
                <ModalGreenCheckBtn aria-label="Downloaded" title="Downloaded">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </ModalGreenCheckBtn>
              ) : !isActive ? (
                <ModalDownloadBtn onClick={onDownload} aria-label="Download" title="Download">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <line x1="12" y1="4" x2="12" y2="20" />
                    <line x1="4" y1="12" x2="20" y2="12" />
                  </svg>
                </ModalDownloadBtn>
              ) : isDownloading ? (
                <ModalDownloadBtn onClick={onPause} aria-label="Pause" title="Pause">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <rect x="5" y="4" width="4" height="16" rx="1" />
                    <rect x="15" y="4" width="4" height="16" rx="1" />
                  </svg>
                </ModalDownloadBtn>
              ) : (
                <ModalDownloadBtn onClick={onResume} aria-label="Resume" title="Resume">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="6,4 20,12 6,20" />
                  </svg>
                </ModalDownloadBtn>
              )}
            </ModalRingWrapper>
          )}
        </ModalActions>
      </InfoCol>
    </Dialog>
  </Backdrop>
)

const fadeIn = keyframes`
  from { opacity: 0 }
  to   { opacity: 1 }
`

const slideUp = keyframes`
  from { transform: translateY(24px); opacity: 0 }
  to   { transform: translateY(0);    opacity: 1 }
`

const Backdrop = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
  animation: ${fadeIn} 0.18s ease;
`

const Dialog = styled.div`
  position: relative;
  display: flex;
  gap: 32px;
  background: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.radii.md};
  overflow: hidden;
  max-width: 860px;
  width: 100%;
  max-height: 90vh;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.8);
  animation: ${slideUp} 0.22s ease;

  @media (max-width: 600px) {
    flex-direction: column;
    max-height: 92vh;
    overflow-y: auto;
  }
`

const CloseBtn = styled.button`
  position: absolute;
  top: 12px;
  right: 14px;
  background: rgba(0, 0, 0, 0.55);
  border: none;
  color: #fff;
  font-size: 18px;
  line-height: 1;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  z-index: 10;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
`

const PosterCol = styled.div`
  flex-shrink: 0;
  width: 260px;

  @media (max-width: 600px) {
    width: 100%;
    max-height: 340px;
    overflow: hidden;
  }
`

const Poster = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
`

const InfoCol = styled.div`
  flex: 1;
  padding: 28px 28px 28px 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;

  @media (max-width: 600px) {
    padding: 20px;
  }
`

const Title = styled.h2`
  margin: 0;
  font-size: clamp(18px, 2.5vw, 26px);
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text};
  line-height: 1.25;
`

const Meta = styled.div`
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
`

const MetaItem = styled.span`
  font-size: ${({ theme }) => theme.fontSizes.sm};
  color: ${({ theme }) => theme.colors.textSecondary};
`

const Star = styled.span`
  color: #f5c518;
`

const Pill = styled.span`
  display: inline-block;
  padding: 2px 8px;
  border-radius: ${({ theme }) => theme.radii.sm};
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
`

const TypePill = styled(Pill)`
  background: ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textSecondary};
`

const Genres = styled.p`
  margin: 0;
  font-size: ${({ theme }) => theme.fontSizes.sm};
  color: ${({ theme }) => theme.colors.textSecondary};
`

const Synopsis = styled.p`
  margin: 0;
  font-size: ${({ theme }) => theme.fontSizes.md};
  color: ${({ theme }) => theme.colors.text};
  line-height: 1.7;
`

const NoSynopsis = styled.p`
  margin: 0;
  font-size: ${({ theme }) => theme.fontSizes.sm};
  color: ${({ theme }) => theme.colors.textMuted};
  font-style: italic;
`

const ModalActions = styled.div`
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: ${({ theme }) => theme.spacing.md};
  padding-top: ${({ theme }) => theme.spacing.md};
`

const ModalCtrlArea = styled.div`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};
  flex: 1;
`

const ModalCtrlBtn = styled.button`
  background: none;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.sm};
  color: ${({ theme }) => theme.colors.text};
  cursor: pointer;
  font-size: ${({ theme }) => theme.fontSizes.sm};
  padding: 4px 12px;

  &:hover {
    background: ${({ theme }) => theme.colors.border};
  }
`

const ModalProgressText = styled.span`
  font-size: ${({ theme }) => theme.fontSizes.sm};
  color: #f5c518;
`

const ModalRingWrapper = styled.div`
  position: relative;
  flex-shrink: 0;
  width: 60px;
  height: 60px;
`

const ModalRingSvg = styled.svg`
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
  transform-origin: center;
  pointer-events: none;
  z-index: 2;
`

const ModalTrackCircle = styled.circle`
  fill: none;
  stroke: ${({ theme }) => theme.colors.border};
  stroke-width: 2.5;
`

const ModalProgressArc = styled.circle<{ $circ: number; $pct: number; $active: boolean; $done: boolean }>`
  fill: none;
  stroke: ${({ theme, $done }) => $done ? theme.colors.success : "#f5c518"};
  stroke-width: 2.5;
  stroke-linecap: round;
  stroke-dasharray: ${({ $circ }) => $circ};
  stroke-dashoffset: ${({ $circ, $pct, $active, $done }) =>
    $done ? 0 : ($active ? $circ * (1 - $pct / 100) : $circ)};
  opacity: ${({ $active, $done }) => ($active || $done ? 1 : 0)};
  transition: stroke-dashoffset 0.5s ease, stroke 0.3s ease, opacity 0.3s ease;
`

const ModalDownloadBtn = styled.button`
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: ${({ theme }) => theme.colors.text};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 14px;
  z-index: 1;

  svg {
    width: 84%;
    height: 84%;
    display: block;
  }
`

const ModalGreenCheckBtn = styled.button`
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: ${({ theme }) => theme.colors.success};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: default;
  padding: 14px;
  z-index: 1;

  svg {
    width: 84%;
    height: 84%;
    display: block;
  }
`

const WatchBtn = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  background: ${({ theme }) => theme.colors.primary};
  color: ${({ theme }) => theme.colors.text};
  border: none;
  border-radius: ${({ theme }) => theme.radii.sm};
  font-size: ${({ theme }) => theme.fontSizes.md};
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;

  &:hover:not(:disabled) {
    background: ${({ theme }) => theme.colors.primaryHover};
  }

  &:disabled {
    opacity: 0.55;
    cursor: default;
  }
`

const PlayerError = styled.span`
  font-size: ${({ theme }) => theme.fontSizes.sm};
  color: ${({ theme }) => theme.colors.error};
`
