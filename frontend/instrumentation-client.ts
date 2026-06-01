// Sentry init for the browser. Runs before React hydration.
// Stays disabled when NEXT_PUBLIC_SENTRY_DSN is unset (init is a no-op).
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
});

export const onRouterTransitionStart = Sentry.captureRouterTransitionStart;
