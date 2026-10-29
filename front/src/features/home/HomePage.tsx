// HomePage — container: wires useSearch + useAuth and delegates rendering to HomePageView.
import React from "react"
import HomePageView from "./HomePageView"
import { useHomeController } from "./hooks/useHomeController"

const HomePage: React.FC = () => {
  const {
    user,
    logout,
    query,
    activeTab,
    heading,
    results,
    totalPages,
    page,
    localMovies,
    localTvShows,
    loading,
    error,
    search,
    changeTab,
    changePage,
  } = useHomeController()

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
