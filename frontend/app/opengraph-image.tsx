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
          background: "#07090c",
          color: "#eef2f6",
          fontFamily: "sans-serif",
        }}
      >
        <svg width="110" height="110" viewBox="0 0 26 26">
          <circle cx="13" cy="13" r="12" fill="#eef2f6" />
          <circle cx="13" cy="13" r="5.7" fill="none" stroke="#e23b2e" strokeWidth="1.2" />
        </svg>
        <div style={{ fontSize: 76, fontWeight: 800, letterSpacing: -2 }}>
          Taegeukgi Fluttering
        </div>
        <div style={{ fontSize: 34, color: "#8b95a1" }}>
          Korean MLB &amp; MiLB players — daily results and season stats
        </div>
        <div style={{ display: "flex", height: 8, width: 140, background: "#e23b2e" }} />
      </div>
    ),
    size,
  );
}
