// Owner: Member 2. Connects the API client to the reducer and exposes simple actions to the UI.
import { useCallback, useEffect, useReducer, useRef } from 'react'
import * as api from '../api/client'
import { initialState, reducer } from '../state/gameReducer'

const STORAGE_KEY = 'rabbit-hole-game-id'

const remember = (id) => {
  try {
    sessionStorage.setItem(STORAGE_KEY, id)
  } catch {
    // storage can be blocked; refresh then simply starts over
  }
}

const forget = () => {
  try {
    sessionStorage.removeItem(STORAGE_KEY)
  } catch {
    // ignore
  }
}

const recall = () => {
  try {
    return sessionStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}

function toUiError(err) {
  if (err instanceof api.ApiError) {
    return { code: err.code, message: err.message, retryable: err.retryable }
  }
  return { code: 'UNKNOWN', message: 'Something went wrong. Please try again.', retryable: true }
}

export function useGame() {
  const [state, dispatch] = useReducer(reducer, initialState)
  const stateRef = useRef(state)
  useEffect(() => {
    stateRef.current = state
  }, [state])

  const busy = useRef(false) // blocks double clicks and duplicate requests
  const epoch = useRef(0) // bumps when the player goes home, so late replies are ignored

  const run = useCallback(async (action) => {
    if (busy.current) return
    busy.current = true
    const mine = epoch.current
    const emit = (a) => {
      if (mine === epoch.current) dispatch(a)
    }

    let step = action // what to repeat if this fails
    try {
      let current = action
      if (current.kind === 'new' || current.kind === 'same' || current.kind === 'resume') {
        emit({ type: 'FETCH_START' })
        const game =
          current.kind === 'new'
            ? await api.createGame()
            : current.kind === 'same'
            ? await api.restartGame(current.gameId)
            : await api.getGame(current.gameId)
        remember(game.gameId)
        emit({ type: 'GAME_LOADED', game })
        current = game.status === 'ARTICLE_READY' ? { kind: 'begin', gameId: game.gameId } : null
      }

      if (current?.kind === 'begin') {
        step = current
        emit({ type: 'GENERATE_START' })
        emit({ type: 'GAME_LOADED', game: await api.startGame(current.gameId) })
      } else if (current?.kind === 'choose') {
        step = current
        emit({ type: 'GENERATE_START' })
        const game = await api.sendChoice(current.gameId, current.turn, current.choiceId)
        emit({ type: 'GAME_LOADED', game })
      }
    } catch (err) {
      if (action.kind === 'resume' && err.code === 'GAME_NOT_FOUND') {
        forget() // the saved game expired: quietly go back to the start
        emit({ type: 'RESET' })
      } else if ((err.code === 'STALE_TURN' || err.code === 'GAME_NOT_PLAYING') && step.gameId) {
        try {
          // The server is ahead of us (for example a second tab): just show the real state.
          emit({ type: 'GAME_LOADED', game: await api.getGame(step.gameId) })
        } catch (inner) {
          emit({ type: 'FAIL', error: toUiError(inner), retry: step })
        }
      } else {
        emit({ type: 'FAIL', error: toUiError(err), retry: step })
      }
    } finally {
      if (mine === epoch.current) busy.current = false
    }
  }, [])

  // Predictable refresh: if a game id is saved, ask the server where we were.
  useEffect(() => {
    const id = recall()
    if (id) run({ kind: 'resume', gameId: id })
  }, [run])

  const startNew = useCallback(() => run({ kind: 'new' }), [run])

  const playSame = useCallback(() => {
    const id = stateRef.current.gameId
    if (id) run({ kind: 'same', gameId: id })
  }, [run])

  const choose = useCallback(
    (choiceId) => {
      const s = stateRef.current
      if (s.status !== 'PLAYING' || !s.scene) return // ignore clicks while busy or finished
      if (!s.scene.choices.some((c) => c.id === choiceId)) return
      run({ kind: 'choose', gameId: s.gameId, turn: s.turn, choiceId })
    },
    [run],
  )

  const retry = useCallback(() => {
    const action = stateRef.current.retry
    if (action) run(action)
  }, [run])

  const goHome = useCallback(() => {
    epoch.current += 1
    busy.current = false
    forget()
    dispatch({ type: 'RESET' })
  }, [])

  return { state, startNew, playSame, choose, retry, goHome }
}
