import React, { useState, useRef, useEffect } from "react"
import styled from "styled-components"
import type { User } from "@/types/auth.types"

interface UserMenuProps {
  user: User
  onLogout: () => void
}

const UserMenu: React.FC<UserMenuProps> = ({ user, onLogout }) => {
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const handleLogout = () => {
    setOpen(false)
    onLogout()
  }

  return (
    <Container ref={containerRef}>
      <Trigger onClick={() => setOpen((prev) => !prev)} aria-expanded={open}>
        <Avatar aria-label="Profile picture">
          {user.profile_picture
            ? <AvatarImage src={user.profile_picture} alt={user.username} />
            : <AvatarFallback>{user.username[0].toUpperCase()}</AvatarFallback>
          }
        </Avatar>
        <Username>{user.username}</Username>
        <Chevron $open={open}>▾</Chevron>
      </Trigger>
      {open && (
        <Dropdown>
          <DropdownHeader>
            <DropdownName>{user.firstname} {user.lastname}</DropdownName>
            <DropdownEmail>{user.username}</DropdownEmail>
          </DropdownHeader>
          <Divider />
          <MenuItem disabled title="Coming soon">Downloads</MenuItem>
          <MenuItem disabled title="Coming soon">Account</MenuItem>
          <MenuItem disabled title="Coming soon">Settings</MenuItem>
          <Divider />
          <MenuItem $danger onClick={handleLogout}>Logout</MenuItem>
        </Dropdown>
      )}
    </Container>
  )
}

export default UserMenu


const Container = styled.div`
  position: relative;
  display: flex;
  align-items: center;
`

const Trigger = styled.button`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};
  background: none;
  border: none;
  cursor: pointer;
  padding: ${({ theme }) => `${theme.spacing.xs} ${theme.spacing.sm}`};
  border-radius: ${({ theme }) => theme.radii.md};
  color: ${({ theme }) => theme.colors.text};
  transition: background 0.15s;

  &:hover {
    background: ${({ theme }) => theme.colors.surfaceHover};
  }
`

const Avatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
`

const AvatarImage = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
`

const AvatarFallback = styled.div`
  width: 100%;
  height: 100%;
  background: ${({ theme }) => theme.colors.primary};
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
`

const Username = styled.span`
  font-size: ${({ theme }) => theme.fontSizes.md};
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
`

const Chevron = styled.span<{ $open: boolean }>`
  font-size: 12px;
  color: ${({ theme }) => theme.colors.textSecondary};
  transition: transform 0.2s;
  transform: ${({ $open }) => ($open ? "rotate(180deg)" : "rotate(0deg)")};
  display: inline-block;
`

const Dropdown = styled.div`
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 200px;
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  z-index: 200;
  overflow: hidden;
`

const DropdownHeader = styled.div`
  padding: ${({ theme }) => `${theme.spacing.md} ${theme.spacing.md} ${theme.spacing.sm}`};
`

const DropdownName = styled.p`
  margin: 0;
  font-size: ${({ theme }) => theme.fontSizes.md};
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
`

const DropdownEmail = styled.p`
  margin: ${({ theme }) => theme.spacing.xs} 0 0;
  font-size: ${({ theme }) => theme.fontSizes.sm};
  color: ${({ theme }) => theme.colors.textSecondary};
`

const Divider = styled.hr`
  border: none;
  border-top: 1px solid ${({ theme }) => theme.colors.border};
  margin: 0;
`

const MenuItem = styled.button<{ $danger?: boolean; disabled?: boolean }>`
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  padding: ${({ theme }) => `${theme.spacing.sm} ${theme.spacing.md}`};
  font-size: ${({ theme }) => theme.fontSizes.md};
  font-family: ${({ theme }) => theme.fonts.base};
  cursor: ${({ disabled }) => (disabled ? "default" : "pointer")};
  color: ${({ theme, $danger, disabled }) =>
    disabled
      ? theme.colors.textMuted
      : $danger
        ? theme.colors.error
        : theme.colors.text};
  transition: background 0.12s;

  &:hover {
    background: ${({ theme, disabled }) =>
      disabled ? "transparent" : theme.colors.surfaceHover};
  }
`
