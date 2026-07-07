"use client";

import Link from "next/link";

import { lineFor } from "@/components/Dashboard";
import { useDashboard } from "@/lib/queries";

// Bottom score strip on the landing (wireframe). Marquee loops the latest
// game feed; renders nothing while loading / when there are no games so the
// hero never shows an error state.
export function LandingTicker() {
  const { data } = useDashboard();

  if (!data || data.date === null || data.games.length === 0) return null;

  // Duplicate the list so translateX(-50%) loops seamlessly.
  const items = [...data.games, ...data.games];

  return (
    <div className="absolute inset-x-0 bottom-0 z-10 border-t border-white/[0.07] bg-gradient-to-b from-[rgba(9,12,16,0.4)] to-[rgba(5,7,9,0.92)] backdrop-blur-sm">
      <div className="flex h-16 items-stretch">
        <div className="flex items-center gap-2 whitespace-nowrap border-r border-white/[0.07] px-5 font-mono text-[11px] tracking-[2px] text-[#8b95a1]">
          <span className="h-[7px] w-[7px] animate-[blink_1.4s_infinite] rounded-full bg-[#e23b2e]" />
          최근 경기
        </div>
        <div className="relative flex-1 overflow-hidden">
          <div className="flex h-full w-max animate-[ticker_32s_linear_infinite] items-center">
            {items.map((g, i) => (
              <Link
                key={`${g.player_id}-${g.group_name}-${i}`}
                href={`/players/${g.player_id}`}
                className="flex items-center gap-3 whitespace-nowrap border-r border-white/[0.06] px-6"
              >
                {g.current_level ? (
                  <span className="font-mono text-[10px] tracking-wider text-[#e23b2e]">
                    {g.current_level}
                  </span>
                ) : null}
                <span className="text-sm font-medium text-[#d3d9e0]">
                  {g.full_name_ko}
                </span>
                <span className="text-xs text-[#8b95a1]">
                  vs {g.opponent_abbrev ?? g.opponent_id ?? "-"}
                </span>
                <span className="text-sm text-[#eef2f6]">{lineFor(g)}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
