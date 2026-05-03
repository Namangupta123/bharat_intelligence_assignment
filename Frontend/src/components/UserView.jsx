import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'

const STATUS_COLORS = {
  PENDING: 'bg-yellow-100 text-yellow-800',
  APPROVED: 'bg-green-100 text-green-800',
  REJECTED: 'bg-red-100 text-red-800',
}

export default function UserView() {
  const { auth, logout } = useAuth()
  const [tasks, setTasks] = useState([])
  const [managers, setManagers] = useState([])
  const [form, setForm] = useState({ title: '', description: '', assigned_manager: '' })
  const [error, setError] = useState('')
  const [fetchError, setFetchError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const [profileForm, setProfileForm] = useState({ email: '', emailPassword: '', currentPassword: '', newPassword: '', confirmNewPassword: '' })
  const [profileError, setProfileError] = useState('')
  const [profileSuccess, setProfileSuccess] = useState('')
  const [profileLoading, setProfileLoading] = useState(false)

  const fetchTasks = useCallback(async () => {
    try {
      const { data } = await api.get('/api/tasks/mine/')
      setTasks(data)
    } catch {
      setFetchError('Failed to load tasks.')
    }
  }, [])

  useEffect(() => {
    fetchTasks()
    api.get('/api/managers/').then(r => setManagers(r.data)).catch(() => {})
  }, [fetchTasks])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const payload = { title: form.title, description: form.description }
      if (form.assigned_manager) payload.assigned_manager = Number(form.assigned_manager)
      await api.post('/api/tasks/', payload)
      setForm({ title: '', description: '', assigned_manager: '' })
      setSuccess('Task submitted successfully.')
      fetchTasks()
    } catch (err) {
      const data = err.response?.data
      setError(data?.title?.[0] || data?.detail || 'Failed to create task.')
    } finally {
      setLoading(false)
    }
  }

  async function handleEmailUpdate(e) {
    e.preventDefault()
    setProfileError('')
    setProfileSuccess('')
    setProfileLoading(true)
    try {
      await api.patch('/api/profile/email/', { email: profileForm.email, current_password: profileForm.emailPassword })
      setProfileSuccess('Email updated successfully.')
      setProfileForm(f => ({ ...f, email: '', emailPassword: '' }))
    } catch (err) {
      const data = err.response?.data
      setProfileError(data?.email?.[0] || data?.current_password?.[0] || data?.detail || 'Failed to update email.')
    } finally {
      setProfileLoading(false)
    }
  }

  async function handlePasswordUpdate(e) {
    e.preventDefault()
    setProfileError('')
    setProfileSuccess('')
    setProfileLoading(true)
    try {
      await api.post('/api/profile/password/', {
        current_password: profileForm.currentPassword,
        new_password: profileForm.newPassword,
        confirm_new_password: profileForm.confirmNewPassword,
      })
      setProfileSuccess('Password updated successfully.')
      setProfileForm(f => ({ ...f, currentPassword: '', newPassword: '', confirmNewPassword: '' }))
    } catch (err) {
      const data = err.response?.data
      setProfileError(
        data?.current_password?.[0] ||
        data?.new_password?.[0] ||
        data?.confirm_new_password?.[0] ||
        data?.non_field_errors?.[0] ||
        data?.detail ||
        'Failed to update password.'
      )
    } finally {
      setProfileLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-800">Task Manager</h1>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">Hi, {auth.username}</span>
          <button
            onClick={logout}
            className="text-sm text-red-600 hover:underline"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-2xl mx-auto p-6 space-y-6">
        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Submit a New Task</h2>

          {error && (
            <p className="mb-3 text-sm text-red-600 bg-red-50 border border-red-200 p-2 rounded-lg">
              {error}
            </p>
          )}
          {success && (
            <p className="mb-3 text-sm text-green-700 bg-green-50 border border-green-200 p-2 rounded-lg">
              {success}
            </p>
          )}

          <form onSubmit={handleSubmit} className="space-y-3">
            <input
              type="text"
              placeholder="Task title *"
              aria-label="Task title"
              value={form.title}
              onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <textarea
              placeholder="Description (optional)"
              aria-label="Task description"
              value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
            {managers.length > 0 && (
              <select
                value={form.assigned_manager}
                onChange={e => setForm(f => ({ ...f, assigned_manager: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">No manager assigned</option>
                {managers.map(m => (
                  <option key={m.id} value={m.id}>{m.username}</option>
                ))}
              </select>
            )}
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-semibold px-6 py-2 rounded-lg transition-colors"
            >
              {loading ? 'Submitting…' : 'Submit Task'}
            </button>
          </form>
        </div>

        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            My Tasks ({tasks.length})
          </h2>
          {fetchError && (
            <p className="text-sm text-red-600 bg-red-50 border border-red-200 p-2 rounded-lg mb-3">
              {fetchError}
            </p>
          )}
          {tasks.length === 0 ? (
            <p className="text-sm text-gray-500">No tasks yet. Submit one above.</p>
          ) : (
            <ul className="divide-y divide-gray-100">
              {tasks.map(task => (
                <li key={task.id} className="py-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">
                        {task.title}
                      </p>
                      {task.description && (
                        <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                          {task.description}
                        </p>
                      )}
                      {task.assigned_manager_username && (
                        <p className="text-xs text-gray-400 mt-0.5">
                          Manager: {task.assigned_manager_username}
                        </p>
                      )}
                    </div>
                    <span
                      className={`text-xs font-semibold px-2 py-1 rounded-full whitespace-nowrap ${STATUS_COLORS[task.status]}`}
                    >
                      {task.status}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Profile Settings</h2>

          {profileError && (
            <p className="mb-3 text-sm text-red-600 bg-red-50 border border-red-200 p-2 rounded-lg">
              {profileError}
            </p>
          )}
          {profileSuccess && (
            <p className="mb-3 text-sm text-green-700 bg-green-50 border border-green-200 p-2 rounded-lg">
              {profileSuccess}
            </p>
          )}

          <form onSubmit={handleEmailUpdate} className="space-y-3 mb-6">
            <p className="text-sm font-medium text-gray-700">Change Email</p>
            <input
              type="email"
              placeholder="New email address"
              aria-label="New email address"
              value={profileForm.email}
              onChange={e => setProfileForm(f => ({ ...f, email: e.target.value }))}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="password"
              placeholder="Confirm with your current password"
              aria-label="Current password for email change"
              value={profileForm.emailPassword}
              onChange={e => setProfileForm(f => ({ ...f, emailPassword: e.target.value }))}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={profileLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-semibold px-6 py-2 rounded-lg transition-colors"
            >
              {profileLoading ? 'Saving…' : 'Update Email'}
            </button>
          </form>

          <hr className="border-gray-100 mb-6" />

          <form onSubmit={handlePasswordUpdate} className="space-y-3">
            <p className="text-sm font-medium text-gray-700">Change Password</p>
            <input
              type="password"
              placeholder="Current password"
              aria-label="Current password"
              value={profileForm.currentPassword}
              onChange={e => setProfileForm(f => ({ ...f, currentPassword: e.target.value }))}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="password"
              placeholder="New password"
              aria-label="New password"
              value={profileForm.newPassword}
              onChange={e => setProfileForm(f => ({ ...f, newPassword: e.target.value }))}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="password"
              placeholder="Confirm new password"
              aria-label="Confirm new password"
              value={profileForm.confirmNewPassword}
              onChange={e => setProfileForm(f => ({ ...f, confirmNewPassword: e.target.value }))}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={profileLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-semibold px-6 py-2 rounded-lg transition-colors"
            >
              {profileLoading ? 'Saving…' : 'Update Password'}
            </button>
          </form>
        </div>
      </main>
    </div>
  )
}
