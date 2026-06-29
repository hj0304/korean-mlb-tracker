"use client";

import { useState } from "react";

import { SearchX } from "lucide-react";

import { EmptyState } from "@/components/EmptyState";
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

// "명예 한국인" (honorary) are tracked alongside Korean nationals but shown as a
// separate group, so the list filters on two independent axes: category + level.
const CATEGORIES = [
  { value: ALL, label: "전체" },
  { value: "korean", label: "한국인" },
  { value: "honorary", label: "명예 한국인" },
] as const;

export function PlayerList() {
  const { data, isLoading, error, refetch } = usePlayers();
  const [category, setCategory] = useState<string>(ALL);
  const [level, setLevel] = useState<string>(ALL);

  if (isLoading) {
    // Mirror the loaded layout (tabs row + card grid) so the filter tabs don't
    // pop in and shove the cards down when data arrives (CLS).
    return (
      <div className="flex flex-col gap-6">
        <Skeleton className="h-9 w-64 rounded-md" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 9 }).map((_, i) => (
            <Skeleton key={i} className="h-28 w-full rounded-xl" />
          ))}
        </div>
      </div>
    );
  }
  if (error) {
    return (
      <ErrorState message="선수 목록을 불러오지 못했습니다." onRetry={() => void refetch()} />
    );
  }

  const players = data ?? [];
  // Category first; the level tabs (counts included) then reflect that subset.
  const inCategory =
    category === ALL
      ? players
      : players.filter((p) => (category === "honorary") === p.is_honorary);
  const presentLevels = LEVEL_ORDER.filter((l) => inCategory.some((p) => p.current_level === l));
  const activeLevel =
    level !== ALL && (presentLevels as readonly string[]).includes(level) ? level : ALL;
  const filtered =
    activeLevel === ALL ? inCategory : inCategory.filter((p) => p.current_level === activeLevel);

  return (
    <div className="flex flex-col gap-6">
      <Tabs
        value={category}
        onValueChange={(v) => {
          setCategory(v);
          setLevel(ALL); // reset level so it stays valid for the new category
        }}
      >
        <div className="overflow-x-auto">
          <TabsList>
            {CATEGORIES.map((c) => (
              <TabsTrigger key={c.value} value={c.value}>
                {c.label}{" "}
                {c.value === ALL
                  ? players.length
                  : players.filter((p) => (c.value === "honorary") === p.is_honorary).length}
              </TabsTrigger>
            ))}
          </TabsList>
        </div>
      </Tabs>

      <Tabs value={activeLevel} onValueChange={setLevel}>
        <div className="overflow-x-auto">
          <TabsList>
            <TabsTrigger value={ALL}>전체 {inCategory.length}</TabsTrigger>
            {presentLevels.map((l) => (
              <TabsTrigger key={l} value={l}>
                {LEVEL_LABEL[l]} {inCategory.filter((p) => p.current_level === l).length}
              </TabsTrigger>
            ))}
          </TabsList>
        </div>
      </Tabs>

      {filtered.length === 0 ? (
        <EmptyState message="해당 레벨의 선수가 없습니다." icon={SearchX} />
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
