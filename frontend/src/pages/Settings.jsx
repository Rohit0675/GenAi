import { useAuth } from "../context/AuthContext";
import { signOut } from "firebase/auth";
import { auth } from "../lib/firebase";
import { LogOut } from "lucide-react";

function Settings() {
  const { user } = useAuth();

  const handleLogout = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl">
        <h1 className="text-2xl font-bold text-slate-900">
          Settings
        </h1>

        <p className="mt-1 text-sm text-slate-500">
          Manage your account and application preferences.
        </p>

        <div className="mt-8 bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900">
            Account
          </h2>

          <div className="mt-6 space-y-4">
            <div>
              <p className="text-xs text-slate-500">Name</p>
              <p className="text-sm font-medium text-slate-900 mt-1">
                {user?.displayName || "Not provided"}
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-500">Email</p>
              <p className="text-sm font-medium text-slate-900 mt-1">
                {user?.email || "Not available"}
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-500">Authentication</p>
              <p className="text-sm font-medium text-slate-900 mt-1">
                Firebase Authentication
              </p>
            </div>
          </div>
        </div>

        <div className="mt-6 bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900">
            Session
          </h2>

          <button
            onClick={handleLogout}
            className="mt-4 flex items-center gap-2 px-4 py-2.5 rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition"
          >
            <LogOut size={17} />
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}

export default Settings;