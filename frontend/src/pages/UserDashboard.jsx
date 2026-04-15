import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../utils/api";

export default function UserDashboard() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get("/bookings/my/")
      .then((res) => {
        console.log("Bookings response:", res.data);
        setBookings(res.data.results ?? res.data);
      })
      .catch((err) => {
        console.error("Error:", err.response?.data || err);
        setError("Failed to load your bookings.");
      })
      .finally(() => setLoading(false));
  }, []);

  const handleCancel = async (bookingId) => {
    if (!confirm("Cancel this booking?")) return;

    try {
      await api.patch(`/bookings/${bookingId}/cancel/`);

      setBookings((prev) =>
        prev.map((b) =>
          b.id === bookingId ? { ...b, status: "cancelled" } : b
        )
      );
    } catch (err) {
      console.error(err);
      alert("Could not cancel. Try again.");
    }
  };

  const getSessionId = (booking) =>
    booking.session?.id ?? booking.session;

  const getSessionTitle = (booking) =>
    booking.session_title ||
    booking.session?.title ||
    `Session #${getSessionId(booking)}`;

  const getSessionPrice = (booking) =>
    booking.session_price ?? booking.session?.price ?? "—";

  const getSessionDate = (booking) =>
    booking.session_date ?? booking.booked_at;

  return (
    <div className="dashboard">
      <h1>My Bookings</h1>

      {loading && <p>Loading your bookings...</p>}
      {error && <p className="error">{error}</p>}

      {!loading && bookings.length === 0 && (
        <div className="empty-state">
          <p>You haven't booked any sessions yet.</p>
          <Link to="/" className="btn-primary">
            Browse Sessions
          </Link>
        </div>
      )}

      <div className="booking-list">
        {bookings.map((booking) => (
          <div
            key={booking.id}
            className={`booking-card status-${booking.status}`}
          >
            <div className="booking-info">
              <h3>
                <Link to={`/sessions/${getSessionId(booking)}`}>
                  {getSessionTitle(booking)}
                </Link>
              </h3>

              <p>
                📅{" "}
                {getSessionDate(booking)
                  ? new Date(getSessionDate(booking)).toLocaleString()
                  : "No date"}
              </p>

              <p>💰 ${getSessionPrice(booking)}</p>
            </div>

            <div className="booking-actions">
              <span className={`badge ${booking.status}`}>
                {booking.status}
              </span>

              {booking.status === "confirmed" && (
                <button
                  className="btn-danger"
                  onClick={() => handleCancel(booking.id)}
                >
                  Cancel
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}