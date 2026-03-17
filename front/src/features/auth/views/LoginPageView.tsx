import React from "react"
import { Link } from "react-router-dom"
import styled from "styled-components"
import type { LoginPayload } from "@/types/auth.types"

export interface LoginPageViewProps {
  form: LoginPayload
  loading: boolean
  error: string | null
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void
}

const LoginPageView: React.FC<LoginPageViewProps> = ({
  form,
  loading,
  error,
  onChange,
  onSubmit,
}) => (
  <Page>
    <Card>
      <Logo>HyperTube</Logo>
      <Title>Sign In</Title>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      <Form onSubmit={onSubmit}>
        <Input
          name="username"
          type="text"
          placeholder="Username"
          value={form.username}
          onChange={onChange}
          autoComplete="username"
          required
        />
        <Input
          name="password"
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={onChange}
          autoComplete="current-password"
          required
        />
        <SubmitButton type="submit" disabled={loading}>
          {loading ? "Signing in…" : "Sign In"}
        </SubmitButton>
      </Form>

      <Footer>
        New to HyperTube?
        <Link to="/register">Sign up now</Link>
      </Footer>
    </Card>
  </Page>
)

export default LoginPageView

const Page = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: ${({ theme }) => theme.colors.background};
`

const Card = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  padding: ${({ theme }) => theme.spacing.xl};
  border-radius: ${({ theme }) => theme.radii.md};
  width: 100%;
  max-width: 450px;
`

const Logo = styled.h1`
  color: ${({ theme }) => theme.colors.primary};
  font-size: ${({ theme }) => theme.fontSizes.xl};
  font-weight: 700;
  text-align: center;
  letter-spacing: -1px;
  margin-bottom: ${({ theme }) => theme.spacing.xl};
`

const Title = styled.h2`
  font-size: ${({ theme }) => theme.fontSizes.lg};
  font-weight: 700;
  margin-bottom: ${({ theme }) => theme.spacing.lg};
`

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.md};
`

const Input = styled.input`
  background-color: ${({ theme }) => theme.colors.inputBg};
  border: 1px solid transparent;
  border-radius: ${({ theme }) => theme.radii.sm};
  color: ${({ theme }) => theme.colors.text};
  font-size: ${({ theme }) => theme.fontSizes.md};
  padding: 14px 16px;
  width: 100%;
  transition: border-color 0.15s;

  &:focus {
    border-color: ${({ theme }) => theme.colors.inputFocus};
  }

  &::placeholder {
    color: ${({ theme }) => theme.colors.textMuted};
  }
`

const SubmitButton = styled.button`
  background-color: ${({ theme }) => theme.colors.primary};
  border-radius: ${({ theme }) => theme.radii.sm};
  color: #fff;
  font-size: ${({ theme }) => theme.fontSizes.md};
  font-weight: 700;
  padding: 16px;
  width: 100%;
  transition: background-color 0.15s;
  margin-top: ${({ theme }) => theme.spacing.sm};

  &:hover:not(:disabled) {
    background-color: ${({ theme }) => theme.colors.primaryHover};
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`

const ErrorMessage = styled.p`
  color: ${({ theme }) => theme.colors.error};
  font-size: ${({ theme }) => theme.fontSizes.sm};
  padding: ${({ theme }) => theme.spacing.sm};
  background-color: rgba(232, 124, 3, 0.1);
  border-radius: ${({ theme }) => theme.radii.sm};
`

const Footer = styled.p`
  color: ${({ theme }) => theme.colors.textSecondary};
  font-size: ${({ theme }) => theme.fontSizes.sm};
  margin-top: ${({ theme }) => theme.spacing.lg};
  text-align: center;

  a {
    color: ${({ theme }) => theme.colors.text};
    font-weight: 700;
    margin-left: 4px;

    &:hover {
      text-decoration: underline;
    }
  }
`
