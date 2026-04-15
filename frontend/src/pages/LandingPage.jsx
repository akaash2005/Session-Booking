import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../utils/api";

export default function LandingPage() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get("/sessions/")
      .then((res) => setSessions(res.data.results ?? res.data))
      .catch(() => setError("Failed to load sessions."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="landing">
      <section className="hero">
        <h1>Discover & Book Sessions</h1>
        <p>Learn from expert creators. One session at a time.</p>
        <Link to="/login" className="btn-primary">Get Started</Link>
      </section>

      <section className="catalog">
        <h2>Browse Sessions</h2>

        {loading && <p>Loading sessions...</p>}
        {error && <p className="error">{error}</p>}

        <div className="session-grid">
          {!loading && sessions.length === 0 && (
            <p>No sessions available yet. Check back soon!</p>
          )}

          {sessions.map((session) => (
            <div key={session.id} className="session-card">
              {session.cover_image && (
                <div className="session-image">
                  <img src={`http://localhost:8000/api/sessions/${session.id}/image/`} />
                </div>
              )}
              
              {/* Title clickable */}
              <Link to={`/sessions/${session.id}`}>
                <h3>{session.title}</h3>
              </Link>

              {/* Description */}
              <p>{session.description?.slice(0, 100)}...</p>

              {/* Meta */}
              <div className="session-meta">
                <span className="price">${session.price}</span>
                <span className="date">
                  {session.date
                    ? new Date(session.date).toLocaleDateString()
                    : "No date"}
                </span>
              </div>

              {/* Creator (SAFE) */}
              <span className="creator">
                by {session.creator_name || session.creator?.username || "Unknown"}
              </span>

            </div>
          ))}
        </div>
      </section>
    </div>
  );
}