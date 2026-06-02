// TanStack Query hooks. Per CLAUDE.md, all query hooks live here (not scattered
// across components) so the data layer is in one place.

import { useQuery } from "@tanstack/react-query"

import { apiFetch, type Player } from "./api"

export function usePlayers() {
  return useQuery({
    queryKey: ["players"],
    queryFn: () => apiFetch<Player[]>("/api/v1/players"),
  })
}
