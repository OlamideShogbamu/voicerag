"use client";

import Image from "next/image";
import { useEffect, useRef } from "react";
import { type AgentState } from "@livekit/components-react";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Mic01Icon,
  MicOff01Icon,
  VolumeHighIcon,
} from "@hugeicons/core-free-icons";
import { AgentAudioVisualizerRadial } from "@/components/agent-audio-visualizer-radial";
import { cn } from "@/lib/utils";
import { ChatMessage } from "./chat-message";
import { IngestDataButton } from "./ingest-data-button";
import { useVoiceConsole } from "../hooks/use-voice-console";

const VISUALIZER_COLOR = "#8B5CF6";

export function VoiceConsole() {
  const {
    consoleState,
    messages,
    agentSpeaking,
    isMicEnabled,
    micPermission,
    error,
    onStartListening,
    onStopListening,
  } = useVoiceConsole();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const hasMessages = messages.length > 0;
  const isConnecting = consoleState === "connecting";

  const agentState: AgentState = isConnecting
    ? "connecting"
    : agentSpeaking
      ? "speaking"
      : isMicEnabled
        ? "listening"
        : "idle";

  const orbIcon = agentSpeaking
    ? VolumeHighIcon
    : isMicEnabled
      ? Mic01Icon
      : MicOff01Icon;

  const statusLabel = isConnecting
    ? "Connecting..."
    : agentSpeaking
      ? "Agent speaking..."
      : isMicEnabled
        ? "Tap to stop"
        : "Tap to speak";

  const handleOrbClick = () => {
    if (isConnecting || agentSpeaking) return;
    if (isMicEnabled) onStopListening();
    else onStartListening();
  };

  return (
    <div className="flex-1 relative flex flex-col h-full overflow-hidden bg-white">
      <div className="absolute top-0 left-0 right-0 px-6 py-4 z-10 flex items-center gap-2">
        <Image
          src="/assets/voice-assistant.png"
          alt=""
          width={28}
          height={28}
          priority
          className="rounded-full"
        />
        <span className="text-sm font-semibold text-brand-gradient">VoiceRAG</span>
      </div>

      <div className="flex-1 overflow-y-auto pt-16 pb-2">
        <div className="w-full max-w-[700px] mx-auto px-4 sm:px-8 py-6 flex flex-col gap-5 sm:gap-7 min-h-full">
          <div
            className={cn(
              "flex-1 flex flex-col items-center justify-center gap-4 text-center transition-all duration-300",
              hasMessages ? "opacity-0 pointer-events-none h-0 overflow-hidden" : "opacity-100",
            )}
          >
            {micPermission === "denied" ? (
              <>
                <div className="flex items-center justify-center size-12 rounded-full bg-red-50">
                  <HugeiconsIcon icon={MicOff01Icon} size={22} className="text-red-500" />
                </div>
                <h1 className="text-xl font-semibold text-zinc-900">Microphone access denied</h1>
                <p className="text-sm text-zinc-500 max-w-xs">
                  Allow microphone access in your browser settings, then reload the page.
                </p>
              </>
            ) : (
              <>
                <h1 className="text-3xl sm:text-4xl font-bold text-brand-gradient">VoiceRAG</h1>
                <p className="text-sm text-zinc-500">
                  Tap the orb to start a conversation.
                </p>
                <p className="text-xs text-zinc-400 max-w-sm">
                  Ask anything, or say &ldquo;remember that…&rdquo; to save a note for later.
                </p>
              </>
            )}
          </div>

          {hasMessages &&
            messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                role={msg.role}
                content={msg.content}
                timestamp={msg.timestamp}
              />
            ))}

          {error && <p className="text-sm text-red-500 text-center">{error}</p>}

          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="shrink-0 flex flex-col items-center gap-3 px-4 pb-8 pt-2">
        <button
          onClick={handleOrbClick}
          disabled={isConnecting}
          aria-label={statusLabel}
          className={cn(
            "relative size-[224px] rounded-full focus:outline-none transition-opacity duration-200",
            isConnecting && "cursor-default opacity-90",
          )}
        >
          <AgentAudioVisualizerRadial
            size="lg"
            radius={92}
            barCount={32}
            state={agentState}
            color={VISUALIZER_COLOR}
            className="absolute inset-0"
          />

          <div
            className={cn(
              "absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2",
              "size-36 rounded-full bg-brand-gradient",
              "shadow-lg shadow-fuchsia-500/30 ring-1 ring-white/30",
              "flex items-center justify-center",
              "transition-transform duration-200",
              agentSpeaking && "scale-105",
            )}
          >
            <HugeiconsIcon
              icon={orbIcon}
              size={40}
              className="text-white drop-shadow-sm"
              strokeWidth={1.6}
            />
          </div>
        </button>

        <p className="text-xs text-zinc-500 transition-all duration-200">{statusLabel}</p>
      </div>

      <IngestDataButton />
    </div>
  );
}
