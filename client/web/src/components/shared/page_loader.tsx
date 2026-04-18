import { LoadingSpinner } from './loading_spinner'

export function PageLoader() {
  return (
    <div className="flex h-screen w-screen items-center justify-center bg-background">
      <LoadingSpinner size="lg" />
    </div>
  )
}
