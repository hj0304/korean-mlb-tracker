import Link from "next/link";

import { PlayerDetail } from "@/components/PlayerDetail";

// Next 16 passes route params as a Promise.
export default async function PlayerDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-10">
      <Link href="/" className="text-sm text-muted-foreground hover:underline">
        ← 선수 목록
      </Link>
      <div className="mt-6">
        <PlayerDetail playerId={Number(id)} />
      </div>
    </main>
  );
}
