import React from "react"
import { Navigate, Outlet } from "react-router-dom"
import { useAppSelector } from "@/hooks/useAppStore"

/** Guards routes that require authentication. */
const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, bootstrapping } = useAppSelector((state) => state.auth)

  // Bootstrap (silent refresh on mount) not yet resolved: wait without redirecting
  // to avoid a false logout on page load.
  if (bootstrapping) return null

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />
}

export default ProtectedRoute
