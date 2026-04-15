import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../utils/api";

const EMPTY_FORM = {
  title: "",
  description: "",
  price: "",
  date: "",
};

export default function CreatorDashboard() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [editId, setEditId] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [sessionToUpload, setSessionToUpload] = useState(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = () => {
    api.get("/sessions/")
      .then((res) => setSessions(res.data.results ?? res.data))
      .catch(() => setError("Failed to load your sessions."))
      .finally(() => setLoading(false));
  };

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)) {
        alert('Please upload a valid image (JPEG, PNG, GIF, WebP)');
        return;
      }
      // Validate file size (5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('Image must be smaller than 5MB');
        return;
      }
      setSelectedImage(file);
    }
  };

  const uploadImage = async (sessionId) => {
    if (!selectedImage) return;
    
    setUploadingImage(true);
    const formData = new FormData();
    formData.append('image', selectedImage);

    try {
      const res = await api.post(`/sessions/${sessionId}/upload_image/`, formData);
      
      // Update session with new image URL
      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId ? { ...s, cover_image: res.data.url } : s
        )
      );
      
      setSelectedImage(null);
      alert('Image uploaded successfully!');
    } catch (err) {
      console.error('Upload error:', err);
      alert(err.response?.data?.error ?? 'Failed to upload image');
    } finally {
      setUploadingImage(false);
    }
  };

  const handleSubmit = async () => {
    setSaving(true);
    try {
      if (editId) {
        const res = await api.put(`/sessions/${editId}/`, form);
        setSessions((prev) => prev.map((s) => s.id === editId ? res.data : s));
        setSessionToUpload(res.data.id);
      } else {
        const res = await api.post("/sessions/", form);
        setSessions((prev) => [res.data, ...prev]);
        setSessionToUpload(res.data.id);
      }
      setForm(EMPTY_FORM);
      setShowForm(false);
      setEditId(null);
      setSelectedImage(null);
    } catch (err) {
      alert(err.response?.data?.detail ?? "Failed to save session.");
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (session) => {
    setForm({
      title: session.title,
      description: session.description,
      price: session.price,
      date: session.date.slice(0, 16), // for datetime-local input
    });
    setEditId(session.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!confirm("Delete this session? This cannot be undone.")) return;
    try {
      await api.delete(`/sessions/${id}/`);
      setSessions((prev) => prev.filter((s) => s.id !== id));
    } catch {
      alert("Could not delete session.");
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>My Sessions</h1>
        <button className="btn-primary" onClick={() => { setShowForm(true); setEditId(null); setForm(EMPTY_FORM); }}>
          + New Session
        </button>
      </div>

      {showForm && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>{editId ? "Edit Session" : "Create Session"}</h2>
            <input
              name="title"
              placeholder="Title"
              value={form.title}
              onChange={handleChange}
            />
            <textarea
              name="description"
              placeholder="Description"
              value={form.description}
              onChange={handleChange}
              rows={4}
            />
            <input
              name="price"
              type="number"
              placeholder="Price (USD)"
              value={form.price}
              onChange={handleChange}
            />
            <input
              name="date"
              type="datetime-local"
              value={form.date}
              onChange={handleChange}
            />
            
            <div className="image-upload-section">
              <label htmlFor="image-input">Cover Image</label>
              <input
                id="image-input"
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                disabled={uploadingImage}
              />
              {selectedImage && (
                <p style={{ fontSize: '0.9em', color: '#666' }}>
                  📸 {selectedImage.name} selected
                </p>
              )}
            </div>

            <div className="modal-actions">
              <button className="btn-primary" onClick={handleSubmit} disabled={saving}>
                {saving ? "Saving..." : editId ? "Update" : "Create"}
              </button>
              <button className="btn-secondary" onClick={() => { setShowForm(false); setSelectedImage(null); }}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {sessionToUpload && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Upload Cover Image</h2>
            <p>Add a cover image to your session (optional)</p>
            
            <div className="image-upload-section">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                disabled={uploadingImage}
              />
              {selectedImage && (
                <p style={{ fontSize: '0.9em', color: '#666' }}>
                  📸 {selectedImage.name} selected
                </p>
              )}
            </div>

            <div className="modal-actions">
              {selectedImage && (
                <button className="btn-primary" onClick={() => uploadImage(sessionToUpload)} disabled={uploadingImage}>
                  {uploadingImage ? "Uploading..." : "Upload Image"}
                </button>
              )}
              <button className="btn-secondary" onClick={() => { setSessionToUpload(null); setSelectedImage(null); }}>
                {selectedImage ? "Skip" : "Done"}
              </button>
            </div>
          </div>
        </div>
      )}

      {loading && <p>Loading your sessions...</p>}
      {error && <p className="error">{error}</p>}

      {!loading && sessions.length === 0 && (
        <div className="empty-state">
          <p>You haven't created any sessions yet.</p>
        </div>
      )}

      <div className="session-grid">
        {sessions.map((session) => (
          <div key={session.id} className="session-card creator-card">
            {console.log("img path:", session.cover_image)}
            {session.cover_image && (
              <div className="session-image">
                <img src={`http://localhost:8000/api/sessions/${session.id}/image/`} />
              </div>
            )}
            <h3>{session.title}</h3>
            <p>{session.description?.slice(0, 80)}...</p>
            <div className="session-meta">
              <span>💰 ${session.price}</span>
              <span>📅 {new Date(session.date).toLocaleDateString()}</span>
            </div>
            <div className="card-actions">
              <Link to={`/sessions/${session.id}`} className="btn-secondary">View</Link>
              <button className="btn-secondary" onClick={() => handleEdit(session)}>Edit</button>
              <button className="btn-danger" onClick={() => handleDelete(session.id)}>Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}