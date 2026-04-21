import { useEffect, useState } from 'react'

interface ErrorAlertProps {
  message: string | null
}

function format_error(msg: string): string {
  if (msg.toLowerCase().includes('failed to fetch')) {
    return 'Unable to connect to our servers. Please check your connection.'
  }

  // Handle snake_case error codes (e.g. RATE_LIMIT_EXCEEDED -> Rate limit exceeded)
  if (/^[A-Z_]+$/.test(msg)) {
    return msg
      .toLowerCase()
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  return msg
}

export function ErrorAlert({ message }: ErrorAlertProps) {
  const [visible, set_visible] = useState(false)

  useEffect(() => {
    if (message) {
      set_visible(true)
      const timer = setTimeout(() => {
        set_visible(false)
      }, 5000)
      return () => clearTimeout(timer)
    } else {
      set_visible(false)
    }
  }, [message])

  if (!message || !visible) return null

  return (
    <div className="pt-1.5 animate-in fade-in slide-in-from-top-1 duration-200">
      <p className="text-[11px] font-medium text-destructive leading-relaxed text-center">
        {format_error(message)}
      </p>
    </div>
  )
}
