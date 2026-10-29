// Search slice — Redux state for the search domain (query, results, pagination, local videos).
import { createSlice, createAsyncThunk, type PayloadAction } from "@reduxjs/toolkit"
import searchService from "@/services/search.service"
import videoService from "@/services/video.service"
import type { SearchState, ActiveTab } from "@/types/search.types"
import { deleteVideo } from "./downloadSlice"

interface FetchSearchArgs {
  query: string
  page: number
  limit: number
}

export const fetchLocalVideos = createAsyncThunk(
  "search/fetchLocal",
  async (_, { rejectWithValue }) => {
    try {
      const { videos } = await videoService.getAll()
      return videos
    } catch (err) {
      return rejectWithValue((err as Error).message)
    }
  }
)

export const fetchSearch = createAsyncThunk(
  "search/fetch",
  async ({ query, page, limit }: FetchSearchArgs, { rejectWithValue }) => {
    try {
      return await searchService.search(query, page, limit)
    } catch (err) {
      return rejectWithValue((err as Error).message)
    }
  },
  {
    // Skip if a search is already in progress (prevents StrictMode double-dispatch)
    condition: (_, { getState }) => {
      const state = getState() as { search: SearchState }
      return !state.search.loading
    },
  }
)

const initialState: SearchState = {
  query: "",
  activeTab: "movies",
  movies: [],
  tv_shows: [],
  localVideos: [],
  pages: { movies: 1, tv_shows: 1, my_list: 1 },
  totalPages: { movies: 1, tv_shows: 1, my_list: 1 },
  totalResults: { movies: 0, tv_shows: 0, my_list: 0 },
  loading: false,
  error: null,
}

const searchSlice = createSlice({
  name: "search",
  initialState,
  reducers: {
    setQuery(state, action: PayloadAction<string>) {
      state.query = action.payload
      state.pages = { movies: 1, tv_shows: 1, my_list: 1 }
    },
    setActiveTab(state, action: PayloadAction<ActiveTab>) {
      state.activeTab = action.payload
    },
    setPage(state, action: PayloadAction<{ tab: ActiveTab; page: number }>) {
      state.pages[action.payload.tab] = action.payload.page
    },
    clearResults(state) {
      state.movies = []
      state.tv_shows = []
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchLocalVideos.fulfilled, (state, action) => {
        state.localVideos = action.payload
      })
      .addCase(fetchSearch.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchSearch.fulfilled, (state, action) => {
        state.loading = false
        state.movies = action.payload.movies.results
        state.tv_shows = action.payload.tv_shows.results
        state.pages = {
          ...state.pages,
          movies: action.payload.page,
          tv_shows: action.payload.page,
        }
        state.totalPages = {
          ...state.totalPages,
          movies: action.payload.movies.total_pages,
          tv_shows: action.payload.tv_shows.total_pages,
        }
        state.totalResults = {
          ...state.totalResults,
          movies: action.payload.movies.total_results,
          tv_shows: action.payload.tv_shows.total_results,
        }
      })
      .addCase(fetchSearch.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      .addCase(deleteVideo.fulfilled, (state, action) => {
        const { videoId, contentType } = action.meta.arg
        const list = contentType === "movie" ? state.movies : state.tv_shows
        const video = list.find(v => v.id === videoId)
        if (video) {
          video.downloaded = false
          video.download_status = undefined
          video.download_progress = 0
        }
        state.localVideos = state.localVideos.filter(v => v.id !== videoId)
      })
  },
})

export const { setQuery, setActiveTab, setPage, clearResults } = searchSlice.actions
export default searchSlice.reducer
