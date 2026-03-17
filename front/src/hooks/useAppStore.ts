// Typed Redux hooks — use these everywhere instead of the generic useDispatch/useSelector.
import { useDispatch, useSelector } from "react-redux"
import type { AppDispatch, RootState } from "@/store"
export const useAppDispatch = () => useDispatch<AppDispatch>()
export const useAppSelector = <T>(selector: (state: RootState) => T): T =>
  useSelector(selector)
