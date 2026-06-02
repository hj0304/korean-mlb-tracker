"use client";

import { PlayerCard } from "@/components/PlayerCard";
import { usePlayers } from "@/lib/queries";

// Basic loading/error states here; skeletons + richer error UI come in S1-16.
export function PlayerList() {
  const { data, isLoading, error } = usePlayers();

  if (isLoading) {
    return <p className="text-muted-foreground">선수 목록을 불러오는 중…</p>;
  }
  if (error) {
    return <p className="text-destructive">선수 목록을 불러오지 못했습니다.</p>;
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {data?.map((player) => (
        <PlayerCard key={player.id} player={player} />
      ))}
    </div>
  );
}
