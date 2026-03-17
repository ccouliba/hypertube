import React, { useState, useEffect } from "react"
import useAuth from "@/hooks/useAuth"
import type { RegisterPayload } from "@/types/auth.types"
import RegisterPageView from "./views/RegisterPageView"

const initialForm: RegisterPayload = {
  firstname: "",
  lastname: "",
  username: "",
  email: "",
  password: "",
}

const RegisterPage: React.FC = () => {
  const { register, loading, error, resetError } = useAuth()
  const [form, setForm] = useState<RegisterPayload>(initialForm)

  useEffect(() => {
    resetError()
  }, [resetError])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    await register(form)
  }

  return (
    <RegisterPageView
      form={form}
      loading={loading}
      error={error}
      onChange={handleChange}
      onSubmit={handleSubmit}
    />
  )
}

export default RegisterPage
