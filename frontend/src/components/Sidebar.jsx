import {
  LayoutDashboard,
  GitCompare,
  Newspaper,
  Sparkles,
  FileText,
  Settings,
  LogOut,
} from "lucide-react";
import { Link } from "react-router-dom";
import { signOut } from "firebase/auth";
import { auth } from "../lib/firebase";
import { useAuth } from "../context/AuthContext";

const menuItems = [
  { name: "Dashboard", icon: LayoutDashboard, path: "/" },
  { name: "Compare Products", icon: GitCompare, path: "/compare" },
  { name: "Recent Updates", icon: Newspaper, path: "/updates" },
  { name: "AI Analyst", icon: Sparkles, path: "/analyst" },
  { name: "Saved Reports", icon: FileText, path: "/reports" },
  { name: "Settings", icon: Settings, path: "/settings" },
];

function Sidebar() {
  const { user } = useAuth();
  const handleLogout = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <aside className="w-64 min-h-screen bg-slate-950 text-white border-r border-slate-800 flex flex-col">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-slate-800">
        <h1 className="text-xl font-bold">Competitive AI</h1>
        <p className="text-xs text-slate-400 mt-1">Intelligence Platform</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-5 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              to={item.path}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-800 hover:text-white transition"
            >
              <Icon size={18} />
              <span className="text-sm">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* User + Logout */}
      <div className="border-t border-slate-800 p-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-9 h-9 rounded-full bg-slate-700 flex items-center justify-center">
            {user?.displayName?.charAt(0).toUpperCase() || "U"}
          </div>

          <div>
            <p className="text-sm font-medium">{user?.displayName || "User"}</p>

            <p className="text-xs text-slate-400">{user?.email || "Analyst"}</p>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition"
        >
          <LogOut size={18} />
          <span className="text-sm">Logout</span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
