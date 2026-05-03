import { useAuth } from './context/AuthContext'
import LoginPage from './components/LoginPage'
import UserView from './components/UserView'
import ManagerView from './components/ManagerView'
import AdminView from './components/AdminView'

export default function App() {
  const { auth } = useAuth()

  if (!auth) return <LoginPage />
  if (auth.role === 'USER') return <UserView />
  if (auth.role === 'MANAGER') return <ManagerView />
  if (auth.role === 'ADMIN') return <AdminView />

  return (
    <div className="p-8 text-red-600">
      Unknown role: {auth.role}. Please contact an administrator.
    </div>
  )
}
