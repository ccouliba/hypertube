import apiClient from "@/api/axios"
import type { SearchResponse } from "@/types/search.types"

const BASE = "/api/search"

const searchService = {
  /**
   * Unified search across movies and TV shows.
   * If query is empty, the backend returns popular content.
   */
  search: (query: string, page = 1, limit = 20): Promise<SearchResponse> =>
    apiClient
      .get<SearchResponse>(`${BASE}/`, { params: { query, page, limit } })
      .then((r) => r.data),
}

export default searchService
