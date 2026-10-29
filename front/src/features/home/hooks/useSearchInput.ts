import { useEffect, useRef, useState, type ChangeEvent, type KeyboardEvent } from "react"

const DEBOUNCE_MS = 700

export const useSearchInput = (value: string, onSearch: (query: string) => void) => {
  const [draft, setDraft] = useState(value)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    setDraft(value)
  }, [value])

  useEffect(() => () => {
    if (timerRef.current) clearTimeout(timerRef.current)
  }, [])

  const scheduleSearch = (query: string) => {
    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => onSearch(query), DEBOUNCE_MS)
  }

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const query = event.target.value
    setDraft(query)
    scheduleSearch(query)
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      if (timerRef.current) clearTimeout(timerRef.current)
      onSearch(draft)
    }
    if (event.key === "Escape") {
      if (timerRef.current) clearTimeout(timerRef.current)
      setDraft("")
      onSearch("")
    }
  }

  const clear = () => {
    if (timerRef.current) clearTimeout(timerRef.current)
    setDraft("")
    onSearch("")
  }

  return { draft, handleChange, handleKeyDown, clear }
}
