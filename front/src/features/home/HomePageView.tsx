import React from "react"
import styled from "styled-components"
import type { ActiveTab, VideoResult } from "@/types/search.types"
import type { User } from "@/types/auth.types"
import SearchBar from "./components/SearchBar"
import TabBar from "./components/TabBar"
import VideoCard from "./components/VideoCard"
import UserMenu from "./components/UserMenu"
import MyListView from "./components/MyListView"

export interface HomePageViewProps {
  user: User | null
  query: string
  activeTab: ActiveTab
  heading: string
  results: VideoResult[]
  localMovies: VideoResult[]
  localTvShows: VideoResult[]
  loading: boolean
  error: string | null
  page: number
  totalPages: number
  onSearch: (q: string) => void
  onChangeTab: (tab: ActiveTab) => void
  onPageChange: (page: number) => void
  onLogout: () => void
}

const PageInfo = styled.span`
  font-size: 13px;
  color: #888;
  min-width: 48px;
  text-align: center;
`

const HomePageView: React.FC<HomePageViewProps> = ({
  user,
  query,
  activeTab,
  heading,
  results,
  localMovies,
  localTvShows,
  loading,
  error,
  page,
  totalPages,
  onSearch,
  onChangeTab,
  onPageChange,
  onLogout,
}) => (
  <Page>
    <Header>
      <Logo>HyperTube</Logo>
      {user && <UserMenu user={user} onLogout={onLogout} />}
    </Header>
    <HeroSection>
      <HeroTitle>Find your next watch</HeroTitle>
      <SearchBar value={query} onSearch={onSearch} />
    </HeroSection>
    <ContentSection>
      <TabsRow>
        <TabBar active={activeTab} onChange={onChangeTab} />
      </TabsRow>
      {activeTab !== "my_list" && heading && (
        <SectionTitle>{heading}</SectionTitle>
      )}
      {loading && (
        <StatusWrapper>
          <Spinner aria-label="Loading" />
        </StatusWrapper>
      )}
      {!loading && error && (
        <StatusWrapper>
          <ErrorMessage role="alert">⚠ {error}</ErrorMessage>
        </StatusWrapper>
      )}
      {activeTab === "my_list" ? (
        <MyListView movies={localMovies} tvShows={localTvShows} />
      ) : (
        <>
          {!loading && !error && results.length === 0 && (
            <StatusWrapper>
              <EmptyMessage>No results found.</EmptyMessage>
            </StatusWrapper>
          )}
          {!loading && results.length > 0 && (
            <Grid>
              {results.map((video, idx) => (
                <VideoCard key={video.id ?? `${video.title}-${idx}`} video={video} />
              ))}
            </Grid>
          )}
          {!loading && totalPages > 1 && (
            <Pagination>
              <PageBtn onClick={() => onPageChange(page - 1)} disabled={page <= 1}>‹ Prev</PageBtn>
              <PageInfo>{page} / {totalPages}</PageInfo>
              <PageBtn onClick={() => onPageChange(page + 1)} disabled={page >= totalPages}>Next ›</PageBtn>
            </Pagination>
          )}
        </>
      )}
    </ContentSection>
  </Page>
)

export default HomePageView

const Page = styled.div`
  min-height: 100vh;
  background-color: ${({ theme }) => theme.colors.background};
  color: ${({ theme }) => theme.colors.text};
  font-family: ${({ theme }) => theme.fonts.base};
`

const Header = styled.header`
  position: sticky;
  top: 0;
  z-index: 100;
  background: linear-gradient(
    to bottom,
    rgba(20, 20, 20, 0.98) 0%,
    rgba(20, 20, 20, 0.6) 80%,
    transparent 100%
  );
  padding: ${({ theme }) => `${theme.spacing.md} ${theme.spacing.xl}`};
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: ${({ theme }) => theme.spacing.lg};
`

const Logo = styled.span`
  font-size: 26px;
  font-weight: 900;
  color: ${({ theme }) => theme.colors.primary};
  letter-spacing: -0.5px;
  user-select: none;
`

const HeroSection = styled.section`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.lg};
  padding: ${({ theme }) => `${theme.spacing.xl} ${theme.spacing.xl} ${theme.spacing.lg}`};
`

const HeroTitle = styled.h1`
  font-size: clamp(22px, 4vw, 40px);
  font-weight: 700;
  text-align: center;
  margin: 0;
  color: ${({ theme }) => theme.colors.text};
`

const ContentSection = styled.section`
  padding: ${({ theme }) => `0 ${theme.spacing.xl} ${theme.spacing.xl}`};
`

const TabsRow = styled.div`
  display: flex;
  justify-content: center;
  margin-bottom: ${({ theme }) => theme.spacing.sm};
`

const SectionTitle = styled.h2`
  font-size: ${({ theme }) => theme.fontSizes.lg};
  font-weight: 700;
  margin: 0 0 ${({ theme }) => theme.spacing.lg};
`

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: ${({ theme }) => theme.spacing.md};

  @media (min-width: 600px) {
    grid-template-columns: repeat(auto-fill, minmax(155px, 1fr));
  }

  @media (min-width: 1024px) {
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  }
`

const StatusWrapper = styled.div`
  display: flex;
  justify-content: center;
  padding: ${({ theme }) => `${theme.spacing.xl} 0`};
`

const Spinner = styled.div`
  width: 42px;
  height: 42px;
  border: 4px solid ${({ theme }) => theme.colors.border};
  border-top-color: ${({ theme }) => theme.colors.primary};
  border-radius: 50%;
  animation: spin 0.7s linear infinite;

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
`

const ErrorMessage = styled.p`
  color: ${({ theme }) => theme.colors.error};
  font-size: ${({ theme }) => theme.fontSizes.md};
  text-align: center;
`

const EmptyMessage = styled.p`
  color: ${({ theme }) => theme.colors.textSecondary};
  font-size: ${({ theme }) => theme.fontSizes.md};
  text-align: center;
`

const Pagination = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};
  margin-top: ${({ theme }) => theme.spacing.xl};
`

const PageBtn = styled.button<{ $active?: boolean }>`
  background: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.text};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.sm};
  padding: ${({ theme }) => `${theme.spacing.xs} ${theme.spacing.md}`};
  font-size: ${({ theme }) => theme.fontSizes.sm};
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;

  &:disabled {
    opacity: 0.35;
    cursor: default;
  }

  &:not(:disabled):hover {
    background: ${({ theme }) => theme.colors.surfaceHover};
  }
`
