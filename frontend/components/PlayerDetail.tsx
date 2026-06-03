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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { SeasonStats } from "@/lib/api";
import { usePlayer, usePlayerGames } from "@/lib/queries";
import { cn } from "@/lib/utils";

// JSONB stats are free-form; pull a value as display text. Every tracked player
// is currently a batter, so we render hitting stats (pitching split comes in S2-08).
function stat(stats: { [key: string]: unknown }, key: string): string {
  const value = stats[key];
  return value === null || value === undefined ? "-" : String(value);
}

// Headline stats shown big at the top (the "at a glance" grid).
const SEASON_SUMMARY: [string, string][] = [
  ["avg", "타율"],
  ["homeRuns", "홈런"],
  ["hits", "안타"],
  ["rbi", "타점"],
  ["runs", "득점"],
  ["stolenBases", "도루"],
  ["obp", "출루율"],
  ["ops", "OPS"],
];

// Full season line for the 통산기록 table (one row per season).
const SEASON_TABLE: [string, string][] = [
  ["avg", "타율"],
  ["gamesPlayed", "경기"],
  ["atBats", "타수"],
  ["hits", "안타"],
  ["doubles", "2루타"],
  ["triples", "3루타"],
  ["homeRuns", "홈런"],
  ["rbi", "타점"],
  ["runs", "득점"],
  ["stolenBases", "도루"],
  ["baseOnBalls", "볼넷"],
  ["strikeOuts", "삼진"],
  ["obp", "출루율"],
  ["ops", "OPS"],
];

// Per-game box-score line columns.
const GAME_COLS: [string, string][] = [
  ["plateAppearances", "타석"],
  ["atBats", "타수"],
  ["runs", "득점"],
  ["hits", "안타"],
  ["doubles", "2루타"],
  ["triples", "3루타"],
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
          <Skeleton key={i} className="h-20 w-full rounded-md" />
        ))}
      </div>
      <Skeleton className="h-40 w-full rounded-md" />
    </div>
  );
}

function GamesTable({ playerId }: { playerId: number }) {
  const games = usePlayerGames(playerId);

  if (games.isLoading) {
    return <Skeleton className="h-40 w-full rounded-md" />;
  }
  if (games.error) {
    return (
      <ErrorState message="경기 기록을 불러오지 못했습니다." onRetry={() => void games.refetch()} />
    );
  }
  if (!games.data || games.data.length === 0) {
    return <p className="text-sm text-muted-foreground">최근 경기 기록이 없습니다.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-muted/50">
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
            <TableCell className="whitespace-nowrap">{g.game_date}</TableCell>
            <TableCell className="whitespace-nowrap">
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
  );
}

function SeasonTable({ seasons }: { seasons: SeasonStats[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-muted/50">
          <TableHead>시즌</TableHead>
          {SEASON_TABLE.map(([key, label]) => (
            <TableHead key={key} className="text-right">
              {label}
            </TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {seasons.map((s) => (
          <TableRow key={s.season}>
            <TableCell className="font-medium">{s.season}</TableCell>
            {SEASON_TABLE.map(([key]) => (
              <TableCell key={key} className="text-right">
                {stat(s.stats, key)}
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function PlayerDetail({ playerId }: { playerId: number }) {
  const player = usePlayer(playerId);

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
  const seasons = p.season_stats
    .filter((s) => s.group_name === "hitting")
    .sort((a, b) => b.season - a.season);
  const current = seasons[0];

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

      {current ? (
        <section className="flex flex-col gap-3">
          <h2 className="text-lg font-semibold">{current.season} 시즌</h2>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {SEASON_SUMMARY.map(([key, label], i) => (
              <div
                key={key}
                className={cn(
                  "rounded-md border p-4 text-center",
                  i === 0 && "border-t-2 border-t-primary",
                )}
              >
                <div className="text-xs text-muted-foreground">{label}</div>
                <div className="mt-1 text-2xl font-bold">{stat(current.stats, key)}</div>
              </div>
            ))}
          </div>
        </section>
      ) : (
        <p className="text-sm text-muted-foreground">시즌 기록이 없습니다.</p>
      )}

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">기록</h2>
        <Tabs defaultValue="season">
          <TabsList>
            <TabsTrigger value="season">통산기록</TabsTrigger>
            <TabsTrigger value="games">경기별기록</TabsTrigger>
          </TabsList>
          <TabsContent value="season">
            {seasons.length > 0 ? (
              <SeasonTable seasons={seasons} />
            ) : (
              <p className="text-sm text-muted-foreground">시즌 기록이 없습니다.</p>
            )}
          </TabsContent>
          <TabsContent value="games">
            <GamesTable playerId={playerId} />
          </TabsContent>
        </Tabs>
      </section>
    </div>
  );
}
