import { BrowserRouter, Routes, Route } from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

import DashboardLayout from "./layouts/DashboardLayout";
import Settings from "./pages/Settings";
import Dashboard from "./pages/Dashboard";
import Compare from "./pages/Compare";
import AIAnalyst from "./pages/AIAnalyst";
import RecentUpdates from "./pages/RecentUpdates";
import Reports from "./pages/Reports";
import Login from "./pages/Login";
import Signup from "./pages/Signup";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route element={<DashboardLayout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/compare" element={<Compare />} />
              <Route path="/analyst" element={<AIAnalyst />} />
              <Route path="/updates" element={<RecentUpdates />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/settings" element={<Settings />} />
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;