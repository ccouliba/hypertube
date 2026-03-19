import React from "react"
import styled from "styled-components"
import type { VideoResult } from "@/types/search.types"
import DownloadsTable from "./DownloadsTable"
import VideoCarousel from "./VideoCarousel"

interface MyListViewProps {
  movies: VideoResult[]
  tvShows: VideoResult[]
}

const MyListView: React.FC<MyListViewProps> = ({ movies, tvShows }) => (
  <MyListViewLayout movies={movies} tvShows={tvShows} />
)

export default MyListView


export const MyListViewLayout: React.FC<MyListViewProps> = ({ movies, tvShows }) => (
  <Layout>
    <LeftPanel>
      <DownloadsTable />
    </LeftPanel>
    <RightPanel>
      <ContentSection>
        <SectionHeader>
          <SectionTitle>Movies</SectionTitle>
          <Count>{movies.length}</Count>
        </SectionHeader>
        {movies.length === 0 ? (
          <EmptySection>No movies downloaded yet.</EmptySection>
        ) : (
          <VideoCarousel videos={movies} />
        )}
      </ContentSection>
      <Divider />
      <ContentSection>
        <SectionHeader>
          <SectionTitle>TV Shows</SectionTitle>
          <Count>{tvShows.length}</Count>
        </SectionHeader>
        {tvShows.length === 0 ? (
          <EmptySection>No TV shows downloaded yet.</EmptySection>
        ) : (
          <VideoCarousel videos={tvShows} />
        )}
      </ContentSection>
    </RightPanel>
  </Layout>
)


const Layout = styled.div`
  display: flex;
  gap: ${({ theme }) => theme.spacing.xl};
  align-items: flex-start;

  @media (max-width: 900px) {
    flex-direction: column;
  }
`

const LeftPanel = styled.div`
  flex: 1;
  min-width: 0;

  @media (max-width: 900px) {
    flex: unset;
    width: 100%;
  }
`

const RightPanel = styled.div`
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.xl};
`

const ContentSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.md};
`

const SectionHeader = styled.div`
  display: flex;
  align-items: baseline;
  justify-content: space-between;
`

const SectionTitle = styled.h3`
  margin: 0;
  font-size: ${({ theme }) => theme.fontSizes.md};
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text};
`

const Count = styled.span`
  font-size: ${({ theme }) => theme.fontSizes.sm};
  color: ${({ theme }) => theme.colors.textMuted};
`

const EmptySection = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: ${({ theme }) => theme.fontSizes.sm};
  margin: 0;
`

const Divider = styled.hr`
  border: none;
  border-top: 1px solid ${({ theme }) => theme.colors.border};
  margin: 0;
`
