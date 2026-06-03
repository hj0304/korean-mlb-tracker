"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { GameLog } from "@/lib/api";

// Per-game batting average (hits / at-bats). Null when the player had no at-bat
// (e.g. a pinch-run / walk-only game) so the line skips it.
function gameAvg(stats: { [key: string]: unknown }): number | null {
  const atBats = Number(stats.atBats);
  if (!atBats) return null;
  return Number(stats.hits) / atBats;
}

export function RecentGamesChart({
  games,
  seasonAvg,
}: {
  games: GameLog[];
  seasonAvg: number | null;
}) {
  // API returns newest-first; chart reads left→right oldest→newest.
  const data = [...games].reverse().map((g) => ({
    date: g.game_date.slice(5), // MM-DD
    avg: gameAvg(g.stats),
  }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={data} margin={{ top: 16, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
        <XAxis dataKey="date" tickLine={false} axisLine={false} fontSize={12} />
        <YAxis
          domain={[0, 1]}
          ticks={[0, 0.25, 0.5, 0.75, 1]}
          tickFormatter={(v: number) => v.toFixed(3)}
          tickLine={false}
          axisLine={false}
          width={44}
          fontSize={12}
        />
        <Tooltip />
        {seasonAvg !== null ? (
          <ReferenceLine
            y={seasonAvg}
            stroke="#f97316"
            strokeDasharray="4 2"
            label={{ value: `시즌 ${seasonAvg.toFixed(3)}`, position: "insideTopRight", fontSize: 11 }}
          />
        ) : null}
        <Line
          type="monotone"
          dataKey="avg"
          name="경기 타율"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={{ r: 3 }}
          connectNulls
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
