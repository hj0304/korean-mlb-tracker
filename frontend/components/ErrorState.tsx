import { Button } from "@/components/ui/button";

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center gap-3 py-8 text-center">
      <p className="text-sm text-destructive">{message}</p>
      {onRetry ? (
        <Button variant="outline" size="sm" onClick={onRetry}>
          다시 시도
        </Button>
      ) : null}
    </div>
  );
}
