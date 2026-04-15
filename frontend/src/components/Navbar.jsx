import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        🎯 Sessions
      </Link>

      <div className="navbar-links">
        <Link to="/">Browse</Link>

        {user ? (
          <>
            {user.role === "creator" && (
              <Link to="/creator">My Sessions</Link>
            )}
            <Link to="/dashboard">Bookings</Link>
            <Link to="/profile">Profile</Link>
            <button className="btn-logout" onClick={handleLogout}>
              Logout
            </button>
          </>
        ) : (
          <Link to="/login" className="btn-primary">
            Sign In
          </Link>
        )}
      </div>
    </nav>
  );
}