// VideoCard — thumbnail card with inline download ring and click-to-open modal.
import React, { useState } from "react"
import { createPortal } from "react-dom"
import styled from "styled-components"
import type { VideoResult } from "@/types/search.types"
import VideoModal from "./VideoModal"
import { useDownload } from "@/hooks/useDownload"

const PLACEHOLDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='250' height='370'%3E%3Crect width='250' height='370' fill='%231f1f1f'/%3E%3Ctext x='125' y='185' font-family='sans-serif' font-size='14' fill='%23666' text-anchor='middle' dominant-baseline='middle'%3ENo Poster%3C/text%3E%3C/svg%3E"
const SMALL_RADIUS = 13
const SMALL_CIRC = +(2 * Math.PI * SMALL_RADIUS).toFixed(2)


interface VideoCardProps {
  video: VideoResult
}


const VideoCard: React.FC<VideoCardProps> = ({ video }) => {
  const [open, setOpen] = useState(false)
  const { entry, hasTorrent, startDownload, pauseDownload, resumeDownload, deleteVideo, stopDownload, canDelete } = useDownload(video)

  const poster = video.thumbnail ?? PLACEHOLDER
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

  return (
    <>
      <VideoCardView
        video={video}
        poster={poster}
        rating={rating}
        isDone={isDone}
        isDownloading={isDownloading}
        isActive={isActive}
        progress={progress}
        hasTorrent={hasTorrent}
        canDelete={canDelete}
        onOpen={() => setOpen(true)}
        onDownload={handleDownloadClick}
        onPause={(e) => { e.stopPropagation(); pauseDownload() }}
        onResume={(e) => { e.stopPropagation(); resumeDownload() }}
        onStopOrDelete={(e) => { e.stopPropagation(); isActive ? stopDownload() : deleteVideo() }}
      />
      {open && createPortal(
        <VideoModal video={video} onClose={() => setOpen(false)} />,
        document.body
      )}
    </>
  )
}

export default VideoCard


interface VideoCardViewProps {
  video: VideoResult
  poster: string
  rating: string | null
  isDone: boolean
  isDownloading: boolean
  isActive: boolean
  progress: number
  hasTorrent: boolean
  canDelete: boolean
  onOpen: () => void
  onDownload: (e: React.MouseEvent) => void
  onPause: (e: React.MouseEvent) => void
  onResume: (e: React.MouseEvent) => void
  onStopOrDelete: (e: React.MouseEvent) => void
}

export const VideoCardView: React.FC<VideoCardViewProps> = ({
  video,
  poster,
  rating,
  isDone,
  isDownloading,
  isActive,
  progress,
  hasTorrent,
  canDelete,
  onOpen,
  onDownload,
  onPause,
  onResume,
  onStopOrDelete,
}) => (
  <Card onClick={onOpen}>
    <PosterWrapper>
      <Poster src={poster} alt={video.title} loading="lazy" />
      <Overlay>
        <OverlayContent>
          <OverlayTitle>{video.title}</OverlayTitle>
          <OverlayMeta>
            {video.year && <span>{video.year}</span>}
            {rating && <Rating>★ {rating}</Rating>}
          </OverlayMeta>
          {video.genres && video.genres.length > 0 && (
            <Genres>{video.genres.slice(0, 3).join(" · ")}</Genres>
          )}
        </OverlayContent>
      </Overlay>
    </PosterWrapper>
    <CardFooter>
      <FooterRow>
        <TitleBlock>
          <Title title={video.title}>{video.title}</Title>
          {isActive && <ProgressText>{Math.round(progress)}%</ProgressText>}
        </TitleBlock>
        {(hasTorrent || isDone) && (
          <FooterActions>
            {canDelete && (
              <DeleteWrapper $alwaysVisible={isActive}>
                <RingSvg viewBox="0 0 30 30">
                  <TrackCircle cx="15" cy="15" r={SMALL_RADIUS} />
                </RingSvg>
                <IconBtn
                  onClick={onStopOrDelete}
                  aria-label={isActive ? "Cancel" : "Remove"}
                  title={isActive ? "Cancel download" : "Remove from board"}
                >
                  {isActive ? (
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <rect x="5" y="5" width="14" height="14" rx="1" />
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                      <line x1="4" y1="12" x2="20" y2="12" />
                    </svg>
                  )}
                </IconBtn>
              </DeleteWrapper>
            )}
            {/* Single ring: + → yellow arc → green ✓ */}
            <RingWrapper>
              <RingSvg viewBox="0 0 30 30">
                <TrackCircle cx="15" cy="15" r={SMALL_RADIUS} />
                <ProgressArc
                  cx="15" cy="15" r={SMALL_RADIUS}
                  $circ={SMALL_CIRC} $pct={progress} $active={isActive} $done={isDone}
                />
              </RingSvg>
              {isDone ? (
                <GreenCheckBtn aria-label="Downloaded" title="Downloaded">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </GreenCheckBtn>
              ) : !isActive ? (
                <IconBtn onClick={onDownload} aria-label="Download" title="Download">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                    <line x1="12" y1="4" x2="12" y2="20" />
                    <line x1="4" y1="12" x2="20" y2="12" />
                  </svg>
                </IconBtn>
              ) : isDownloading ? (
                <IconBtn onClick={onPause} aria-label="Pause" title="Pause">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <rect x="5" y="4" width="4" height="16" rx="1" />
                    <rect x="15" y="4" width="4" height="16" rx="1" />
                  </svg>
                </IconBtn>
              ) : (
                <IconBtn onClick={onResume} aria-label="Resume" title="Resume">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="6,4 20,12 6,20" />
                  </svg>
                </IconBtn>
              )}
            </RingWrapper>
          </FooterActions>
        )}
      </FooterRow>
    </CardFooter>
  </Card>
)


const Card = styled.article`
  background-color: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.radii.md};
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: scale(1.04);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.7);
    z-index: 1;
  }
`

const PosterWrapper = styled.div`
  position: relative;
  aspect-ratio: 2 / 3;
  overflow: hidden;
`

const Poster = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
`

const Overlay = styled.div`
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.95) 30%, rgba(0, 0, 0, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.25s ease;
  display: flex;
  align-items: flex-end;
  padding: ${({ theme }) => theme.spacing.md};

  ${Card}:hover & {
    opacity: 1;
  }
`

const OverlayContent = styled.div`
  width: 100%;
`

const OverlayTitle = styled.h3`
  margin: 0 0 ${({ theme }) => theme.spacing.xs};
  font-size: ${({ theme }) => theme.fontSizes.md};
  color: ${({ theme }) => theme.colors.text};
  font-weight: 600;
  line-height: 1.3;
`

const OverlayMeta = styled.div`
  display: flex;
  gap: ${({ theme }) => theme.spacing.sm};
  align-items: center;
  font-size: ${({ theme }) => theme.fontSizes.sm};
  color: ${({ theme }) => theme.colors.textSecondary};
  margin-bottom: ${({ theme }) => theme.spacing.xs};
`

const Rating = styled.span`
  color: #f5c518;
  font-weight: 600;
`

const Genres = styled.p`
  margin: 0 0 ${({ theme }) => theme.spacing.xs};
  font-size: ${({ theme }) => theme.fontSizes.sm};
  color: ${({ theme }) => theme.colors.textSecondary};
`

// const Synopsis = styled.p`
//   margin: 0;
//   font-size: 11px;
//   color: ${({ theme }) => theme.colors.textMuted};
//   display: -webkit-box;
//   -webkit-line-clamp: 3;
//   -webkit-box-orient: vertical;
//   overflow: hidden;
// `

const CardFooter = styled.div`
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
`

const FooterRow = styled.div`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};
`

const TitleBlock = styled.div`
  flex: 1;
  min-width: 0;
`

const Title = styled.p`
  margin: 0;
  font-size: ${({ theme }) => theme.fontSizes.sm};
  color: ${({ theme }) => theme.colors.text};
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
`

const ProgressText = styled.span`
  display: block;
  font-size: 10px;
  color: #f5c518;
  margin-top: 2px;
`

const FooterActions = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
`

/* Delete button — invisible by default, always visible when $alwaysVisible */
const DeleteWrapper = styled.div<{ $alwaysVisible?: boolean }>`
  position: relative;
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  opacity: ${({ $alwaysVisible }) => ($alwaysVisible ? 1 : 0)};
  transition: opacity 0.2s ease;

  ${Card}:hover & {
    opacity: 1;
  }
`

const GreenCheckBtn = styled.button`
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
  padding: 7px;
  z-index: 1;

  svg {
    width: 100%;
    height: 100%;
    display: block;
  }
`

const RingWrapper = styled.div`
  position: relative;
  flex-shrink: 0;
  width: 30px;
  height: 30px;
`

const RingSvg = styled.svg`
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
  transform-origin: center;
  pointer-events: none;
  z-index: 2;
`

const TrackCircle = styled.circle`
  fill: none;
  stroke: ${({ theme }) => theme.colors.border};
  stroke-width: 2;
`

const ProgressArc = styled.circle<{ $circ: number; $pct: number; $active: boolean; $done: boolean }>`
  fill: none;
  stroke: ${({ theme, $done }) => $done ? theme.colors.success : "#f5c518"};
  stroke-width: 2;
  stroke-linecap: round;
  stroke-dasharray: ${({ $circ }) => $circ};
  stroke-dashoffset: ${({ $circ, $pct, $active, $done }) =>
    $done ? 0 : ($active ? $circ * (1 - $pct / 100) : $circ)};
  opacity: ${({ $active, $done }) => ($active || $done ? 1 : 0)};
  transition: stroke-dashoffset 0.5s ease, stroke 0.3s ease, opacity 0.3s ease;
`

const IconBtn = styled.button`
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
  padding: 7px;
  z-index: 1;

  svg {
    width: 100%;
    height: 100%;
    display: block;
  }
`

// const TypeBadge = styled(Badge)`
//   background-color: ${({ theme }) => theme.colors.inputBg};
//   color: ${({ theme }) => theme.colors.textSecondary};
// `
