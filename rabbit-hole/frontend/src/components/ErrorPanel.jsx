// Owner: Member 1. Props: { error: {code, message, retryable} | null, onRetry: (() => void) | null, onHome() }

export default function ErrorPanel({ error, onRetry, onHome }) {
  const message = error?.message ?? 'Something went wrong. Please try again.'
  const canRetry = Boolean(onRetry) && (error?.retryable ?? true)

  return (
    <section className="reveal mx-auto max-w-3xl px-5 py-20 sm:px-10" role="alert">
      <p className="font-mono text-xs text-dust">Archive / Error</p>
      <h1 className="mt-4 font-display text-5xl font-light sm:text-7xl">The file is stuck</h1>
      <p className="mt-6 max-w-lg font-mono text-sm leading-6">{message}</p>
      {error?.code && <p className="mt-2 font-mono text-xs text-dust">Error code: {error.code}</p>}
      <div className="mt-8 flex flex-wrap gap-4">
        {canRetry && (
          <button type="button" className="pill" onClick={onRetry}>
            Try again
          </button>
        )}
        <button type="button" className="pill pill-outline" onClick={onHome}>
          Back to start
        </button>
      </div>
    </section>
  )
}
