// Auth types — all data shapes exchanged with the auth API and Redux state.

export interface User {
  id: number
  username: string
  email: string
  firstname: string
  lastname: string
  language: string
  profile_picture: string
}

// Request payloads
export interface RegisterPayload {
  username: string
  email: string
  firstname: string
  lastname: string
  password: string
}

export interface LoginPayload {
  username: string
  password: string
}

export interface UpdateUserPayload {
  username?: string
  email?: string
  firstname?: string
  lastname?: string
  language?: string
  profile_picture?: string
}

// API responses
export interface LoginResponse {
  message: string
  access_token: string
  user: User
}

export interface AccessTokenResponse {
  access_token: string
  user?: User
}

export interface RegisterResponse {
  message: string
  user: Pick<User, 'username' | 'profile_picture'>
}

export interface UsersListResponse {
  users: Pick<User, 'id' | 'username'>[]
}

// Redux state
export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  bootstrapping: boolean   // true while the initial silent refresh has not yet resolved
  loading: boolean
  error: string | null
}
