"use client";

import { useState } from "react";

import { ErrorState } from "@/components/ErrorState";
import { PlayerCard } from "@/components/PlayerCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { usePlayers } from "@/lib/queries";

// Highest level first; tabs only render for levels that currently have players,
// so a level with no prospects right now doesn't show an empty tab.
const LEVEL_ORDER = ["MLB", "AAA", "AA", "A+", "A", "R"] as const;
const LEVEL_LABEL: Record<string, string> = {
  MLB: "MLB",
  AAA: "AAA",
  AA: "AA",
  "A+": "A+",
  A: "A",
  R: "루키",
};

const ALL = "ALL";

export function PlayerList() {
  const { data, isLoading, error, refetch } = usePlayers();
  const [level, setLevel] = useState<string>(ALL);

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-28 w-full rounded-xl" />
        ))}
      </div>
    );
  }
  if (error) {
    return (
      <ErrorState message="선수 목록을 불러오지 못했습니다." onRetry={() => void refetch()} />
    );
  }

  const players = data ?? [];
  const presentLevels = LEVEL_ORDER.filter((l) => players.some((p) => p.current_level === l));
  const filtered = level === ALL ? players : players.filter((p) => p.current_level === level);

  return (
    <div className="flex flex-col gap-6">
      <Tabs value={level} onValueChange={setLevel}>
        <div className="overflow-x-auto">
          <TabsList>
            <TabsTrigger value={ALL}>전체 {players.length}</TabsTrigger>
            {presentLevels.map((l) => (
              <TabsTrigger key={l} value={l}>
                {LEVEL_LABEL[l]} {players.filter((p) => p.current_level === l).length}
              </TabsTrigger>
            ))}
          </TabsList>
        </div>
      </Tabs>

      {filtered.length === 0 ? (
        <p className="text-sm text-muted-foreground">해당 레벨의 선수가 없습니다.</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((player) => (
            <PlayerCard key={player.id} player={player} />
          ))}
        </div>
      )}
    </div>
  );
}
