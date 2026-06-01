// Sentry init for the Node.js server runtime. Loaded from instrumentation.ts.
// Stays disabled when NEXT_PUBLIC_SENTRY_DSN is unset (init is a no-op).
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
});
