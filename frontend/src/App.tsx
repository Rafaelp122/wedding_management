import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "./stores/authStore";
import { PublicLayout } from "./components/layouts/PublicLayout";
import { AppLayout } from "./components/layouts/AppLayout";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";

function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <Routes>
      {/* Public Routes */}
      <Route element={<PublicLayout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<h1>Home Page</h1>} />
      </Route>

      {/* Protected Routes */}
      <Route
        element={
          isAuthenticated ? <AppLayout /> : <Navigate to="/login" replace />
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/weddings" element={<h1>Weddings</h1>} />
        <Route path="/scheduler" element={<h1>Scheduler</h1>} />
        <Route path="/contracts" element={<h1>Contracts</h1>} />
        <Route path="/budget" element={<h1>Budget</h1>} />
        <Route path="/items" element={<h1>Items</h1>} />
      </Route>

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
