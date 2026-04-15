import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function OAuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const { loginWithTokens } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const access = searchParams.get("access");
    const refresh = searchParams.get("refresh");

    if (access && refresh) {
      loginWithTokens(access, refresh);
      navigate("/dashboard", { replace: true });
    } else {
      // Something went wrong — send back to login
      navigate("/login", { replace: true });
    }
  }, []);

  return (
    <div className="center">
      <p>Signing you in...</p>
    </div>
  );
}