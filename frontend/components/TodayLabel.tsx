"use client";

import { useSyncExternalStore } from "react";

function formatToday(): string {
  return new Intl.DateTimeFormat("ko-KR", {
    month: "long",
    day: "numeric",
    weekday: "short",
    timeZone: "Asia/Seoul",
  }).format(new Date());
}

// KST "7월 8일 (수)" label. Client-only via useSyncExternalStore because the
// landing is statically generated — a server-rendered date would freeze at
// build time. Server snapshot is empty; the client fills it after hydration.
export function TodayLabel() {
  const label = useSyncExternalStore(
    () => () => {},
    formatToday,
    () => "",
  );

  return <span suppressHydrationWarning>{label}</span>;
}
