// Single backend API client (see CLAUDE.md). The generic fetch + error-handling
// core; endpoint-typed query hooks build on it in lib/queries.ts (S1-13).

import type { components } from "./api.types"

// Friendly aliases for the OpenAPI-generated response schemas. Regenerate
// api.types.ts with `npm run gen:types` after the backend API changes.
export type Player = components["schemas"]["PlayerOut"]
export type PlayerDetail = components["schemas"]["PlayerDetailOut"]
export type GameLog = components["schemas"]["GameLogOut"]
export type SeasonStats = components["schemas"]["SeasonStatsOut"]

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"

/** Thrown on any non-2xx response. Carries the status and parsed body. */
export class ApiError extends Error {
  readonly status: number
  readonly body: unknown

  constructor(status: number, message: string, body: unknown) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.body = body
  }
}

// FastAPI puts the human-readable reason in `detail` (a string for our
// HTTPExceptions). Fall back to the status line otherwise.
function messageFromBody(body: unknown, fallback: string): string {
  if (body !== null && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail
    if (typeof detail === "string") return detail
  }
  return fallback
}

/**
 * Fetch JSON from the backend. `path` is absolute from the host
 * (e.g. "/api/v1/players"). Throws {@link ApiError} on a non-2xx response.
 */
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { Accept: "application/json", ...init?.headers },
  })

  if (!res.ok) {
    const body: unknown = await res.json().catch(() => null)
    const message = messageFromBody(body, `${res.status} ${res.statusText}`)
    throw new ApiError(res.status, message, body)
  }

  return res.json() as Promise<T>
}
