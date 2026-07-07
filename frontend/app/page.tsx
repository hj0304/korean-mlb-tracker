import Image from "next/image";
import Link from "next/link";

import { BrandLogo } from "@/components/BrandLogo";
import { LandingTicker } from "@/components/LandingTicker";
import { TodayLabel } from "@/components/TodayLabel";

const ACCENT = "#e23b2e";

// Landing per the user's wireframe: near-black canvas, stadium-light
// gradients, masked player photo on the right, Black Han Sans headline,
// red accent, live score ticker at the bottom. Colors are fixed — this page
// is always dark regardless of the app theme.
export default function LandingPage() {
  return (
    <main className="relative min-h-svh w-full overflow-hidden bg-[#07090c] text-[#eef2f6]">
      {/* ambient light layers */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(120% 90% at 78% 8%, rgba(70,92,120,.28), rgba(7,9,12,0) 55%)",
        }}
      />
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(80% 60% at 12% 100%, rgba(24,58,40,.35), rgba(7,9,12,0) 60%)",
        }}
      />
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "linear-gradient(180deg, rgba(7,9,12,0) 40%, rgba(4,5,7,.85) 100%)",
        }}
      />
      <div
        className="pointer-events-none absolute inset-0 opacity-5"
        style={{
          backgroundImage:
            "repeating-linear-gradient(0deg, #fff 0 1px, transparent 1px 3px)",
        }}
      />

      {/* player photo, masked to fade into the canvas */}
      <Image
        src="/hero-player.png"
        alt=""
        width={298}
        height={449}
        priority
        className="pointer-events-none absolute bottom-0 right-[clamp(-40px,4vw,120px)] h-[min(92vh,860px)] w-auto select-none object-contain"
        style={{
          maskImage:
            "linear-gradient(180deg, #000 60%, transparent 99%), linear-gradient(90deg, transparent 0, #000 26%)",
          maskComposite: "intersect",
          WebkitMaskImage:
            "linear-gradient(180deg, #000 60%, transparent 99%), linear-gradient(90deg, transparent 0, #000 26%)",
          filter: "contrast(1.08) brightness(1.05)",
        }}
      />
      <div
        className="pointer-events-none absolute bottom-0 right-0 h-[min(92vh,860px)] w-[min(58vw,820px)]"
        style={{
          background:
            "linear-gradient(90deg, rgba(7,9,12,.55), rgba(7,9,12,0) 40%)",
        }}
      />

      {/* top bar */}
      <header className="relative z-10 flex items-center justify-between px-[clamp(24px,5vw,72px)] py-6">
        <div className="flex items-center gap-3">
          <BrandLogo className="h-[26px] w-[26px]" />
          <span className="font-heading text-xl leading-none tracking-tight">
            태극기 펄럭이며
          </span>
        </div>
        <nav className="flex items-center gap-[clamp(18px,2.4vw,40px)] text-sm font-medium text-[#aeb6c0]">
          <Link href="/dashboard" className="transition-colors hover:text-white">
            대시보드
          </Link>
          <Link href="/dashboard#players" className="transition-colors hover:text-white">
            선수
          </Link>
        </nav>
      </header>

      {/* hero */}
      <section className="relative z-10 max-w-[900px] px-[clamp(24px,5vw,72px)] pb-32 pt-[clamp(24px,6vh,80px)]">
        <div className="mb-7 flex animate-[rise_.6s_ease_both] items-center gap-3 font-mono text-[12.5px] tracking-[2.5px] text-[#8b95a1]">
          <span className="inline-flex items-center gap-2" style={{ color: ACCENT }}>
            <span
              className="h-2 w-2 animate-[blink_1.4s_infinite] rounded-full"
              style={{ background: ACCENT }}
            />
            LIVE
          </span>
          <span className="h-3 w-px bg-[#2a323c]" />
          2026 시즌 · <TodayLabel />
        </div>

        <h1
          className="m-0 animate-[rise_.7s_ease_.05s_both] font-heading text-[clamp(52px,8.4vw,132px)] font-normal leading-[0.94] tracking-tight"
          style={{ textShadow: "0 2px 40px rgba(0,0,0,.6)" }}
        >
          그라운드의
          <br />
          모든 순간을
          <br />
          <span style={{ color: ACCENT }}>기록</span>하다
        </h1>

        <p className="mt-8 max-w-[440px] animate-[rise_.7s_ease_.12s_both] text-base leading-[1.75] text-[#aeb6c0]">
          MLB와 MiLB에서 뛰는 한국인 선수들의
          <br />
          매일 경기 결과와 시즌 스탯을 한곳에서.
        </p>

        <div className="mt-11 flex animate-[rise_.7s_ease_.2s_both] flex-wrap gap-3.5">
          <Link
            href="/dashboard"
            className="inline-flex h-[58px] items-center gap-3 rounded px-8 text-[15.5px] font-bold tracking-[.3px] text-white transition-transform hover:-translate-y-0.5"
            style={{
              background: ACCENT,
              boxShadow: "0 10px 30px -8px rgba(226,59,46,.65)",
            }}
          >
            오늘의 기록 보기
            <span className="font-mono">→</span>
          </Link>
          <Link
            href="#"
            className="inline-flex h-[58px] items-center gap-2.5 rounded border border-[#303945] bg-white/[0.03] px-[30px] text-[15.5px] font-semibold tracking-[.3px] text-[#eef2f6] transition-colors hover:border-[#4a5563] hover:bg-white/[0.08]"
          >
            로그인
          </Link>
        </div>
      </section>

      <LandingTicker />
    </main>
  );
}
