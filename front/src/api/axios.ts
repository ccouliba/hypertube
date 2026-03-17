// Axios client — shared instance with JWT injection and transparent token-refresh retry logic.
import axios from "axios"
import type { AxiosRequestConfig } from "axios"
import { getToken, setToken } from "@/api/tokenStore"

const BASE_URL = import.meta.env.VITE_API_URL ?? ""

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30_000,
})

/**
 * Dedicated refresh client — separate instance to prevent infinite retry loops
 * if the refresh call itself returns 401.
 */
const _refreshClient = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
})

apiClient.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handles edge cases: dormant tab, clock skew, network hiccup, etc.
let _isRefreshing = false
let _pendingQueue: Array<(token: string | null) => void> = []

const flushQueue = (token: string | null) => {
  _pendingQueue.forEach((cb) => cb(token))
  _pendingQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original: AxiosRequestConfig & { _retry?: boolean } = error.config ?? {}
    const is401 = error.response?.status === 401
    const isRefreshCall = original.url?.includes("/api/auth/refresh")

    if (is401 && !original._retry && !isRefreshCall) {
      if (_isRefreshing) {
        // Queue the request and replay it once the refresh completes
        return new Promise((resolve, reject) => {
          _pendingQueue.push((newToken) => {
            if (!newToken) return reject(error)
            original.headers = { ...original.headers, Authorization: `Bearer ${newToken}` }
            resolve(apiClient(original))
          })
        })
      }

      original._retry = true
      _isRefreshing = true

      try {
        const { data } = await _refreshClient.post<{ access_token: string }>(
          "/api/auth/refresh"
        )
        setToken(data.access_token)
        flushQueue(data.access_token)
        original.headers = { ...original.headers, Authorization: `Bearer ${data.access_token}` }
        return apiClient(original)
      } catch {
        setToken(null)
        flushQueue(null)
        window.location.href = "/login"
        return Promise.reject(error)
      } finally {
        _isRefreshing = false
      }
    }

    const message = error.response?.data?.message ?? error.message ?? "Unknown error"
    return Promise.reject(new Error(message))
  }
)

export default apiClient
