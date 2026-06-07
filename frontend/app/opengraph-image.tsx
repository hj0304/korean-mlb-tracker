import { ImageResponse } from "next/og";

// Dynamic OG image (1200x630). Text is English on purpose: the satori renderer
// behind ImageResponse has no Korean font bundled, so Hangul wouldn't render.
export const alt = "Korean MLB Tracker";
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
          gap: 24,
          padding: "0 96px",
          background: "linear-gradient(135deg, #0b1220 0%, #111827 60%, #1f2937 100%)",
          color: "#f9fafb",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", height: 10, width: 120, background: "#3b82f6" }} />
        <div style={{ fontSize: 78, fontWeight: 800, letterSpacing: -2 }}>
          Korean MLB Tracker
        </div>
        <div style={{ fontSize: 36, color: "#9ca3af" }}>
          MLB &amp; MiLB Korean players — daily results and season stats
        </div>
      </div>
    ),
    size,
  );
}
