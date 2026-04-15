import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../utils/api";

export default function ProfilePage() {
  const { user, setUser } = useAuth();
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", role: "" });
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [becomingCreator, setBecomingCreator] = useState(false);

  useEffect(() => {
    api.get("/auth/profile/")
      .then((res) => {
        const { first_name, last_name, email, role } = res.data;
        setForm({ first_name, last_name, email, role });
      })
      .catch(() => setError("Failed to load profile."));
  }, []);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleBecomeCreator = async () => {
    setBecomingCreator(true);
    setError(null);
    try {
      const res = await api.post("/auth/become-creator/");
      setForm((prev) => ({ ...prev, role: res.data.user.role }));
      setUser(res.data.user);
      setSuccess(true);
      setTimeout(() => {
        window.location.href = "/creator";
      }, 1000);
    } catch (err) {
      setError(err.response?.data?.message || "Failed to become creator.");
    } finally {
      setBecomingCreator(false);
    }
  };

  const handleBecomeUser = async () => {
    setBecomingCreator(true);
    setError(null);
    try {
      const res = await api.post("/auth/become-user/");
      setForm((prev) => ({ ...prev, role: res.data.user.role }));
      setUser(res.data.user);
      setSuccess(true);
      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 1000);
    } catch (err) {
      setError(err.response?.data?.message || "Failed to switch to user.");
    } finally {
      setBecomingCreator(false);
    }
  };

  const handleSubmit = async () => {
    setSaving(true);
    setSuccess(false);
    setError(null);
    try {
      const res = await api.patch("/auth/profile/", {
        first_name: form.first_name,
        last_name: form.last_name,
      });
      setUser((prev) => ({ ...prev, ...res.data }));
      setSuccess(true);
    } catch {
      setError("Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="profile-page">
      <h1>My Profile</h1>

      {error && <p className="error">{error}</p>}
      {success && <p className="success">Profile updated successfully!</p>}

      <div className="profile-card">
        <div className="avatar">
          {form.first_name?.[0]?.toUpperCase() ?? user?.email?.[0]?.toUpperCase() ?? "?"}
        </div>

        <div className="form-group">
          <label>First Name</label>
          <input
            name="first_name"
            value={form.first_name}
            onChange={handleChange}
            placeholder="First name"
          />
        </div>

        <div className="form-group">
          <label>Last Name</label>
          <input
            name="last_name"
            value={form.last_name}
            onChange={handleChange}
            placeholder="Last name"
          />
        </div>

        <div className="form-group">
          <label>Email</label>
          <input value={form.email} disabled />
        </div>

        <div className="form-group">
          <label>Role</label>
          <input value={form.role} disabled />
        </div>

        <button className="btn-primary" onClick={handleSubmit} disabled={saving}>
          {saving ? "Saving..." : "Save Changes"}
        </button>

        {form.role !== "creator" ? (
          <button 
            className="btn-secondary" 
            onClick={handleBecomeCreator} 
            disabled={becomingCreator}
            style={{ marginLeft: "10px" }}
          >
            {becomingCreator ? "Enabling..." : "Become a Creator"}
          </button>
        ) : (
          <button 
            className="btn-secondary" 
            onClick={handleBecomeUser} 
            disabled={becomingCreator}
            style={{ marginLeft: "10px" }}
          >
            {becomingCreator ? "Switching..." : "Switch to User"}
          </button>
        )}
      </div>
    </div>
  );
}