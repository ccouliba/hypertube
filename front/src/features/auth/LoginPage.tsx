// LoginPage — container: manages form state and delegates rendering to LoginPageView.
import React, { useState, useEffect } from "react"
import useAuth from "@/hooks/useAuth"
import type { LoginPayload } from "@/types/auth.types"
import LoginPageView from "./views/LoginPageView"

const LoginPage: React.FC = () => {
  const { login, loading, error, resetError } = useAuth()
  const [form, setForm] = useState<LoginPayload>({ username: "", password: "" })

  useEffect(() => {
    resetError()
  }, [resetError])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    await login(form)
  }

  return (
    <LoginPageView
      form={form}
      loading={loading}
      error={error}
      onChange={handleChange}
      onSubmit={handleSubmit}
    />
  )
}

export default LoginPage
