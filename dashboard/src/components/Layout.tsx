import { Link, Outlet, useNavigate } from 'react-router-dom'

export default function Layout() {
  const navigate = useNavigate()

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-8">
            <h1 className="text-xl font-bold text-blue-600">Hospital Claim AI</h1>
            <div className="flex gap-4">
              <Link to="/" className="text-gray-600 hover:text-blue-600 font-medium">Dashboard</Link>
              <Link to="/claims" className="text-gray-600 hover:text-blue-600 font-medium">Claims</Link>
              <Link to="/reports" className="text-gray-600 hover:text-blue-600 font-medium">Reports</Link>
            </div>
          </div>
          <button onClick={logout} className="text-sm text-gray-500 hover:text-red-600">
            Logout
          </button>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-6 py-6">
        <Outlet />
      </main>
    </div>
  )
}
