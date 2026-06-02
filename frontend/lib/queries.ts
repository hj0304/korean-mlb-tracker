// TanStack Query hooks. Per CLAUDE.md, all query hooks live here (not scattered
// across components) so the data layer is in one place.

import { useQuery } from "@tanstack/react-query"

import { apiFetch, type GameLog, type Player, type PlayerDetail } from "./api"

export function usePlayers() {
  return useQuery({
    queryKey: ["players"],
    queryFn: () => apiFetch<Player[]>("/api/v1/players"),
  })
}

export function usePlayer(id: number) {
  return useQuery({
    queryKey: ["player", id],
    queryFn: () => apiFetch<PlayerDetail>(`/api/v1/players/${id}`),
  })
}

export function usePlayerGames(id: number) {
  return useQuery({
    queryKey: ["player", id, "games"],
    queryFn: () => apiFetch<GameLog[]>(`/api/v1/players/${id}/games`),
  })
}
