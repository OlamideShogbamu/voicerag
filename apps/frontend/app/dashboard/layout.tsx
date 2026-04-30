export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="flex h-[100dvh] overflow-hidden font-sans bg-white">
      {children}
    </main>
  );
}
