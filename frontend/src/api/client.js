// Owner: Member 2. The ONLY file that talks to the backend.
// Every function returns a "GameView" (see docs/CONTRACT.md) or throws an ApiError.

const BASE = import.meta.env.VITE_API_BASE ?? '/api'
const TIMEOUT_MS = 70000 // a little longer than the backend's Gemma timeout

export class ApiError extends Error {
  constructor({ code, message, retryable, status }) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.retryable = retryable
    this.status = status
  }
}

async function request(path, { method = 'GET', body } = {}) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS)
  let response
  try {
    response = await fetch(`${BASE}${path}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    })
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new ApiError({
        code: 'CLIENT_TIMEOUT',
        message: 'The narrator is taking too long. Please try again.',
        retryable: true,
      })
    }
    throw new ApiError({
      code: 'NETWORK',
      message: 'Cannot reach the server. Check your connection and try again.',
      retryable: true,
    })
  } finally {
    clearTimeout(timer)
  }

  let data = null
  try {
    data = await response.json()
  } catch {
    // body was not JSON; handled below
  }

  if (!response.ok) {
    const e = data?.error
    throw new ApiError({
      code: e?.code ?? 'UNKNOWN',
      message: e?.message ?? 'Something went wrong. Please try again.',
      retryable: e?.retryable ?? response.status >= 500,
      status: response.status,
    })
  }
  return data
}

export const createGame = () => request('/games', { method: 'POST' })
export const getGame = (gameId) => request(`/games/${gameId}`)
export const startGame = (gameId) => request(`/games/${gameId}/start`, { method: 'POST' })
export const restartGame = (gameId) => request(`/games/${gameId}/restart`, { method: 'POST' })
export const sendChoice = (gameId, turn, choiceId) =>
  request(`/games/${gameId}/choices`, { method: 'POST', body: { turn, choiceId } })
