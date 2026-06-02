"use client";

import { ErrorState } from "@/components/ErrorState";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { usePlayer, usePlayerGames } from "@/lib/queries";

// JSONB stats are free-form; pull a value as display text. Every tracked player
// is currently a batter, so we render hitting stats (pitching split comes in S2-08).
function stat(stats: { [key: string]: unknown }, key: string): string {
  const value = stats[key];
  return value === null || value === undefined ? "-" : String(value);
}

// [stat key, Korean label] for the season summary grid. The full 34-field stat
// object is stored; this is the meaningful batting subset (incl. BB/SO).
const SEASON_HITTING: [string, string][] = [
  ["gamesPlayed", "경기"],
  ["plateAppearances", "타석"],
  ["atBats", "타수"],
  ["runs", "득점"],
  ["hits", "안타"],
  ["doubles", "2루타"],
  ["triples", "3루타"],
  ["homeRuns", "홈런"],
  ["rbi", "타점"],
  ["baseOnBalls", "볼넷"],
  ["strikeOuts", "삼진"],
  ["stolenBases", "도루"],
  ["avg", "타율"],
  ["obp", "출루율"],
  ["slg", "장타율"],
  ["ops", "OPS"],
];

// Per-game box-score line columns. Wide on purpose (the table scrolls
// horizontally); curated from the 31 boxscore fields to the meaningful ones.
const GAME_COLS: [string, string][] = [
  ["plateAppearances", "타석"],
  ["atBats", "타수"],
  ["runs", "득점"],
  ["hits", "안타"],
  ["doubles", "2B"],
  ["triples", "3B"],
  ["homeRuns", "홈런"],
  ["rbi", "타점"],
  ["totalBases", "루타"],
  ["baseOnBalls", "볼넷"],
  ["strikeOuts", "삼진"],
  ["stolenBases", "도루"],
  ["groundIntoDoublePlay", "병살"],
];

function DetailSkeleton() {
  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col gap-2">
        <Skeleton className="h-9 w-40" />
        <Skeleton className="h-4 w-28" />
        <Skeleton className="h-4 w-56" />
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full rounded-md" />
        ))}
      </div>
      <Skeleton className="h-40 w-full rounded-md" />
    </div>
  );
}

export function PlayerDetail({ playerId }: { playerId: number }) {
  const player = usePlayer(playerId);
  const games = usePlayerGames(playerId);

  if (player.isLoading) {
    return <DetailSkeleton />;
  }
  if (player.error || !player.data) {
    return (
      <ErrorState
        message="선수 정보를 불러오지 못했습니다."
        onRetry={() => void player.refetch()}
      />
    );
  }

  const p = player.data;

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight">{p.full_name_ko}</h1>
        <p className="text-muted-foreground">{p.full_name_en}</p>
        <p className="text-sm text-muted-foreground">
          {p.position}
          {p.current_level ? ` · ${p.current_level}` : ""}
          {p.bats ? ` · 타격 ${p.bats}` : ""}
          {p.throws ? ` · 투구 ${p.throws}` : ""}
        </p>
      </header>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">시즌 누적</h2>
        {p.season_stats.length === 0 ? (
          <p className="text-sm text-muted-foreground">시즌 기록이 없습니다.</p>
        ) : (
          p.season_stats.map((s) => (
            <div key={`${s.season}-${s.group_name}`} className="flex flex-col gap-2">
              <p className="text-sm text-muted-foreground">{s.season}</p>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                {SEASON_HITTING.map(([key, label]) => (
                  <div key={key} className="rounded-md border p-3">
                    <div className="text-xs text-muted-foreground">{label}</div>
                    <div className="text-lg font-semibold">{stat(s.stats, key)}</div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">최근 경기</h2>
        {games.isLoading ? (
          <Skeleton className="h-40 w-full rounded-md" />
        ) : games.error ? (
          <ErrorState
            message="경기 기록을 불러오지 못했습니다."
            onRetry={() => void games.refetch()}
          />
        ) : !games.data || games.data.length === 0 ? (
          <p className="text-sm text-muted-foreground">최근 경기 기록이 없습니다.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>날짜</TableHead>
                <TableHead>상대</TableHead>
                {GAME_COLS.map(([key, label]) => (
                  <TableHead key={key} className="text-right">
                    {label}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {games.data.map((g) => (
                <TableRow key={`${g.game_id}-${g.group_name}`}>
                  <TableCell>{g.game_date}</TableCell>
                  <TableCell>
                    {g.is_home ? "vs" : "@"} {g.opponent_id ?? "-"}
                  </TableCell>
                  {GAME_COLS.map(([key]) => (
                    <TableCell key={key} className="text-right">
                      {stat(g.stats, key)}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </section>
    </div>
  );
}
