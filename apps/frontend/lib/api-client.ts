const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init.headers,
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(body.detail ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

export interface LiveKitToken {
  token: string;
  room_name: string;
  server_url: string;
  identity: string;
}

export const api = {
  livekit: {
    getToken: (userId: string | null) => {
      const qs = userId ? `?user_id=${encodeURIComponent(userId)}` : "";
      return request<LiveKitToken>(`/livekit/token${qs}`);
    },
  },
  ingest: {
    text: (userId: string, content: string) =>
      request<{ id: string; stored: boolean }>("/ingest/text", {
        method: "POST",
        body: JSON.stringify({ user_id: userId, content }),
      }),
  },
};

const _UID_KEY = "voicerag_user_id";

export function getOrCreateUserId(): string {
  if (typeof window === "undefined") return "";
  let id = localStorage.getItem(_UID_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(_UID_KEY, id);
  }
  return id;
}
