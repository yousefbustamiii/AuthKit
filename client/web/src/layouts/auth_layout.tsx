import { Outlet } from 'react-router-dom'

export function AuthLayout() {
  return (
    <div className="dark flex min-h-screen flex-col items-center justify-center bg-background px-4 py-12">
      <div className="w-full max-w-[400px]">
        <Outlet />
      </div>
    </div>
  )
}
