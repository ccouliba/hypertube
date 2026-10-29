import { useEffect } from "react"
import useAuth from "@/hooks/useAuth"
import useSearch from "@/hooks/useSearch"
import { useDownloadsPolling } from "./useDownloadsPolling"

export const useHomeController = () => {
  useDownloadsPolling()
  const { user, logout } = useAuth()
  const {
    query,
    activeTab,
    results,
    totalResults,
    totalPages,
    page,
    localMovies,
    localTvShows,
    loading,
    error,
    search,
    changeTab,
    changePage,
    loadLocalVideos,
    loadActiveDownloads,
  } = useSearch()

  useEffect(() => {
    loadLocalVideos()
    loadActiveDownloads()
    search("")
    // Bootstrap should run once when the home page mounts.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const heading = query.trim()
    ? `Results for "${query}"`
    : activeTab === "my_list"
      ? ""
      : activeTab === "movies"
        ? `Top${totalResults !== null ? ` ${totalResults.toLocaleString()}` : ""} Movies`
        : `Top${totalResults !== null ? ` ${totalResults.toLocaleString()}` : ""} TV Shows`

  return {
    user,
    logout,
    query,
    activeTab,
    heading,
    results,
    totalResults,
    totalPages,
    page,
    localMovies,
    localTvShows,
    loading,
    error,
    search,
    changeTab,
    changePage,
  }
}
