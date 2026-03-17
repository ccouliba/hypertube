// Auth service — all HTTP calls to /api/auth (login, register, refresh, logout, stream token).
import apiClient from "@/api/axios"
import type {
  LoginPayload,
  LoginResponse,
  AccessTokenResponse,
  RegisterPayload,
  RegisterResponse,
  UpdateUserPayload,
  User,
  UsersListResponse,
} from "@/types/auth.types"

const BASE = "/api/auth"

const authService = {
  register: (payload: RegisterPayload): Promise<RegisterResponse> =>
    apiClient.post<RegisterResponse>(`${BASE}/register`, payload).then((r) => r.data),

  login: (payload: LoginPayload): Promise<LoginResponse> =>
    apiClient.post<LoginResponse>(`${BASE}/login`, payload, { withCredentials: true }).then((r) => r.data),

  /**
   * Silent token refresh — sends the httpOnly cookie automatically.
   * Called on app mount and by the Axios 401 interceptor.
   */
  refresh: (): Promise<AccessTokenResponse> =>
    apiClient
      .post<AccessTokenResponse>(`${BASE}/refresh`, null, { withCredentials: true })
      .then((r) => r.data),

  /**
   * Server-side logout — revokes the refresh token and clears the cookie.
   */
  logout: (): Promise<{ message: string }> =>
    apiClient
      .post<{ message: string }>(`${BASE}/logout`, null, { withCredentials: true })
      .then((r) => r.data),

  getUsers: (): Promise<UsersListResponse> =>
    apiClient.get<UsersListResponse>(`${BASE}/users`).then((r) => r.data),

  getUserById: (id: number): Promise<User> =>
    apiClient.get<User>(`${BASE}/users/${id}`).then((r) => r.data),

  updateUser: (id: number, payload: UpdateUserPayload): Promise<{ message: string; user: User }> =>
    apiClient
      .patch<{ message: string; user: User }>(`${BASE}/users/${id}`, payload)
      .then((r) => r.data),

  deleteUser: (id: number): Promise<{ message: string }> =>
    apiClient.delete<{ message: string }>(`${BASE}/users/${id}`).then((r) => r.data),

  /**
   * Ask the server to set a short-lived HttpOnly cookie (stream_token, path=/api/video).
   * Must be called with a valid access token before opening the video player.
   * The cookie is then sent automatically by the browser on every <video> request.
   */
  issueStreamToken: (): Promise<void> =>
    apiClient.post(`${BASE}/stream-token`, null, { withCredentials: true }).then(() => undefined),
}

export default authService
