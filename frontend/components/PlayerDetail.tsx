"use client";

import { ErrorState } from "@/components/ErrorState";
import { RecentGamesChart } from "@/components/RecentGamesChart";
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

// JSONB stats are free-form; pull a value as display text.
function stat(stats: { [key: string]: unknown }, key: string): string {
  const value = stats[key];
  return value === null || value === undefined ? "-" : String(value);
}

// Per-type display config: which stat group to read and which keys to show in
// each section. Pitchers and batters are rendered from the same components,
// just different columns (S2-08).
type StatConfig = {
  group: "hitting" | "pitching";
  // The big accented rate-stat line at the top of the summary.
  slash: [string, string][];
  // Counting-stat tiles below the slash line.
  summary: [string, string][];
  // 통산기록 table columns.
  seasonTable: [string, string][];
  // 경기별기록 table columns.
  gameCols: [string, string][];
  // Per-game batting-average trend chart (batters only for now).
  chart: { key: string; label: string } | null;
};

const BATTER: StatConfig = {
  group: "hitting",
  slash: [
    ["avg", "AVG"],
    ["obp", "OBP"],
    ["slg", "SLG"],
    ["ops", "OPS"],
  ],
  summary: [
    ["homeRuns", "홈런"],
    ["hits", "안타"],
    ["rbi", "타점"],
    ["runs", "득점"],
    ["stolenBases", "도루"],
    ["plateAppearances", "타석"],
    ["baseOnBalls", "볼넷"],
    ["strikeOuts", "삼진"],
  ],
  seasonTable: [
    ["avg", "타율"],
    ["gamesPlayed", "경기"],
    ["plateAppearances", "타석"],
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
    ["slg", "장타율"],
    ["ops", "OPS"],
  ],
  gameCols: [
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
  ],
  chart: { key: "avg", label: "경기별 타율 추이" },
};

const PITCHER: StatConfig = {
  group: "pitching",
  slash: [
    ["era", "ERA"],
    ["whip", "WHIP"],
    ["strikeoutsPer9Inn", "K/9"],
    ["walksPer9Inn", "BB/9"],
  ],
  summary: [
    ["wins", "승"],
    ["losses", "패"],
    ["saves", "세이브"],
    ["holds", "홀드"],
    ["inningsPitched", "이닝"],
    ["strikeOuts", "탈삼진"],
    ["baseOnBalls", "볼넷"],
    ["gamesPitched", "경기"],
  ],
  seasonTable: [
    ["era", "ERA"],
    ["gamesPitched", "경기"],
    ["gamesStarted", "선발"],
    ["wins", "승"],
    ["losses", "패"],
    ["saves", "세이브"],
    ["holds", "홀드"],
    ["inningsPitched", "이닝"],
    ["hits", "피안타"],
    ["earnedRuns", "자책"],
    ["strikeOuts", "탈삼진"],
    ["baseOnBalls", "볼넷"],
    ["whip", "WHIP"],
  ],
  gameCols: [
    ["inningsPitched", "이닝"],
    ["hits", "피안타"],
    ["runs", "실점"],
    ["earnedRuns", "자책"],
    ["homeRuns", "홈런"],
    ["baseOnBalls", "볼넷"],
    ["strikeOuts", "탈삼진"],
  ],
  chart: null,
};

function configFor(playerType: string): StatConfig {
  return playerType === "pitcher" ? PITCHER : BATTER;
}

function DetailSkeleton() {
  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col gap-2">
        <Skeleton className="h-9 w-40" />
        <Skeleton className="h-4 w-28" />
        <Skeleton className="h-4 w-56" />
      </div>
      <Skeleton className="h-[88px] w-full rounded-md" />
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} className="h-20 w-full rounded-md" />
        ))}
      </div>
      <Skeleton className="h-40 w-full rounded-md" />
    </div>
  );
}

function GamesTable({
  playerId,
  group,
  cols,
}: {
  playerId: number;
  group: string;
  cols: [string, string][];
}) {
  const games = usePlayerGames(playerId);

  if (games.isLoading) {
    return <Skeleton className="h-40 w-full rounded-md" />;
  }
  if (games.error) {
    return (
      <ErrorState message="경기 기록을 불러오지 못했습니다." onRetry={() => void games.refetch()} />
    );
  }
  const rows = games.data?.filter((g) => g.group_name === group) ?? [];
  if (rows.length === 0) {
    return <p className="text-sm text-muted-foreground">최근 경기 기록이 없습니다.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-muted/50">
          <TableHead>날짜</TableHead>
          <TableHead>상대</TableHead>
          {cols.map(([key, label]) => (
            <TableHead key={key} className="text-right">
              {label}
            </TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((g) => (
          <TableRow key={`${g.game_id}-${g.group_name}`}>
            <TableCell className="whitespace-nowrap">{g.game_date}</TableCell>
            <TableCell className="whitespace-nowrap">
              {g.is_home ? "vs" : "@"} {g.opponent_id ?? "-"}
            </TableCell>
            {cols.map(([key]) => (
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

function ChartSection({
  playerId,
  label,
  seasonAvg,
}: {
  playerId: number;
  label: string;
  seasonAvg: number | null;
}) {
  const games = usePlayerGames(playerId);

  if (games.isLoading) {
    return <Skeleton className="h-60 w-full rounded-md" />;
  }
  const hitting = games.data?.filter((g) => g.group_name === "hitting") ?? [];
  // No chart when there's nothing to plot; the table tab still covers the data.
  if (games.error || hitting.length === 0) {
    return null;
  }
  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-lg font-semibold">{label}</h2>
      <RecentGamesChart games={hitting} seasonAvg={seasonAvg} />
    </section>
  );
}

function SeasonTable({
  seasons,
  cols,
}: {
  seasons: SeasonStats[];
  cols: [string, string][];
}) {
  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-muted/50">
          <TableHead>시즌</TableHead>
          {cols.map(([key, label]) => (
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
            {cols.map(([key]) => (
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
  const cfg = configFor(p.player_type);
  const seasons = p.season_stats
    .filter((s) => s.group_name === cfg.group)
    .sort((a, b) => b.season - a.season);
  const current = seasons[0];
  const chartAvg = current && cfg.chart ? Number(current.stats[cfg.chart.key]) : NaN;
  const seasonAvg = Number.isFinite(chartAvg) ? chartAvg : null;

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
          <div className="grid grid-cols-4 gap-2 rounded-md border border-t-2 border-t-primary bg-muted/30 p-4">
            {cfg.slash.map(([key, label]) => (
              <div key={key} className="text-center">
                <div className="text-xs font-medium text-muted-foreground">{label}</div>
                <div className="mt-1 text-2xl font-bold tabular-nums text-primary">
                  {stat(current.stats, key)}
                </div>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {cfg.summary.map(([key, label]) => (
              <div key={key} className="rounded-md border p-4 text-center">
                <div className="text-xs text-muted-foreground">{label}</div>
                <div className="mt-1 text-2xl font-bold tabular-nums">
                  {stat(current.stats, key)}
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : (
        <p className="text-sm text-muted-foreground">시즌 기록이 없습니다.</p>
      )}

      {cfg.chart ? (
        <ChartSection playerId={playerId} label={cfg.chart.label} seasonAvg={seasonAvg} />
      ) : null}

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">기록</h2>
        <Tabs defaultValue="season">
          <TabsList>
            <TabsTrigger value="season">통산기록</TabsTrigger>
            <TabsTrigger value="games">경기별기록</TabsTrigger>
          </TabsList>
          <TabsContent value="season">
            {seasons.length > 0 ? (
              <SeasonTable seasons={seasons} cols={cfg.seasonTable} />
            ) : (
              <p className="text-sm text-muted-foreground">시즌 기록이 없습니다.</p>
            )}
          </TabsContent>
          <TabsContent value="games">
            <GamesTable playerId={playerId} group={cfg.group} cols={cfg.gameCols} />
          </TabsContent>
        </Tabs>
      </section>
    </div>
  );
}
