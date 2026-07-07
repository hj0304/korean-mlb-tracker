import Link from "next/link";

import { BrandLogo } from "@/components/BrandLogo";
import { ThemeToggle } from "@/components/ThemeToggle";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b bg-background/85 backdrop-blur">
      <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-3">
        <Link href="/" className="flex items-center gap-2.5">
          <BrandLogo className="h-6 w-6" />
          <span className="font-heading text-lg leading-none tracking-tight">
            태극기 펄럭이며
          </span>
        </Link>
        <div className="flex items-center gap-6">
          <nav className="flex items-center gap-5 text-sm font-medium text-muted-foreground">
            <Link href="/dashboard" className="transition-colors hover:text-foreground">
              대시보드
            </Link>
            <Link
              href="/dashboard#players"
              className="transition-colors hover:text-foreground"
            >
              선수
            </Link>
          </nav>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
