"use client";

// TEMPORARY (S0-11 verification): throws a client-side error so we can confirm
// Sentry receives the event from the deployed frontend. Remove once verified.
export default function SentryTestPage() {
  return (
    <button
      type="button"
      onClick={() => {
        throw new Error("Sentry frontend verification error");
      }}
    >
      Throw test error
    </button>
  );
}
