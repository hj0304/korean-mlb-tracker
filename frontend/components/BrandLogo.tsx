// Baseball brand mark (wireframe): light ball with a red ring. Fixed colors —
// the mark sits on dark surfaces and must not change with the theme.
export function BrandLogo({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 26 26" className={className} aria-hidden="true">
      <circle cx="13" cy="13" r="12" fill="#eef2f6" />
      <circle cx="13" cy="13" r="5.7" fill="none" stroke="#e23b2e" strokeWidth="1.2" />
    </svg>
  );
}
