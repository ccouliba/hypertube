import { useCallback } from "react"
import { useNavigate } from "react-router-dom"
import { useAppDispatch, useAppSelector } from "@/hooks/useAppStore"
import { login, register, logout, clearError } from "@/store/slices/authSlice"
import type { LoginPayload, RegisterPayload } from "@/types/auth.types"

/**
 * Primary hook for all authentication concerns.
 * Encapsulates dispatch, selectors, and navigation so components stay Redux-agnostic.
 */
const useAuth = () => {
  
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { user, token, isAuthenticated, loading, error } = useAppSelector(
    (state) => state.auth
  )

  const handleLogin = async (payload: LoginPayload) => {
    const result = await dispatch(login(payload))
    if (login.fulfilled.match(result)) {
      navigate("/")
    }
  }

  const handleRegister = async (payload: RegisterPayload) => {
    const result = await dispatch(register(payload))
    if (register.fulfilled.match(result)) {
      const loginResult = await dispatch(login({ username: payload.username, password: payload.password }))
      if (login.fulfilled.match(loginResult)) {
        navigate("/")
      }
    }
  }

  const handleLogout = () => {
    dispatch(logout())
    navigate("/login")
  }

  const resetError = useCallback(() => dispatch(clearError()), [dispatch])

  return {
    user,
    token,
    isAuthenticated,
    loading,
    error,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    resetError,
  }
}

export default useAuth
