"use client";

import { CalendarOff } from "lucide-react";
import Link from "next/link";

import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { Skeleton } from "@/components/ui/skeleton";
import type { DashboardGame } from "@/lib/api";
import { useDashboard } from "@/lib/queries";

function num(stats: { [key: string]: unknown }, key: string): number {
  const n = Number(stats[key]);
  return Number.isFinite(n) ? n : 0;
}

function txt(stats: { [key: string]: unknown }, key: string): string {
  const v = stats[key];
  return v === null || v === undefined ? "-" : String(v);
}

// Compact one-line stat summary for a player's game.
function lineFor(g: DashboardGame): string {
  const s = g.stats;
  if (g.group_name === "pitching") {
    const parts = [`${txt(s, "inningsPitched")}이닝`, `${num(s, "earnedRuns")}자책`, `${num(s, "strikeOuts")}K`];
    if (num(s, "wins") > 0) parts.push("승");
    return parts.join(" · ");
  }
  const parts = [`${num(s, "atBats")}타수 ${num(s, "hits")}안타`];
  if (num(s, "homeRuns") > 0) parts.push(`${num(s, "homeRuns")}홈런`);
  if (num(s, "rbi") > 0) parts.push(`${num(s, "rbi")}타점`);
  return parts.join(" · ");
}

// Notable performances to call out above the feed; null if nothing stood out.
function highlightFor(g: DashboardGame): string | null {
  const s = g.stats;
  if (g.group_name === "pitching") {
    if (num(s, "wins") > 0) return `${g.full_name_ko} 승리`;
    if (num(s, "inningsPitched") >= 1 && num(s, "earnedRuns") === 0) return `${g.full_name_ko} 무실점`;
    return null;
  }
  if (num(s, "homeRuns") > 0) return `${g.full_name_ko} ${num(s, "homeRuns")}홈런`;
  if (num(s, "hits") >= 3) return `${g.full_name_ko} ${num(s, "hits")}안타`;
  return null;
}

export function Dashboard() {
  const { data, isLoading, error, refetch } = useDashboard();

  if (isLoading) {
    // Mirror the loaded layout (heading + bordered feed) so the dashboard
    // doesn't grow and push the player list down when data arrives (CLS).
    return (
      <section className="flex flex-col gap-3">
        <Skeleton className="h-7 w-28 rounded-md" />
        <div className="divide-y rounded-md border">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="px-4 py-2.5">
              <Skeleton className="h-5 w-full rounded-md" />
            </div>
          ))}
        </div>
      </section>
    );
  }
  if (error) {
    return (
      <ErrorState message="최근 경기를 불러오지 못했습니다." onRetry={() => void refetch()} />
    );
  }
  if (!data || data.date === null || data.games.length === 0) {
    return (
      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">최근 경기</h2>
        <EmptyState message="최근 경기가 없습니다." icon={CalendarOff} />
      </section>
    );
  }

  const highlights = data.games.map(highlightFor).filter((h): h is string => h !== null);

  return (
    <section className="flex flex-col gap-3">
      <div className="flex items-baseline justify-between">
        <h2 className="text-lg font-semibold">최근 경기</h2>
        <span className="text-sm text-muted-foreground">{data.date}</span>
      </div>

      {highlights.length > 0 ? (
        <p className="rounded-md border border-t-2 border-t-primary bg-muted/30 p-3 text-sm">
          🔥 <span className="font-medium">오늘의 활약</span> · {highlights.join(", ")}
        </p>
      ) : null}

      <ul className="divide-y rounded-md border">
        {data.games.map((g) => (
          <li
            key={`${g.player_id}-${g.group_name}`}
            className="flex items-center justify-between gap-3 px-4 py-2.5"
          >
            <div className="flex min-w-0 items-center gap-2">
              <Link href={`/players/${g.player_id}`} className="font-medium hover:underline">
                {g.full_name_ko}
              </Link>
              {g.current_level ? (
                <span className="rounded bg-muted px-1.5 py-0.5 text-xs text-muted-foreground">
                  {g.current_level}
                </span>
              ) : null}
              <span
                className="whitespace-nowrap text-xs text-muted-foreground"
                title={g.opponent_name ?? undefined}
              >
                {g.is_home ? "vs" : "@"} {g.opponent_abbrev ?? g.opponent_id ?? "-"}
              </span>
            </div>
            <span className="whitespace-nowrap text-right text-sm tabular-nums">{lineFor(g)}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
