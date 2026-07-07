import type { Metadata } from "next";

import { Dashboard } from "@/components/Dashboard";
import { PlayerList } from "@/components/PlayerList";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = { title: "대시보드" };

export default function DashboardPage() {
  return (
    <>
      <SiteHeader />
      <main className="mx-auto flex w-full max-w-5xl flex-col gap-10 px-6 py-8">
        <Dashboard />
        <div id="players" className="scroll-mt-20">
          <PlayerList />
        </div>
      </main>
    </>
  );
}
