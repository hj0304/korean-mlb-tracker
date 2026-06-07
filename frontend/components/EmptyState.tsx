import type { ComponentType } from "react";

// Consistent "nothing here" placeholder, mirroring ErrorState's centered layout.
// `icon` is any lucide icon (or anything taking a className).
export function EmptyState({
  message,
  icon: Icon,
}: {
  message: string;
  icon?: ComponentType<{ className?: string }>;
}) {
  return (
    <div className="flex flex-col items-center gap-2 py-10 text-center text-muted-foreground">
      {Icon ? <Icon className="h-8 w-8 opacity-40" /> : null}
      <p className="text-sm">{message}</p>
    </div>
  );
}
