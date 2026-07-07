// Simplified taegeuk (태극) brand mark. Colors are the flag's official-ish
// red/blue and intentionally fixed — the mark must not change with the theme.
export function TaegeukMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 56 56" className={className} aria-hidden="true">
      <circle cx="28" cy="28" r="24" fill="#0047A0" />
      <path
        d="M4 28 A24 24 0 0 1 52 28 A12 12 0 0 1 28 28 A12 12 0 0 0 4 28 Z"
        fill="#CD2E3A"
      />
    </svg>
  );
}
