import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import LoginPage from "@/features/auth/LoginPage"
import RegisterPage from "@/features/auth/RegisterPage"
import ProtectedRoute from "@/features/auth/ProtectedRoute"
import HomePage from "@/features/home/HomePage"
import { registerRefreshCallback } from "@/api/tokenStore"
import { bootstrapAuth } from "@/store/slices/authSlice"
import { fetchConfig } from "@/store/slices/configSlice"
import { store } from "@/store"

// Registers the proactive refresh callback in tokenStore.
registerRefreshCallback(() => {
  store.dispatch(bootstrapAuth())
})

// Bootstrap on mount: public config + silent auth refresh.
store.dispatch(fetchConfig())
store.dispatch(bootstrapAuth())

const App = () => (
  <BrowserRouter>
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<HomePage />} />
      </Route>

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </BrowserRouter>
)

export default App
