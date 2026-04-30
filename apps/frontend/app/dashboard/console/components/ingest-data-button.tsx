"use client";

import { useState } from "react";
import { HugeiconsIcon } from "@hugeicons/react";
import { Add01Icon, Loading03Icon } from "@hugeicons/core-free-icons";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { api, getOrCreateUserId } from "@/lib/api-client";

type Status = "idle" | "submitting" | "error";

export function IngestDataButton() {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const reset = () => {
    setText("");
    setStatus("idle");
    setErrorMessage("");
  };

  const handleOpenChange = (next: boolean) => {
    setOpen(next);
    if (!next) reset();
  };

  const handleSubmit = async () => {
    const trimmed = text.trim();
    if (!trimmed || status === "submitting") return;

    setStatus("submitting");
    setErrorMessage("");

    try {
      await api.ingest.text(getOrCreateUserId(), trimmed);
      handleOpenChange(false);
    } catch (err) {
      setStatus("error");
      setErrorMessage(err instanceof Error ? err.message : "Failed to ingest");
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger
        className={cn(
          "fixed bottom-6 right-6 z-30 inline-flex items-center gap-2",
          "rounded-full bg-brand-gradient px-5 py-3 text-sm font-semibold text-white",
          "shadow-lg shadow-fuchsia-500/30 ring-1 ring-white/30",
          "transition-transform duration-200 hover:scale-[1.03] active:scale-[0.98]",
          "focus:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-400",
        )}
        aria-label="Ingest data"
      >
        <HugeiconsIcon icon={Add01Icon} size={18} />
        <span>Ingest data</span>
      </DialogTrigger>

      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Ingest data</DialogTitle>
          <DialogDescription>
            Paste text to embed into your knowledge base. The agent can recall it later.
          </DialogDescription>
        </DialogHeader>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste notes, articles, anything…"
          rows={6}
          disabled={status === "submitting"}
          className={cn(
            "w-full resize-none rounded-md border border-zinc-200 bg-white p-3 text-sm",
            "placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-fuchsia-400/60",
            "disabled:opacity-60",
          )}
        />

        {errorMessage && (
          <p className="text-xs text-red-500">{errorMessage}</p>
        )}

        <DialogFooter>
          <Button
            type="button"
            variant="ghost"
            onClick={() => handleOpenChange(false)}
            disabled={status === "submitting"}
          >
            Cancel
          </Button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!text.trim() || status === "submitting"}
            className={cn(
              "inline-flex items-center gap-2 rounded-md bg-brand-gradient px-4 py-2",
              "text-sm font-semibold text-white shadow-md shadow-fuchsia-500/20",
              "transition-opacity hover:opacity-95 disabled:opacity-50",
            )}
          >
            {status === "submitting" && (
              <HugeiconsIcon icon={Loading03Icon} size={16} className="animate-spin" />
            )}
            Save
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
