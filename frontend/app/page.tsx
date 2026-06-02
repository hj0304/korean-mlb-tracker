import { PlayerList } from "@/components/PlayerList";

export default function Home() {
  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-10">
      <h1 className="mb-6 text-2xl font-bold tracking-tight">한국인 MLB 선수</h1>
      <PlayerList />
    </main>
  );
}
