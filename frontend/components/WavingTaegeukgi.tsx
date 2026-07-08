// Animated taegeukgi brand logo. A turbulence-driven displacement filter
// (SMIL, no JS) ripples the whole flag so it reads as cloth fluttering in
// wind. Colors are the flag's official red/blue and intentionally fixed.
//
// The filter id is static, so render at most one instance per page (the
// landing header and SiteHeader never appear together).

type Row = "solid" | "broken";

// One trigram: three stacked bars, orientation follows the flag's diagonals.
function Trigram({
  x,
  y,
  angle,
  rows,
}: {
  x: number;
  y: number;
  angle: number;
  rows: [Row, Row, Row];
}) {
  return (
    <g transform={`translate(${x} ${y}) rotate(${angle})`} fill="#0f0f0f">
      {rows.map((row, i) => {
        const y = (i - 1) * 2.7 - 0.85;
        return row === "solid" ? (
          <rect key={i} x="-5.5" y={y} width="11" height="1.7" />
        ) : (
          <g key={i}>
            <rect x="-5.5" y={y} width="4.7" height="1.7" />
            <rect x="0.8" y={y} width="4.7" height="1.7" />
          </g>
        );
      })}
    </g>
  );
}

export function WavingTaegeukgi({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 72 48" className={className} aria-hidden="true">
      <defs>
        <filter id="tk-wave" x="-15%" y="-20%" width="130%" height="140%">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.018 0.06"
            numOctaves="2"
            seed="3"
            result="noise"
          >
            <animate
              attributeName="baseFrequency"
              values="0.018 0.06;0.028 0.09;0.018 0.06"
              dur="3.2s"
              repeatCount="indefinite"
            />
          </feTurbulence>
          <feDisplacementMap
            in="SourceGraphic"
            in2="noise"
            scale="4.5"
            xChannelSelector="R"
            yChannelSelector="G"
          />
        </filter>
      </defs>

      <g filter="url(#tk-wave)">
        {/* field — hairline stroke so the white cloth reads on light headers */}
        <rect
          x="3"
          y="3"
          width="66"
          height="42"
          rx="2"
          fill="#f7f9fb"
          stroke="rgba(120,128,140,0.45)"
          strokeWidth="1"
        />

        {/* taegeuk, dividing line along the flag diagonal (red upper) */}
        <g transform="rotate(-33.69 36 24)">
          <circle cx="36" cy="24" r="12" fill="#0047A0" />
          <path
            d="M24 24 A12 12 0 0 1 48 24 A6 6 0 0 1 36 24 A6 6 0 0 0 24 24 Z"
            fill="#CD2E3A"
          />
        </g>

        {/* trigrams: 건(TL) 감(TR) 리(BL) 곤(BR) */}
        <Trigram x={20} y={13.3} angle={-56.31} rows={["solid", "solid", "solid"]} />
        <Trigram x={52} y={13.3} angle={56.31} rows={["broken", "solid", "broken"]} />
        <Trigram x={20} y={34.7} angle={56.31} rows={["solid", "broken", "solid"]} />
        <Trigram x={52} y={34.7} angle={-56.31} rows={["broken", "broken", "broken"]} />
      </g>
    </svg>
  );
}
