import Link from "next/link";

import { TaegeukMark } from "@/components/TaegeukMark";
import { ThemeToggle } from "@/components/ThemeToggle";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b bg-card/90 backdrop-blur">
      <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-3">
        <Link
          href="/"
          className="flex items-center gap-2 text-sm font-semibold tracking-tight"
        >
          <TaegeukMark className="h-5 w-5" />
          태극기 펄럭이며
        </Link>
        <ThemeToggle />
      </div>
    </header>
  );
}
