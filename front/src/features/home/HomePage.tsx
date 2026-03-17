// HomePage — container: wires useSearch + useAuth and delegates rendering to HomePageView.
import React, { useEffect } from "react"
import useSearch from "@/hooks/useSearch"
import useAuth from "@/hooks/useAuth"
import HomePageView from "./HomePageView"

const HomePage: React.FC = () => {
  const { user, logout } = useAuth()
  const { query, activeTab, results, totalResults, totalPages, page, localMovies, localTvShows, loading, error, search, changeTab, changePage, loadLocalVideos } =
    useSearch()

  useEffect(() => {
    loadLocalVideos()
    search("")
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const heading = query.trim()
    ? `Results for "${query}"`
    : activeTab === "my_list"
      ? ""
      : activeTab === "movies"
        ? `Top${totalResults !== null ? ` ${totalResults.toLocaleString()}` : ""} Movies`
        : `Top${totalResults !== null ? ` ${totalResults.toLocaleString()}` : ""} TV Shows`

  return (
    <HomePageView
      user={user}
      query={query}
      activeTab={activeTab}
      heading={heading}
      results={results}
      localMovies={localMovies}
      localTvShows={localTvShows}
      loading={loading}
      error={error}
      page={page}
      totalPages={totalPages}
      onSearch={(q) => search(q)}
      onChangeTab={changeTab}
      onPageChange={(p) => { changePage(p); window.scrollTo({ top: 0, behavior: "instant" }) }}
      onLogout={logout}
    />
  )
}

export default HomePage
