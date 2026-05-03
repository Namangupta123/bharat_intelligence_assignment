import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'

const STATUS_COLORS = {
  PENDING: 'bg-yellow-100 text-yellow-800',
  APPROVED: 'bg-green-100 text-green-800',
  REJECTED: 'bg-red-100 text-red-800',
}

export default function ManagerView() {
  const { auth, logout } = useAuth()
  const [tasks, setTasks] = useState([])
  const [updating, setUpdating] = useState(null)
  const [fetchError, setFetchError] = useState('')
  const [updateError, setUpdateError] = useState('')
  const [profileForm, setProfileForm] = useState({ email: '', emailPassword: '', currentPassword: '', newPassword: '', confirmNewPassword: '' })
  const [profileError, setProfileError] = useState('')
  const [profileSuccess, setProfileSuccess] = useState('')
  const [profileLoading, setProfileLoading] = useState(false)

  const fetchTasks = useCallback(async () => {
    try {
      const { data } = await api.get('/api/tasks/assigned/')
      setTasks(data)
    } catch {
      setFetchError('Failed to load assigned tasks.')
    }
  }, [])

  useEffect(() => {
    fetchTasks()
  }, [fetchTasks])

  async function updateStatus(taskId, status) {
    setUpdating(taskId)
    setUpdateError('')
    try {
      await api.patch(`/api/tasks/${taskId}/status/`, { status })
      await fetchTasks()
    } catch (err) {
      setUpdateError(err.response?.data?.detail || 'Failed to update task status.')
    } finally {
      setUpdating(null)
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

  const pending = tasks.filter(t => t.status === 'PENDING')
  const decided = tasks.filter(t => t.status !== 'PENDING')

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
        {fetchError && (
          <p className="text-sm text-red-600 bg-red-50 border border-red-200 p-2 rounded-lg">
            {fetchError}
          </p>
        )}
        {updateError && (
          <p className="text-sm text-red-600 bg-red-50 border border-red-200 p-2 rounded-lg">
            {updateError}
          </p>
        )}
        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Pending Review ({pending.length})
          </h2>
          {pending.length === 0 ? (
            <p className="text-sm text-gray-500">No pending tasks.</p>
          ) : (
            <ul className="divide-y divide-gray-100">
              {pending.map(task => (
                <li key={task.id} className="py-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800">{task.title}</p>
                      {task.description && (
                        <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                          {task.description}
                        </p>
                      )}
                      <p className="text-xs text-gray-400 mt-1">
                        From: {task.created_by_username}
                      </p>
                    </div>
                    <div className="flex gap-2 shrink-0">
                      <button
                        onClick={() => updateStatus(task.id, 'APPROVED')}
                        disabled={updating === task.id}
                        className="bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => updateStatus(task.id, 'REJECTED')}
                        disabled={updating === task.id}
                        className="bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors"
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {decided.length > 0 && (
          <div className="bg-white rounded-2xl shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              Decided ({decided.length})
            </h2>
            <ul className="divide-y divide-gray-100">
              {decided.map(task => (
                <li key={task.id} className="py-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800">{task.title}</p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        From: {task.created_by_username}
                      </p>
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
          </div>
        )}

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
