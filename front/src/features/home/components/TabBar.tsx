import React from "react"
import styled from "styled-components"
import type { ActiveTab } from "@/types/search.types"

interface Tab {
  key: ActiveTab
  label: string
}

const TABS: Tab[] = [
  { key: "my_list", label: "My Board" },
  { key: "movies", label: "Movies" },
  { key: "tv_shows", label: "TV Shows" },
]

interface TabBarProps {
  active: ActiveTab
  onChange: (tab: ActiveTab) => void
}

const TabBar: React.FC<TabBarProps> = ({ active, onChange }) => (
  <Nav role="tablist" aria-label="Content type">
    {TABS.map(({ key, label }) => (
      <TabButton
        key={key}
        role="tab"
        aria-selected={active === key}
        $active={active === key}
        onClick={() => onChange(key)}
        type="button"
      >
        {label}
      </TabButton>
    ))}
  </Nav>
)

export default TabBar


const Nav = styled.nav`
  display: flex;
  justify-content: center;
  gap: ${({ theme }) => theme.spacing.sm};
`

const TabButton = styled.button<{ $active: boolean }>`
  background: none;
  border: none;
  border-bottom: 3px solid
    ${({ $active, theme }) => ($active ? theme.colors.primary : "transparent")};
  color: ${({ $active, theme }) =>
    $active ? theme.colors.text : theme.colors.textSecondary};
  font-family: ${({ theme }) => theme.fonts.base};
  font-size: ${({ theme }) => theme.fontSizes.md};
  font-weight: ${({ $active }) => ($active ? "700" : "400")};
  padding: ${({ theme }) => `${theme.spacing.sm} ${theme.spacing.md}`};
  cursor: pointer;
  transition: color 0.2s ease, border-color 0.2s ease;

  &:hover {
    color: ${({ theme }) => theme.colors.text};
  }
`
