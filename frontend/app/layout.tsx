import type { Metadata } from "next";
import { Bebas_Neue, Black_Han_Sans, JetBrains_Mono, Noto_Sans_KR } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const notoSansKr = Noto_Sans_KR({
  variable: "--font-sans",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jbmono",
  subsets: ["latin"],
});

// Display fonts for the sporty look: Black Han Sans for Korean headlines,
// Bebas Neue for latin numerals/stats.
const blackHanSans = Black_Han_Sans({
  variable: "--font-black-han",
  weight: "400",
  subsets: ["latin"],
});

const bebasNeue = Bebas_Neue({
  variable: "--font-bebas",
  weight: "400",
  subsets: ["latin"],
});

const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://korean-mlb-tracker-sabior-s-projects.vercel.app";
const SITE_NAME = "태극기 펄럭이며";
const TITLE = "태극기 펄럭이며 — 한국인 MLB · MiLB 트래커";
const DESCRIPTION =
  "메이저리그(MLB)·마이너리그(MiLB)에서 뛰는 한국인 선수들의 매일 경기 결과와 시즌 스탯을 한곳에서.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: TITLE,
    template: `%s · ${SITE_NAME}`,
  },
  description: DESCRIPTION,
  openGraph: {
    type: "website",
    locale: "ko_KR",
    siteName: SITE_NAME,
    url: SITE_URL,
    title: TITLE,
    description: DESCRIPTION,
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="ko"
      suppressHydrationWarning
      className={`${notoSansKr.variable} ${jetbrainsMono.variable} ${blackHanSans.variable} ${bebasNeue.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
