"use client";

import { ErrorState } from "@/components/ErrorState";
import { PlayerCard } from "@/components/PlayerCard";
import { Skeleton } from "@/components/ui/skeleton";
import { usePlayers } from "@/lib/queries";

export function PlayerList() {
  const { data, isLoading, error, refetch } = usePlayers();

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

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {data?.map((player) => (
        <PlayerCard key={player.id} player={player} />
      ))}
    </div>
  );
}
