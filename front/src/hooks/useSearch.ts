import { useCallback, useMemo, useEffect, useRef } from "react"
import { useAppDispatch, useAppSelector } from "@/hooks/useAppStore"
import {
  fetchSearch,
  fetchLocalVideos,
  setQuery,
  setActiveTab,
  setPage,
  clearResults,
} from "@/store/slices/searchSlice"
import { fetchActiveDownloads } from "@/store/slices/downloadSlice"
import type { ActiveTab } from "@/types/search.types"

/**
 * Primary hook for the search domain.
 * Encapsulates dispatch and selectors — components never interact with Redux directly.
 */
const useSearch = () => {
  const dispatch = useAppDispatch()
  const { query, activeTab, movies, tv_shows, localVideos, pages, totalPages, totalResults, loading, error } =
    useAppSelector((state) => state.search)
  const { pageSize } = useAppSelector((state) => state.config)
  const downloadItems = useAppSelector((state) => state.downloads.items)
  const downloadEntries = useMemo(() => Object.values(downloadItems), [downloadItems])

  const completedCount = useMemo(
    () => downloadEntries.filter((e) => e.status === "completed").length,
    [downloadEntries]
  )
  const prevCompletedRef = useRef(completedCount)
  useEffect(() => {
    if (completedCount > prevCompletedRef.current) {
      dispatch(fetchLocalVideos())
    }
    prevCompletedRef.current = completedCount
  }, [completedCount, dispatch])

  const page = pages[activeTab]

  const localMovies = useMemo(
    () => localVideos.filter((v) => v.content_type === "movie" && v.downloaded),
    [localVideos]
  )
  const localTvShows = useMemo(
    () => localVideos.filter((v) => v.content_type === "tv_show" && v.downloaded),
    [localVideos]
  )

  const allResults =
    activeTab === "my_list"
      ? (() => {
          const sessionByHash = new Map(downloadEntries.map((e) => [e.hash, e]))
          return localVideos.map((v) => {
            const liveEntry = v.torrents?.find(
              (t) => t.hash && sessionByHash.has(t.hash!)
            )
            const entry = liveEntry ? sessionByHash.get(liveEntry.hash!) : undefined
            return entry
              ? { ...v, download_status: entry.status, download_progress: entry.progress, downloaded: entry.status === "completed" }
              : { ...v, downloaded: v.download_status === "completed" }
          })
        })()
      : activeTab === "movies"
        ? movies
        : tv_shows
  const resultCount =
    activeTab === "my_list"
      ? allResults.length
      : totalResults[activeTab]
  const pageCount =
    activeTab === "my_list"
      ? Math.max(1, Math.ceil(resultCount / pageSize))
      : totalPages[activeTab]

  // Clamp current page if it exceeds totalPages (e.g. after a deletion)
  useEffect(() => {
    if (page > pageCount) {
      dispatch(setPage({ tab: activeTab, page: pageCount }))
    }
  }, [pageCount, page, activeTab, dispatch])

  const results = activeTab === "my_list"
    ? allResults.slice((page - 1) * pageSize, page * pageSize)
    : allResults

  const search = useCallback(
    (q: string) => {
      dispatch(setQuery(q))
      dispatch(fetchSearch({ query: q, page: 1, limit: pageSize }))
    },
    [dispatch, pageSize]
  )

  const changeTab = useCallback(
    (tab: ActiveTab) => dispatch(setActiveTab(tab)),
    [dispatch]
  )

  const changePage = useCallback(
    (p: number) => {
      dispatch(setPage({ tab: activeTab, page: p }))
      if (activeTab !== "my_list") {
        dispatch(fetchSearch({ query, page: p, limit: pageSize }))
      }
    },
    [dispatch, activeTab, query, pageSize]
  )

  const loadLocalVideos = useCallback(
    () => { dispatch(fetchLocalVideos()) },
    [dispatch]
  )

  const loadActiveDownloads = useCallback(
    () => { dispatch(fetchActiveDownloads()) },
    [dispatch]
  )

  const reset = useCallback(() => dispatch(clearResults()), [dispatch])

  return {
    query,
    activeTab,
    page,
    results,
    totalResults: resultCount,
    totalPages: pageCount,
    localMovies,
    localTvShows,
    loading,
    error,
    search,
    changeTab,
    changePage,
    loadLocalVideos,
    loadActiveDownloads,
    reset,
  }
}

export default useSearch
