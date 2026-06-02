import Link from "next/link";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { Player } from "@/lib/api";

export function PlayerCard({ player }: { player: Player }) {
  return (
    <Link href={`/players/${player.id}`} className="block">
      <Card className="h-full transition-colors hover:bg-accent">
        <CardHeader>
          <CardTitle>{player.full_name_ko}</CardTitle>
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
