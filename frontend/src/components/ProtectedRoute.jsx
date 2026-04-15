import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ requiredRole }) {
  const { user, loading } = useAuth()

  if (loading) return <div style={{ padding: '2rem' }}>Loading...</div>

  if (!user) return <Navigate to="/login" replace />

  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet /> // ✅ THIS is the fix
}