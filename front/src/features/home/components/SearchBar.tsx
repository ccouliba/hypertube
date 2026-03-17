import React, { useEffect, useRef, useState } from "react"
import styled from "styled-components"

const DEBOUNCE_MS = 700

interface SearchBarProps {
  value: string
  onSearch: (query: string) => void
  placeholder?: string
}


const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onSearch,
  placeholder = "Search movies, TV shows…",
}) => {
  const [draft, setDraft] = useState(value)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    setDraft(value)
  }, [value])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const q = e.target.value
    setDraft(q)
    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => onSearch(q), DEBOUNCE_MS)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      if (timerRef.current) clearTimeout(timerRef.current)
      onSearch(draft)
    }
    if (e.key === "Escape") {
      if (timerRef.current) clearTimeout(timerRef.current)
      setDraft("")
      onSearch("")
    }
  }

  useEffect(() => () => { if (timerRef.current) clearTimeout(timerRef.current) }, [])

  return (
    <Wrapper>
      <Icon aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.2}>
          <circle cx={11} cy={11} r={8} />
          <line x1={21} y1={21} x2={16.65} y2={16.65} />
        </svg>
      </Icon>
      <Input
        type="search"
        value={draft}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        aria-label="Search"
        autoComplete="off"
        spellCheck={false}
      />
      {draft && (
        <ClearBtn
          onClick={() => { setDraft(""); onSearch("") }}
          aria-label="Clear search"
          type="button"
        >
          ✕
        </ClearBtn>
      )}
    </Wrapper>
  )
}

export default SearchBar


const Wrapper = styled.div`
  position: relative;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
`

const Icon = styled.span`
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: ${({ theme }) => theme.colors.textSecondary};
  pointer-events: none;
  display: flex;
  align-items: center;
`

const Input = styled.input`
  width: 100%;
  padding: 12px 44px;
  background-color: ${({ theme }) => theme.colors.inputBg};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  color: ${({ theme }) => theme.colors.text};
  font-family: ${({ theme }) => theme.fonts.base};
  font-size: ${({ theme }) => theme.fontSizes.md};
  outline: none;
  transition: border-color 0.2s ease, background-color 0.2s ease;
  box-sizing: border-box;

  /* "search" reset */
  &::-webkit-search-cancel-button { display: none; }

  &::placeholder {
    color: ${({ theme }) => theme.colors.textMuted};
  }

  &:focus {
    border-color: ${({ theme }) => theme.colors.inputFocus};
    background-color: ${({ theme }) => theme.colors.surface};
  }
`

const ClearBtn = styled.button`
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: ${({ theme }) => theme.colors.textSecondary};
  font-size: 14px;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    color: ${({ theme }) => theme.colors.text};
  }
`
