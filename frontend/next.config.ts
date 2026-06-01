import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs";

const nextConfig: NextConfig = {
  /* config options here */
};

// org/project/authToken are read from env at build time (SENTRY_ORG, SENTRY_PROJECT,
// SENTRY_AUTH_TOKEN). Without them, source-map upload is skipped — the build still works.
export default withSentryConfig(nextConfig, {
  silent: true,
});
