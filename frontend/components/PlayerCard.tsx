import Link from "next/link";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { Player } from "@/lib/api";

export function PlayerCard({ player }: { player: Player }) {
  return (
    <Link href={`/players/${player.id}`} className="block">
      <Card className="h-full transition-colors hover:border-primary/40 hover:bg-accent">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {player.full_name_ko}
            {player.is_honorary ? (
              <span className="rounded bg-primary/10 px-1.5 py-0.5 text-xs font-medium text-primary">
                명예 한국인
              </span>
            ) : null}
          </CardTitle>
          <CardDescription>{player.full_name_en}</CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          {player.position}
          {player.current_level ? ` · ${player.current_level}` : ""}
        </CardContent>
      </Card>
    </Link>
  );
}
