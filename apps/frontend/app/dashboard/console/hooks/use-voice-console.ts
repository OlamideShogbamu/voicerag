"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Room, RoomEvent, Track, type RemoteAudioTrack } from "livekit-client";
import { api, getOrCreateUserId } from "@/lib/api-client";

export type VoiceConsoleState = "idle" | "connecting" | "active" | "error";

export interface Message {
  id: string;
  role: "user" | "agent";
  content: string;
  timestamp: string;
  isFinal: boolean;
}

export type MicPermission = "unknown" | "granted" | "denied";

function getTimestamp(): string {
  const d = new Date();
  const h = d.getHours();
  const m = d.getMinutes().toString().padStart(2, "0");
  const ampm = h >= 12 ? "PM" : "AM";
  return `${h % 12 || 12}:${m} ${ampm}`;
}

export function useVoiceConsole() {
  const [consoleState, setConsoleState] = useState<VoiceConsoleState>("idle");
  const [messages, setMessages] = useState<Message[]>([]);
  const [agentSpeaking, setAgentSpeaking] = useState(false);
  const [isMicEnabled, setIsMicEnabled] = useState(false);
  const [micPermission, setMicPermission] = useState<MicPermission>("unknown");
  const [error, setError] = useState("");

  const roomRef = useRef<Room | null>(null);
  const localIdentityRef = useRef<string>("");
  const audioElemsRef = useRef<HTMLAudioElement[]>([]);
  const connectingRef = useRef(false);

  const upsertMessage = useCallback(
    (id: string, role: "user" | "agent", text: string, isFinal: boolean) => {
      setMessages((prev) => {
        const idx = prev.findIndex((m) => m.id === id);
        const next: Message = { id, role, content: text, timestamp: getTimestamp(), isFinal };
        if (idx >= 0) {
          const updated = [...prev];
          updated[idx] = next;
          return updated;
        }
        return [...prev, next];
      });
    },
    [],
  );

  const cleanupAudio = useCallback(() => {
    audioElemsRef.current.forEach((el) => el.remove());
    audioElemsRef.current = [];
  }, []);

  const connect = useCallback(async (): Promise<Room | null> => {
    if (roomRef.current) return roomRef.current;
    if (connectingRef.current) return null;

    connectingRef.current = true;
    setConsoleState("connecting");
    setError("");

    try {
      const userId = getOrCreateUserId();
      const { token, server_url } = await api.livekit.getToken(userId);
      const room = new Room();
      roomRef.current = room;

      await room.startAudio();

      room.on(RoomEvent.TrackSubscribed, (track) => {
        if (track.kind !== Track.Kind.Audio) return;
        const audioEl = (track as RemoteAudioTrack).attach() as HTMLAudioElement;
        audioEl.autoplay = true;
        document.body.appendChild(audioEl);
        audioElemsRef.current.push(audioEl);
      });

      room.on(RoomEvent.TrackUnsubscribed, (track) => {
        if (track.kind !== Track.Kind.Audio) return;
        (track as RemoteAudioTrack).detach();
      });

      room.on(RoomEvent.ActiveSpeakersChanged, (speakers) => {
        const isAgent = speakers.some((p) => p.identity !== localIdentityRef.current);
        setAgentSpeaking(isAgent);
      });

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (room as any).registerTextStreamHandler?.(
        "lk.transcription",
        async (
          reader: { readAll: () => Promise<string>; info: { attributes: Record<string, string> } },
          participantInfo: { identity: string },
        ) => {
          const text = await reader.readAll();
          if (!text.trim()) return;
          const isFinal = reader.info.attributes["lk.transcription_final"] === "true";
          const segmentId = reader.info.attributes["lk.segment_id"] ?? crypto.randomUUID();
          const role: "agent" | "user" =
            participantInfo.identity === localIdentityRef.current ? "user" : "agent";
          upsertMessage(segmentId, role, text, isFinal);
        },
      );

      room.on(RoomEvent.Disconnected, () => {
        roomRef.current = null;
        cleanupAudio();
        setAgentSpeaking(false);
        setIsMicEnabled(false);
        connectingRef.current = false;
        setConsoleState("idle");
      });

      await room.connect(server_url, token);
      localIdentityRef.current = room.localParticipant.identity;
      connectingRef.current = false;
      setConsoleState("active");
      return room;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to connect";
      setError(msg);
      setConsoleState("error");
      roomRef.current = null;
      cleanupAudio();
      connectingRef.current = false;
      return null;
    }
  }, [upsertMessage, cleanupAudio]);

  const disconnect = useCallback(async () => {
    if (roomRef.current) {
      await roomRef.current.disconnect();
      roomRef.current = null;
    }
    cleanupAudio();
    setAgentSpeaking(false);
    setIsMicEnabled(false);
    setConsoleState("idle");
    connectingRef.current = false;
  }, [cleanupAudio]);

  const disconnectRef = useRef(disconnect);
  useEffect(() => {
    disconnectRef.current = disconnect;
  }, [disconnect]);

  useEffect(() => {
    return () => {
      disconnectRef.current();
    };
  }, []);

  const requestMicPermission = useCallback(async (): Promise<boolean> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((t) => t.stop());
      setMicPermission("granted");
      return true;
    } catch {
      setMicPermission("denied");
      setError("Microphone access denied. Allow access in your browser and reload.");
      return false;
    }
  }, []);

  const onStartListening = useCallback(async () => {
    if (micPermission !== "granted") {
      const granted = await requestMicPermission();
      if (!granted) return;
    }
    if (!roomRef.current) {
      const room = await connect();
      if (!room) return;
      await room.localParticipant.setMicrophoneEnabled(true);
      setIsMicEnabled(true);
    } else {
      await roomRef.current.localParticipant.setMicrophoneEnabled(true);
      setIsMicEnabled(true);
    }
  }, [micPermission, requestMicPermission, connect]);

  const onStopListening = useCallback(async () => {
    if (roomRef.current) {
      await roomRef.current.localParticipant.setMicrophoneEnabled(false);
      setIsMicEnabled(false);
    }
  }, []);

  return {
    consoleState,
    messages,
    agentSpeaking,
    isMicEnabled,
    micPermission,
    error,
    onStartListening,
    onStopListening,
  };
}
