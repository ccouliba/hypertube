// Config slice — fetches and stores public API config (pagination limits) at app boot.
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit"
import apiClient from "@/api/axios"

const DEFAULT_MAX_RESULTS : number = 84
const DEFAULT_PAGE_SIZE : number = 20

interface ConfigState {
  maxTotalResults: number
  pageSize: number
  ready: boolean
}

const initialState: ConfigState = {
  maxTotalResults: DEFAULT_MAX_RESULTS,
  pageSize: DEFAULT_PAGE_SIZE,
  ready: false,
}

export const fetchConfig = createAsyncThunk("config/fetch", async () => {
  const { data } = await apiClient.get<{ pagination: { max_total_results: number; page_size: number } }>(
    "/api/info/"
  )
  return data.pagination
})

const configSlice = createSlice({
  name: "config",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(fetchConfig.fulfilled, (state, action) => {
      state.maxTotalResults = action.payload.max_total_results
      state.pageSize = action.payload.page_size
      state.ready = true
    })
    builder.addCase(fetchConfig.rejected, (state) => {
      // Fallback to defaults if the endpoint fails
      state.ready = true
    })
  },
})

export default configSlice.reducer
