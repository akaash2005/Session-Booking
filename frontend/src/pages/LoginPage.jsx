import { useAuth } from "../context/AuthContext";
import { Navigate } from "react-router-dom";
import { useGoogleLogin } from "@react-oauth/google";
import api from "../utils/api";

export default function LoginPage() {
  const { user, login } = useAuth();

  if (user) return <Navigate to="/dashboard" replace />;

  // ✅ Google login (TOKEN-BASED)
  const googleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        const res = await api.post("/auth/google/", {
          access_token: tokenResponse.access_token,
        });

        // store token
        login(res.data.access, res.data.refresh);

        // redirect
        window.location.href = "/dashboard";
      } catch (err) {
        console.error(err);
        alert("Google login failed");
      }
    },
    onError: () => {
      console.log("Google Login Failed");
    },
  });

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Welcome to Sessions</h1>
        <p>Sign in to book sessions or create your own.</p>

        <div className="oauth-buttons">
          <button onClick={() => googleLogin()} className="btn-google">
            <img src="/google-icon.svg" alt="" />
            Continue with Google
          </button>

          <button
            onClick={() => alert("GitHub not wired yet")}
            className="btn-github"
          >
            <img src="/github-icon.svg" alt="" />
            Continue with GitHub
          </button>
        </div>

        <p className="terms">
          By signing in you agree to our{" "}
          <a href="#">Terms of Service</a> and{" "}
          <a href="#">Privacy Policy</a>.
        </p>
      </div>
    </div>
  );
}