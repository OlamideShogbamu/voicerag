import { Suspense } from "react";
import { VoiceConsole } from "./components/voice-console";

export default function DashboardPage() {
  return (
    <Suspense>
      <VoiceConsole />
    </Suspense>
  );
}
