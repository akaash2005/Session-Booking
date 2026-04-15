import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import RazorpayCheckout from "../components/StripeCheckout";
import api from "../utils/api";

export default function SessionDetailPage() {
  const { id } = useParams();
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);
  const [booked, setBooked] = useState(false);
  const [bookingId, setBookingId] = useState(null);
  const [showPayment, setShowPayment] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get(`/sessions/${id}/`)
      .then((res) => setSession(res.data))
      .catch(() => setError("Session not found."))
      .finally(() => setLoading(false));
  }, [id]);

  const handleBook = async () => {
    if (authLoading) return;

    if (!user) {
      navigate("/login");
      return;
    }

    setBooking(true);
    setError(null);

    try {
      const res = await api.post("/bookings/", {
        session_id: Number(id),
      });
      
      setBookingId(res.data.id);
      
      // If session has a price, show payment form
      if (session.price > 0) {
        setShowPayment(true);
      } else {
        // Free session - mark as booked immediately
        setBooked(true);
      }
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
        err.response?.data?.error ||
        "Booking failed."
      );
    } finally {
      setBooking(false);
    }
  };

  const handlePaymentSuccess = () => {
    setShowPayment(false);
    setBooked(true);
  };

  const handlePaymentCancel = () => {
    setShowPayment(false);
  };

  if (loading) return <div className="center">Loading...</div>;
  if (error && !booked) return <div className="center error">{error}</div>;

  return (
    <div className="session-detail">
      <button onClick={() => navigate(-1)}>← Back</button>

      <h1>{session.title}</h1>
      <p>Hosted by {session.creator_name || "Unknown"}</p>

      <p>📅 {new Date(session.date).toLocaleString()}</p>
      <p>💰 ${session.price}</p>

      {showPayment && bookingId ? (
        <RazorpayCheckout 
          bookingId={bookingId}
          amount={session.price}
          userName={user?.full_name || user?.username || "User"}
          userEmail={user?.email || ""}
          onSuccess={handlePaymentSuccess}
          onCancel={handlePaymentCancel}
        />
      ) : booked ? (
        <p>✅ Booked! <a href="/dashboard">Go to dashboard</a></p>
      ) : (
        <button onClick={handleBook} disabled={booking}>
          {booking ? "Booking..." : "Book Now"}
        </button>
      )}
    </div>
  );
}