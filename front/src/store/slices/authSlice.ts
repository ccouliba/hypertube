// Auth slice — Redux state for authentication (login, register, silent refresh, logout).
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit"
import authService from "@/services/auth.service"
import { setToken } from "@/api/tokenStore"
import type {
  AuthState,
  LoginPayload,
  RegisterPayload,
} from "@/types/auth.types"

export const login = createAsyncThunk(
  "auth/login",
  async (payload: LoginPayload, { rejectWithValue }) => {
    try {
      return await authService.login(payload)
    } catch (err) {
      return rejectWithValue((err as Error).message)
    }
  }
)

export const register = createAsyncThunk(
  "auth/register",
  async (payload: RegisterPayload, { rejectWithValue }) => {
    try {
      return await authService.register(payload)
    } catch (err) {
      return rejectWithValue((err as Error).message)
    }
  }
)

/**
 * Silent refresh — called on app mount.
 * Sends the httpOnly cookie to /api/auth/refresh and hydrates the store
 * with a fresh access token. If it fails (no cookie / expired), the user
 * remains unauthenticated and is redirected to /login by ProtectedRoute.
 */
export const bootstrapAuth = createAsyncThunk(
  "auth/bootstrap",
  async (_, { rejectWithValue }) => {
    try {
      return await authService.refresh()
    } catch {
      return rejectWithValue(null) // silent failure — not an error state
    }
  }
)

/**
 * Logout — revokes the refresh token server-side, then clears local state.
 */
export const logoutAsync = createAsyncThunk("auth/logoutAsync", async () => {
  try {
    await authService.logout()
  } catch {
    // Best thing to do : clear local state even if the server call fails
  }
})


const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  bootstrapping: true,   // true by default: waiting for the initial /refresh response on mount
  loading: false,
  error: null,
}

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout(state) {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      state.error = null
      setToken(null)
    },
    clearError(state) {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload.user
        state.token = action.payload.access_token
        state.isAuthenticated = true
        setToken(action.payload.access_token)  // sync tokenStore so Axios picks up the new token
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    builder
      .addCase(register.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Silent refresh (app bootstrap)
    builder
      .addCase(bootstrapAuth.pending, (state) => {
        state.bootstrapping = true
      })
      .addCase(bootstrapAuth.fulfilled, (state, action) => {
        state.bootstrapping = false
        state.token = action.payload.access_token
        state.isAuthenticated = true
        if (action.payload.user) state.user = action.payload.user
        setToken(action.payload.access_token)
      })
      .addCase(bootstrapAuth.rejected, (state) => {
        // No cookie or expired — stay unauthenticated, no error shown
        state.bootstrapping = false
        state.isAuthenticated = false
        setToken(null)
      })

    builder.addCase(logoutAsync.fulfilled, (state) => {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      setToken(null)
    })
  },
})

export const { logout, clearError } = authSlice.actions
export default authSlice.reducer
