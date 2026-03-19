import React, { useEffect, useState } from "react"
import styled from "styled-components"
import { useAppDispatch, useAppSelector } from "@/hooks/useAppStore"
import {
  pauseDownload,
  resumeDownload,
  deleteVideo,
} from "@/store/slices/downloadSlice"
import { restoreDownload } from "@/store/slices/downloadSlice"
import videoService from "@/services/video.service"
import VideoModal from "./VideoModal"
import type { DownloadEntry } from "@/store/slices/downloadSlice"


const DownloadsTable: React.FC = () => {
  const dispatch = useAppDispatch()
  const entries = useAppSelector((state) =>
    Object.values(state.downloads.items).filter(
      (e) => e.status !== "completed" && e.status !== "error"
    )
  )
  const [modalVideo, setModalVideo] = useState<DownloadEntry["video"] | null>(null)

  useEffect(() => {
    let mounted = true
    videoService
      .getActiveDownloads()
      .then(({ videos }) => {
        if (!mounted) return
        videos.forEach((v) => {
          const hash = v.torrents?.[0]?.hash
          if (!hash) return
          dispatch(restoreDownload({ hash, contentType: v.content_type, video: v }))
        })
      })
      .catch(() => {
        /* best-effort restore, ignore errors */
      })
    return () => { mounted = false }
  }, [dispatch])

  const handlePause = (e: DownloadEntry) => {
    if (!e.videoId) return
    dispatch(pauseDownload({ contentType: e.contentType, videoId: e.videoId, hash: e.hash }))
  }

  const handleResume = (e: DownloadEntry) => {
    if (!e.videoId) return
    dispatch(resumeDownload({ contentType: e.contentType, videoId: e.videoId, hash: e.hash }))
  }

  const handleStop = (e: DownloadEntry) => {
    if (!e.videoId) return
    dispatch(deleteVideo({ contentType: e.contentType, videoId: e.videoId, hash: e.hash }))
  }

  const handleTitleClick = (video: DownloadEntry["video"]) => setModalVideo(video)

  return (
    <>
      <DownloadsTableView
        entries={entries}
        onPause={handlePause}
        onResume={handleResume}
        onStop={handleStop}
        onTitleClick={handleTitleClick}
      />
      {modalVideo && <VideoModal video={modalVideo} onClose={() => setModalVideo(null)} />}
    </>
  )
}

export default DownloadsTable


interface DownloadsTableViewProps {
  entries: DownloadEntry[]
  onPause: (e: DownloadEntry) => void
  onResume: (e: DownloadEntry) => void
  onStop: (e: DownloadEntry) => void
  onTitleClick: (video: DownloadEntry["video"]) => void
}

const STATUS_LABELS: Record<string, string> = {
  queued: "Queued",
  downloading: "Downloading",
  paused: "Paused",
}

export const DownloadsTableView: React.FC<DownloadsTableViewProps> = ({
  entries,
  onPause,
  onResume,
  onStop,
  onTitleClick,
}) => {
  if (entries.length === 0) {
    return (
      <Panel>
        <PanelTitle>Downloads</PanelTitle>
        <Empty>No active downloads.</Empty>
      </Panel>
    )
  }

  return (
    <Panel>
      <PanelTitle>Downloads <Count>{entries.length}</Count></PanelTitle>
      <Table>
        <thead>
          <tr>
            <Th $w="35%">Title</Th>
            <Th $center $w="25%">Status</Th>
            <Th $center $w="22%">Progress</Th>
            <Th $center $w="18%">Actions</Th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <Row key={entry.hash}>
              <Td>
                <TitleButton onClick={() => onTitleClick(entry.video)} title={`Open ${entry.video.title}`}>
                  {entry.video.title}
                </TitleButton>
              </Td>
              <Td $center>
                <StatusBadge $status={entry.status}>
                  {STATUS_LABELS[entry.status] ?? entry.status}
                </StatusBadge>
              </Td>
              <Td $center>
                <ProgressLabel>{Math.round(entry.progress)}%</ProgressLabel>
              </Td>
              <Td $center>
                <Actions>
                  {entry.status === "downloading" ? (
                    <ActionBtn onClick={() => onPause(entry)} title="Pause" aria-label="Pause">
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <rect x="5" y="4" width="4" height="16" rx="1" />
                        <rect x="15" y="4" width="4" height="16" rx="1" />
                      </svg>
                    </ActionBtn>
                  ) : (
                    <ActionBtn onClick={() => onResume(entry)} title="Resume" aria-label="Resume">
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <polygon points="6,4 20,12 6,20" />
                      </svg>
                    </ActionBtn>
                  )}
                  <ActionBtn
                    $danger
                    onClick={() => onStop(entry)}
                    title="Cancel"
                    aria-label="Cancel download"
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <rect x="5" y="5" width="14" height="14" rx="1" />
                    </svg>
                  </ActionBtn>
                </Actions>
              </Td>
            </Row>
          ))}
        </tbody>
      </Table>
    </Panel>
  )
}

export const Panel = styled.aside`
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 10px;
  padding: ${({ theme }) => theme.spacing.lg};
  background: ${({ theme }) => theme.colors.surface};
  min-height: 120px;
  overflow: hidden;
`

const PanelTitle = styled.h3`
  margin: 0 0 ${({ theme }) => theme.spacing.md};
  font-size: ${({ theme }) => theme.fontSizes.md};
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text};
  display: flex;
  align-items: baseline;
  justify-content: space-between;
`

const Count = styled.span`
  font-size: ${({ theme }) => theme.fontSizes.sm};
  color: ${({ theme }) => theme.colors.textMuted};
  margin-left: auto;
`

const Empty = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: ${({ theme }) => theme.fontSizes.sm};
  text-align: center;
  margin: ${({ theme }) => theme.spacing.lg} 0 0;
`

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
`

const Th = styled.th<{ $center?: boolean; $w?: string }>`
  text-align: ${({ $center }) => ($center ? "center" : "left")};
  padding: ${({ theme }) => `${theme.spacing.xs} ${theme.spacing.sm}`};
  font-size: ${({ theme }) => theme.fontSizes.sm};
  color: ${({ theme }) => theme.colors.textSecondary};
  font-weight: 600;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  ${({ $w }) => $w ? `width: ${$w};` : ""}
  overflow: hidden;
`

const Row = styled.tr`
  &:not(:last-child) td {
    border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  }
`

const Td = styled.td<{ $center?: boolean }>`
  text-align: ${({ $center }) => ($center ? "center" : "left")};
  padding: ${({ theme }) => `${theme.spacing.sm} ${theme.spacing.sm}`};
  vertical-align: middle;
`

const TitleButton = styled.button`
  display: block;
  font-size: ${({ theme }) => theme.fontSizes.sm};
  color: rgb(255, 255, 255);
  background: transparent;
  border: none;
  padding: 0;
  margin: 0;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  cursor: pointer;
  text-decoration: underline;
  &:hover { color: rgb(245, 24, 24); }
`

const StatusBadge = styled.span<{ $status: string }>`
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  background: ${({ $status }) =>
    $status === "downloading"
      ? "rgba(245,197,24,0.15)"
      : $status === "paused"
        ? "rgba(179,179,179,0.15)"
        : "rgba(255,255,255,0.08)"};
  color: ${({ theme, $status }) =>
    $status === "downloading"
      ? "#f5c518"
      : $status === "paused"
        ? theme.colors.textSecondary
        : theme.colors.textMuted};
`

const ProgressLabel = styled.span`
  font-size: 10px;
  color: #f5c518;
`

const Actions = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${({ theme }) => theme.spacing.xs};
`

const ActionBtn = styled.button<{ $danger?: boolean }>`
  width: 26px;
  height: 26px;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: ${({ theme, $danger }) => ($danger ? theme.colors.error : theme.colors.text)};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 5px;
  transition: background 0.15s;

  svg {
    width: 100%;
    height: 100%;
    display: block;
  }

  &:hover {
    background: ${({ theme }) => theme.colors.surfaceHover};
  }
`
