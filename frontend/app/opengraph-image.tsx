import { ImageResponse } from "next/og";

// Dynamic OG image (1200x630). Text is English on purpose: the satori renderer
// behind ImageResponse has no Korean font bundled, so Hangul wouldn't render.
export const alt = "태극기 펄럭이며 — Korean MLB Tracker";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          justifyContent: "center",
          gap: 28,
          padding: "0 96px",
          background: "#081C30",
          color: "#F7F4EC",
          fontFamily: "sans-serif",
        }}
      >
        <svg width="120" height="120" viewBox="0 0 56 56">
          <circle cx="28" cy="28" r="24" fill="#0047A0" />
          <path
            d="M4 28 A24 24 0 0 1 52 28 A12 12 0 0 1 28 28 A12 12 0 0 0 4 28 Z"
            fill="#CD2E3A"
          />
        </svg>
        <div style={{ fontSize: 76, fontWeight: 800, letterSpacing: -2 }}>
          Taegeukgi Fluttering
        </div>
        <div style={{ fontSize: 34, color: "#85B7EB" }}>
          Korean MLB &amp; MiLB players — daily results and season stats
        </div>
      </div>
    ),
    size,
  );
}
