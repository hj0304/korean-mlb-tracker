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

export type ChartMetric = "avg" | "era";

// Per-game batting average (hits / at-bats). Null when the player had no at-bat
// (e.g. a pinch-run / walk-only game) so the line skips it.
function gameAvg(stats: { [key: string]: unknown }): number | null {
  const atBats = Number(stats.atBats);
  if (!atBats) return null;
  return Number(stats.hits) / atBats;
}

// Innings pitched use the ".1/.2 = thirds" convention (1.2 = 1⅔ innings).
function parseInnings(ip: unknown): number {
  const n = Number(ip);
  if (!Number.isFinite(n)) return 0;
  const whole = Math.trunc(n);
  const outs = Math.round((n - whole) * 10); // 0, 1, or 2
  return whole + outs / 3;
}

// Per-game ERA (earned runs * 9 / innings). Null when the pitcher recorded no
// outs, where ERA is undefined (avoids dividing by zero / plotting infinity).
function gameEra(stats: { [key: string]: unknown }): number | null {
  const innings = parseInnings(stats.inningsPitched);
  if (innings === 0) return null;
  return (Number(stats.earnedRuns) * 9) / innings;
}

type MetricConfig = {
  label: string;
  compute: (stats: { [key: string]: unknown }) => number | null;
  domain: [number, number | "auto"];
  ticks?: number[];
  format: (v: number) => string;
  // Plotted values are clamped to this so a single blow-up outing doesn't
  // flatten the rest of the line; the tooltip still shows the true value.
  cap?: number;
};

const METRICS: Record<ChartMetric, MetricConfig> = {
  avg: {
    label: "경기 타율",
    compute: gameAvg,
    domain: [0, 1],
    ticks: [0, 0.25, 0.5, 0.75, 1],
    format: (v) => v.toFixed(3),
  },
  era: {
    label: "경기 ERA",
    compute: gameEra,
    // Auto-scale, but cap the plotted height: a short outing can push a single
    // game's ERA into the 20s/30s, which would squash every normal game flat.
    domain: [0, "auto"],
    cap: 13.5,
    format: (v) => v.toFixed(2),
  },
};

export function RecentGamesChart({
  games,
  metric,
  seasonValue,
}: {
  games: GameLog[];
  metric: ChartMetric;
  seasonValue: number | null;
}) {
  const cfg = METRICS[metric];
  // API returns newest-first; chart reads left→right oldest→newest. `value` is
  // what we plot (clamped to the cap); `raw` is the true value for the tooltip.
  const data = [...games].reverse().map((g) => {
    const raw = cfg.compute(g.stats);
    const value = raw !== null && cfg.cap !== undefined ? Math.min(raw, cfg.cap) : raw;
    return { date: g.game_date.slice(5), value, raw };
  });

  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={data} margin={{ top: 16, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
        <XAxis dataKey="date" tickLine={false} axisLine={false} fontSize={12} />
        <YAxis
          domain={cfg.domain}
          ticks={cfg.ticks}
          tickFormatter={cfg.format}
          tickLine={false}
          axisLine={false}
          width={44}
          fontSize={12}
        />
        <Tooltip
          formatter={(_value, _name, item) => {
            // Show the true value, not the clamped one we plot.
            const raw = (item?.payload as { raw: number | null } | undefined)?.raw;
            return [typeof raw === "number" ? cfg.format(raw) : "-", cfg.label];
          }}
        />
        {seasonValue !== null ? (
          <ReferenceLine
            y={seasonValue}
            stroke="#8b95a1"
            strokeDasharray="4 2"
            label={{
              value: `시즌 ${cfg.format(seasonValue)}`,
              position: "insideTopRight",
              fontSize: 11,
            }}
          />
        ) : null}
        <Line
          type="monotone"
          dataKey="value"
          name={cfg.label}
          stroke="#e23b2e"
          strokeWidth={2}
          dot={{ r: 3 }}
          connectNulls
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
