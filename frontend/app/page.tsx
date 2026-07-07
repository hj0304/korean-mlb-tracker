import Link from "next/link";

import { TaegeukMark } from "@/components/TaegeukMark";

// Celebrating-runner silhouette on a lit disc, with baseball-seam stitches.
// Fixed colors: the landing is always navy regardless of the app theme.
function HeroSilhouette({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 230 260" className={className} aria-hidden="true">
      <circle cx="115" cy="132" r="103" fill="#14324F" />
      <path
        d="M115 4 A128 128 0 0 1 218 56"
        fill="none"
        stroke="#CD2E3A"
        strokeWidth="3"
        strokeDasharray="2 8"
        strokeLinecap="round"
        opacity="0.5"
      />
      <path
        d="M12 208 A128 128 0 0 0 115 260"
        fill="none"
        stroke="#CD2E3A"
        strokeWidth="3"
        strokeDasharray="2 8"
        strokeLinecap="round"
        opacity="0.5"
      />
      <g fill="#04101C" stroke="#04101C">
        <circle cx="112" cy="46" r="13" stroke="none" />
        <path d="M120 38 L138 44 L121 51 Z" stroke="none" />
        <path d="M98 62 L126 62 L119 134 L100 134 Z" strokeWidth="7" strokeLinejoin="round" />
        <path d="M101 66 C 86 52, 70 34, 58 20" fill="none" strokeWidth="11" strokeLinecap="round" />
        <circle cx="56" cy="18" r="6" stroke="none" />
        <path d="M123 66 C 138 52, 154 34, 166 20" fill="none" strokeWidth="11" strokeLinecap="round" />
        <circle cx="168" cy="18" r="6" stroke="none" />
        <path d="M104 130 C 92 154, 82 174, 76 198" fill="none" strokeWidth="13" strokeLinecap="round" />
        <path d="M76 198 L60 206" fill="none" strokeWidth="10" strokeLinecap="round" />
        <path d="M118 130 C 132 150, 146 166, 160 180" fill="none" strokeWidth="13" strokeLinecap="round" />
        <path d="M160 180 L174 172" fill="none" strokeWidth="10" strokeLinecap="round" />
      </g>
      <path
        d="M104 84 A18 18 0 0 1 122 100"
        fill="none"
        stroke="#CD2E3A"
        strokeWidth="4"
        strokeLinecap="round"
        opacity="0.9"
      />
    </svg>
  );
}

export default function LandingPage() {
  return (
    <main className="flex min-h-svh flex-col bg-[#081C30] text-[#F5F2EA]">
      <nav className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-5">
        <span className="flex items-center gap-2 text-sm font-semibold tracking-tight">
          <TaegeukMark className="h-5 w-5" />
          태극기 펄럭이며
        </span>
      </nav>

      <div className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center gap-10 px-6 py-10 md:flex-row md:gap-8">
        <div className="flex max-w-xl flex-1 flex-col items-start gap-5">
          <p className="text-xs tracking-[0.3em] text-[#85B7EB]">
            한국인 메이저리거 트래커
          </p>
          <h1 className="text-4xl font-bold leading-tight tracking-tight sm:text-5xl">
            태극기 펄럭이며
          </h1>
          <p className="text-[15px] leading-relaxed text-white/60">
            MLB와 MiLB에서 뛰는 한국인 선수들의 매일 경기 결과와 시즌 스탯을
            한곳에서.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link
              href="/dashboard"
              className="rounded-lg bg-[#CD2E3A] px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-[#B72833]"
            >
              오늘의 기록 보기 →
            </Link>
            <Link
              href="/dashboard#players"
              className="rounded-lg border border-white/30 px-6 py-3 text-sm transition-colors hover:bg-white/10"
            >
              선수 목록
            </Link>
          </div>
        </div>
        <HeroSilhouette className="w-56 shrink-0 sm:w-72" />
      </div>

      <div className="border-t border-white/10 bg-white/5">
        <p className="mx-auto w-full max-w-5xl px-6 py-3.5 text-[13px] text-white/70">
          MLB·MiLB 전 레벨 추적 · 매일 KST 16:00 자동 갱신 · 명예 한국인 포함
        </p>
      </div>
    </main>
  );
}
