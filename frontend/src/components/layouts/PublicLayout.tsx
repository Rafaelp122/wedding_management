import { Outlet } from "react-router-dom";

export function PublicLayout() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">Wedding Management</h1>
        </div>
      </header>
      <main className="container mx-auto">
        <Outlet />
      </main>
    </div>
  );
}
