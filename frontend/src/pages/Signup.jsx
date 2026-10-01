import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles } from "lucide-react";
import {
  createUserWithEmailAndPassword,
  updateProfile,
} from "firebase/auth";
import { auth } from "../lib/firebase";

function Signup() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSignup = async (e) => {
    e.preventDefault();

    if (!name.trim() || !email.trim() || !password.trim()) {
      setError("Please fill in all fields.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const userCredential =
        await createUserWithEmailAndPassword(
          auth,
          email.trim(),
          password,
        );

      await updateProfile(userCredential.user, {
        displayName: name.trim(),
      });

      navigate("/");
    } catch (err) {
      console.error(err);

      switch (err.code) {
        case "auth/email-already-in-use":
          setError("An account with this email already exists.");
          break;

        case "auth/invalid-email":
          setError("Please enter a valid email address.");
          break;

        case "auth/weak-password":
          setError("Password must be at least 6 characters.");
          break;

        default:
          setError("Unable to create account. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center">
            <Sparkles size={20} className="text-white" />
          </div>

          <span className="text-xl font-bold text-slate-900">
            Competitive Intelligence
          </span>
        </div>

        {/* Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm">
          <h1 className="text-2xl font-bold text-slate-900">
            Create your account
          </h1>

          <p className="text-sm text-slate-500 mt-2">
            Create an account to save and manage your analyses.
          </p>

          <form onSubmit={handleSignup}>
            {/* Name */}
            <div className="mt-6">
              <label className="text-sm font-medium text-slate-700">
                Full Name
              </label>

              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                className="w-full mt-2 border border-slate-200 rounded-lg px-3 py-3 text-sm outline-none focus:border-slate-400"
              />
            </div>

            {/* Email */}
            <div className="mt-4">
              <label className="text-sm font-medium text-slate-700">
                Email
              </label>

              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full mt-2 border border-slate-200 rounded-lg px-3 py-3 text-sm outline-none focus:border-slate-400"
              />
            </div>

            {/* Password */}
            <div className="mt-4">
              <label className="text-sm font-medium text-slate-700">
                Password
              </label>

              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full mt-2 border border-slate-200 rounded-lg px-3 py-3 text-sm outline-none focus:border-slate-400"
              />
            </div>

            {/* Error */}
            {error && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
                <p className="text-sm text-red-600">
                  {error}
                </p>
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-6 bg-slate-900 text-white rounded-lg py-3 text-sm font-medium hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {loading
                ? "Creating account..."
                : "Create Account"}
            </button>
          </form>

          {/* Login */}
          <p className="text-sm text-slate-500 text-center mt-6">
            Already have an account?{" "}
            <Link
              to="/login"
              className="text-slate-900 font-medium hover:underline"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Signup;