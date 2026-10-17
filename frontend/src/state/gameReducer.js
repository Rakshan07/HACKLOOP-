// Owner: Member 2. Pure state machine: easy to test, no side effects.
// IDLE -> FETCHING_ARTICLE -> GENERATING -> PLAYING -> (GENERATING -> PLAYING)* -> COMPLETED
// Any step can go to ERROR, which is recoverable through `retry`.

export const TOTAL_TURNS = 5

export const initialState = {
  status: 'IDLE',
  gameId: null,
  article: null,
  scene: null,
  ending: null,
  history: [],
  turn: 1,
  totalTurns: TOTAL_TURNS,
  error: null, // { code, message, retryable }
  retry: null, // the action to repeat when the player presses "Try again"
}

const STATUS_FROM_SERVER = {
  ARTICLE_READY: 'GENERATING', // article is ready, Gemma still has to write scene 1
  PLAYING: 'PLAYING',
  COMPLETED: 'COMPLETED',
}

export function reducer(state, action) {
  switch (action.type) {
    case 'FETCH_START':
      return { ...initialState, status: 'FETCHING_ARTICLE' }
    case 'GENERATE_START':
      return { ...state, status: 'GENERATING', error: null }
    case 'GAME_LOADED': {
      const g = action.game
      return {
        ...state,
        status: STATUS_FROM_SERVER[g.status] ?? 'ERROR',
        gameId: g.gameId,
        article: g.article,
        scene: g.scene,
        ending: g.ending,
        history: g.history ?? [],
        turn: g.turn,
        totalTurns: g.totalTurns ?? TOTAL_TURNS,
        error: null,
        retry: null,
      }
    }
    case 'FAIL':
      return { ...state, status: 'ERROR', error: action.error, retry: action.retry ?? null }
    case 'RESET':
      return initialState
    default:
      return state
  }
}
