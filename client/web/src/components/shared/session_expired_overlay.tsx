import { useEffect, useState } from 'react'

export function SessionExpiredOverlay() {
  const [visible, set_visible] = useState(false)

  useEffect(() => {
    const on_expired = () => {
      set_visible(true)
      setTimeout(() => {
        window.location.href = '/login'
      }, 3000)
    }

    window.addEventListener('session-expired', on_expired)
    return () => window.removeEventListener('session-expired', on_expired)
  }, [])

  if (!visible) return null

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="rounded-xl bg-white px-10 py-8 text-center shadow-2xl">
        <p className="mb-2 text-lg font-semibold text-slate-900">Session Expired</p>
        <p className="text-sm text-slate-500">
          Your session has expired. Redirecting to login
        </p>
      </div>
    </div>
  )
}
