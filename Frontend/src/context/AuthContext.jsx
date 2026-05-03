import { createContext, useContext, useState } from 'react'
import api from '../api/axios'

const AuthContext = createContext(null)

function decodePayload(token) {
  try {
    return JSON.parse(atob(token.split('.')[1]))
  } catch {
    return null
  }
}

function loadAuth() {
  const token = localStorage.getItem('access_token')
  if (!token) return null
  const payload = decodePayload(token)
  if (!payload || payload.exp * 1000 < Date.now()) {
    localStorage.removeItem('access_token')
    return null
  }
  return {
    token,
    role: payload.role,
    username: payload.username,
    userId: payload.user_id,
  }
}

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(loadAuth)

  async function login(username, password) {
    const { data } = await api.post('/api/auth/token/', { username, password })
    localStorage.setItem('access_token', data.access)
    const payload = decodePayload(data.access)
    const next = {
      token: data.access,
      role: payload.role,
      username: payload.username,
      userId: payload.user_id,
    }
    setAuth(next)
    return next
  }

  function logout() {
    localStorage.removeItem('access_token')
    setAuth(null)
  }

  return (
    <AuthContext.Provider value={{ auth, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
