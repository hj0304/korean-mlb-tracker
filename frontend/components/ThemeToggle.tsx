"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button";

export function ThemeToggle() {
  const { setTheme, resolvedTheme } = useTheme();

  // Both icons are always rendered; the `.dark` class (set by next-themes before
  // paint) shows the right one via CSS, so there's no hydration mismatch and no
  // need for a mounted flag.
  return (
    <Button
      variant="outline"
      size="icon"
      aria-label="테마 전환"
      onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
    >
      <Sun className="hidden h-4 w-4 dark:block" />
      <Moon className="h-4 w-4 dark:hidden" />
    </Button>
  );
}
