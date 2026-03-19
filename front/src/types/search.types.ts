// Search & discovery types — all data shapes for external provider results and Redux state.

export interface Torrent {
  quality?: string
  type?: string
  size?: string
  url?: string
  hash?: string
  seeds?: number
  peers?: number
}

export interface VideoResult {
  /** DB id — present only if the content has already been downloaded */
  id?: number
  title: string
  year?: number
  rating?: number
  download_count?: number
  genres?: string[]
  synopsis?: string
  /** Low-resolution thumbnail */
  thumbnail?: string
  /** Full-size poster */
  large_cover?: string
  language?: string
  content_type: "movie" | "tv_show"
  torrents: Torrent[]
  provider?: string
  /** Selected torrent hash persisted in DB (if download started) */
  selected_torrent_hash?: string
  // DB enrichment fields
  downloaded?: boolean
  download_status?: string
  download_progress?: number
  file_path?: string
}

export interface PaginatedResults {
  results: VideoResult[]
  total_results: number
  total_pages: number
}

/** Raw backend response from GET /api/search/ */
export interface SearchResponse {
  movies: PaginatedResults
  tv_shows: PaginatedResults
  page: number
  limit: number
  query: string
}

/** Active tab on the Home page */
export type ActiveTab = "movies" | "tv_shows" | "my_list"

/** Redux state for the search domain */
export interface SearchState {
  query: string
  activeTab: ActiveTab
  movies: VideoResult[]
  tv_shows: VideoResult[]
  localVideos: VideoResult[]
  pages: { movies: number; tv_shows: number; my_list: number }
  loading: boolean
  error: string | null
}
