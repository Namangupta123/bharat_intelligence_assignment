import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'

const STATUS_COLORS = {
  PENDING: 'bg-yellow-100 text-yellow-800',
  APPROVED: 'bg-green-100 text-green-800',
  REJECTED: 'bg-red-100 text-red-800',
}

const ROLE_COLORS = {
  ADMIN: 'bg-purple-100 text-purple-800',
  MANAGER: 'bg-blue-100 text-blue-800',
  USER: 'bg-gray-100 text-gray-700',
}

export default function AdminView() {
  const { auth, logout } = useAuth()
  const [overview, setOverview] = useState(null)
  const [users, setUsers] = useState([])
  const [tasks, setTasks] = useState([])
  const [initialLoad, setInitialLoad] = useState(true)
  const [fetchError, setFetchError] = useState('')
  const [inviteForm, setInviteForm] = useState({ email: '', role: 'USER' })
  const [inviteError, setInviteError] = useState('')
  const [inviteSuccess, setInviteSuccess] = useState('')
  const [inviteLoading, setInviteLoading] = useState(false)

  useEffect(() => {
    Promise.allSettled([
      api.get('/api/admin/overview/').then(r => setOverview(r.data)).catch(() => setFetchError('Failed to load overview.')),
      api.get('/api/admin/users/').then(r => setUsers(r.data)).catch(() => setFetchError('Failed to load users.')),
      api.get('/api/admin/tasks/').then(r => setTasks(r.data)).catch(() => setFetchError('Failed to load tasks.')),
    ]).finally(() => setInitialLoad(false))
  }, [])

  async function handleInvite(e) {
    e.preventDefault()
    setInviteError('')
    setInviteSuccess('')
    setInviteLoading(true)
    try {
      const { data } = await api.post('/api/admin/invite/', {
        email: inviteForm.email,
        role: inviteForm.role,
      })
      setInviteSuccess(`Invited ${data.username} as ${data.role}. A welcome email has been sent.`)
      setInviteForm({ email: '', role: 'USER' })
      api.get('/api/admin/users/').then(r => setUsers(r.data)).catch(() => {})
    } catch (err) {
      const data = err.response?.data
      setInviteError(data?.email?.[0] || data?.role?.[0] || data?.detail || 'Failed to send invitation.')
    } finally {
      setInviteLoading(false)
    }
  }

  const stats = overview
    ? [
        { label: 'Total Users', value: overview.total_users },
        { label: 'Total Tasks', value: overview.total_tasks },
        { label: 'Pending', value: overview.tasks_by_status.PENDING },
        { label: 'Approved', value: overview.tasks_by_status.APPROVED },
      ]
    : []

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-800">Task Manager — Admin</h1>
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

      <main className="max-w-5xl mx-auto p-6 space-y-6">
        {fetchError && (
          <p className="text-sm text-red-600 bg-red-50 border border-red-200 p-2 rounded-lg">
            {fetchError}
          </p>
        )}
        {initialLoad ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 animate-pulse">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="bg-white rounded-2xl shadow p-4 text-center">
                <div className="h-8 w-12 bg-gray-200 rounded mx-auto mb-2" />
                <div className="h-2.5 w-20 bg-gray-200 rounded mx-auto" />
              </div>
            ))}
          </div>
        ) : stats.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {stats.map(stat => (
              <div
                key={stat.label}
                className="bg-white rounded-2xl shadow p-4 text-center"
              >
                <p className="text-3xl font-bold text-gray-800">{stat.value}</p>
                <p className="text-xs text-gray-500 mt-1">{stat.label}</p>
              </div>
            ))}
          </div>
        )}

        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Invite User</h2>

          {inviteError && (
            <p className="mb-3 text-sm text-red-600 bg-red-50 border border-red-200 p-2 rounded-lg">
              {inviteError}
            </p>
          )}
          {inviteSuccess && (
            <p className="mb-3 text-sm text-green-700 bg-green-50 border border-green-200 p-2 rounded-lg">
              {inviteSuccess}
            </p>
          )}

          <form onSubmit={handleInvite} className="flex flex-col sm:flex-row gap-3 items-end">
            <div className="flex-1">
              <label className="block text-xs text-gray-500 mb-1">Email address</label>
              <input
                type="email"
                placeholder="user@example.com"
                aria-label="Invite email address"
                value={inviteForm.email}
                onChange={e => setInviteForm(f => ({ ...f, email: e.target.value }))}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Role</label>
              <select
                value={inviteForm.role}
                onChange={e => setInviteForm(f => ({ ...f, role: e.target.value }))}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="USER">User</option>
                <option value="MANAGER">Manager</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={inviteLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-semibold px-6 py-2 rounded-lg transition-colors whitespace-nowrap"
            >
              {inviteLoading ? 'Sending…' : 'Send Invite'}
            </button>
          </form>
        </div>

        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            All Users {!initialLoad && `(${users.length})`}
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-left text-xs text-gray-500 uppercase tracking-wider">
                  <th className="pb-2 pr-4">ID</th>
                  <th className="pb-2 pr-4">Username</th>
                  <th className="pb-2 pr-4">Email</th>
                  <th className="pb-2 pr-4">Role</th>
                  <th className="pb-2">Joined</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 animate-pulse">
                {initialLoad
                  ? [1, 2, 3, 4, 5].map(i => (
                      <tr key={i}>
                        {[1, 2, 3, 4, 5].map(j => (
                          <td key={j} className="py-3 pr-4">
                            <div className="h-3 bg-gray-200 rounded w-full" />
                          </td>
                        ))}
                      </tr>
                    ))
                  : users.map(u => (
                      <tr key={u.id} className="hover:bg-gray-50">
                        <td className="py-2 pr-4 text-gray-400 text-xs">{u.id}</td>
                        <td className="py-2 pr-4 font-medium text-gray-800">{u.username}</td>
                        <td className="py-2 pr-4 text-gray-600">{u.email || '—'}</td>
                        <td className="py-2 pr-4">
                          <span
                            className={`text-xs font-semibold px-2 py-0.5 rounded-full ${ROLE_COLORS[u.role]}`}
                          >
                            {u.role}
                          </span>
                        </td>
                        <td className="py-2 text-gray-500 text-xs">
                          {new Date(u.date_joined).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            All Tasks {!initialLoad && `(${tasks.length})`}
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-left text-xs text-gray-500 uppercase tracking-wider">
                  <th className="pb-2 pr-4">ID</th>
                  <th className="pb-2 pr-4">Title</th>
                  <th className="pb-2 pr-4">Status</th>
                  <th className="pb-2 pr-4">Created By</th>
                  <th className="pb-2 pr-4">Manager</th>
                  <th className="pb-2">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 animate-pulse">
                {initialLoad
                  ? [1, 2, 3, 4, 5].map(i => (
                      <tr key={i}>
                        {[1, 2, 3, 4, 5, 6].map(j => (
                          <td key={j} className="py-3 pr-4">
                            <div className="h-3 bg-gray-200 rounded w-full" />
                          </td>
                        ))}
                      </tr>
                    ))
                  : tasks.map(t => (
                      <tr key={t.id} className="hover:bg-gray-50">
                        <td className="py-2 pr-4 text-gray-400 text-xs">{t.id}</td>
                        <td className="py-2 pr-4 font-medium text-gray-800 max-w-xs truncate">
                          {t.title}
                        </td>
                        <td className="py-2 pr-4">
                          <span
                            className={`text-xs font-semibold px-2 py-0.5 rounded-full ${STATUS_COLORS[t.status]}`}
                          >
                            {t.status}
                          </span>
                        </td>
                        <td className="py-2 pr-4 text-gray-600">{t.created_by_username}</td>
                        <td className="py-2 pr-4 text-gray-600">
                          {t.assigned_manager_username || '—'}
                        </td>
                        <td className="py-2 text-gray-500 text-xs">
                          {new Date(t.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  )
}
