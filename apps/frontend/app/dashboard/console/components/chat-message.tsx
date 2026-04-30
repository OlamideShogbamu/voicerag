interface ChatMessageProps {
  role: "user" | "agent";
  content: string;
  timestamp: string;
}

export function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  if (role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] sm:max-w-[60%]">
          <div className="bg-white border border-zinc-200 rounded-2xl rounded-tr-sm px-4 py-3">
            <p className="text-sm text-zinc-800 leading-relaxed">{content}</p>
            <p className="text-[11px] text-zinc-400 mt-1.5 text-right">{timestamp}</p>
          </div>
        </div>
      </div>
    );
  }
  return (
    <div className="max-w-[85%] sm:max-w-[60%]">
      <p className="text-sm text-zinc-700 leading-relaxed">{content}</p>
      <p className="text-[11px] text-zinc-400 mt-1.5">{timestamp}</p>
    </div>
  );
}
