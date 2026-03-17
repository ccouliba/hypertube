/**
 * Token store — keeps the JWT in memory (outside Redux, outside localStorage).
 *
 * Strategy: PROACTIVE refresh.
 * The JWT contains an `exp` claim. We schedule a refresh 60s before expiry
 * so the token is always valid when Axios attaches it.
 * The 401 interceptor remains as a safety net.
 */

const REFRESH_MARGIN_MS = 60_000  // refresh 60s before expiry

let _token: string | null = null
let _refreshTimer: ReturnType<typeof setTimeout> | null = null
let _onRefreshNeeded: (() => void) | null = null

/** Registers the refresh callback (called from App.tsx to avoid circular imports). */
export const registerRefreshCallback = (fn: () => void): void => {
  _onRefreshNeeded = fn
}

/** Decodes the `exp` claim (in ms) from a JWT payload. */
const decodeExp = (token: string): number | null => {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]))
    return typeof payload.exp === "number" ? payload.exp * 1000 : null
  } catch {
    return null
  }
}

const clearTimer = (): void => {
  if (_refreshTimer !== null) {
    clearTimeout(_refreshTimer)
    _refreshTimer = null
  }
}

const scheduleRefresh = (token: string): void => {
  clearTimer()
  if (!_onRefreshNeeded) return
  const exp = decodeExp(token)
  if (!exp) return
  const delay = exp - Date.now() - REFRESH_MARGIN_MS
  if (delay <= 0) {
    // Token already expired or expiring within 60s: refresh immediately
    _onRefreshNeeded()
    return
  }
  _refreshTimer = setTimeout(_onRefreshNeeded, delay)
}

export const setToken = (token: string | null): void => {
  clearTimer()
  _token = token
  if (token) scheduleRefresh(token)
}

export const getToken = (): string | null => _token
