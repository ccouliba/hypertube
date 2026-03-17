// Redux store — root configuration and typed hooks.
import { configureStore } from "@reduxjs/toolkit"
import authReducer from "@/store/slices/authSlice"
import searchReducer from "@/store/slices/searchSlice"
import configReducer from "@/store/slices/configSlice"
import downloadsReducer from "@/store/slices/downloadSlice"

export const store = configureStore({
  reducer: {
    auth: authReducer,
    search: searchReducer,
    config: configReducer,
    downloads: downloadsReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
