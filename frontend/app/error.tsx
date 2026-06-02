"use client"; // Error boundaries must be Client Components.

import { useEffect } from "react";

// Global error boundary: catches uncaught render errors in the route tree and
// shows a fallback instead of crashing the app. Next 16 passes `unstable_retry`
// (not `reset`) to re-render the segment.
export default function Error({
  error,
  unstable_retry,
}: {
  error: Error & { digest?: string };
  unstable_retry: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main className="flex min-h-full flex-col items-center justify-center gap-4 p-8 text-center">
      <h2 className="text-lg font-semibold">문제가 발생했습니다</h2>
      <p className="text-sm text-muted-foreground">
        데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.
      </p>
      <button
        type="button"
        onClick={() => unstable_retry()}
        className="rounded-md border px-4 py-2 text-sm hover:bg-accent"
      >
        다시 시도
      </button>
    </main>
  );
}
