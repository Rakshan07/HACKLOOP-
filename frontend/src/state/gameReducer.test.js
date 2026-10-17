// Owner: Member 2. Run with: npm test
import { describe, expect, it } from 'vitest'
import { initialState, reducer } from './gameReducer'

const article = { title: 'Test', extract: 'x', url: 'https://en.wikipedia.org/wiki/Test' }
const scene = (turn) => ({
  turn,
  narrative: 'n',
  fact: 'f',
  choices: [
    { id: 'A', text: 'a' },
    { id: 'B', text: 'b' },
    { id: 'C', text: 'c' },
  ],
})
const game = (over) => ({
  gameId: 'g1',
  status: 'PLAYING',
  turn: 1,
  totalTurns: 5,
  article,
  scene: scene(1),
  ending: null,
  history: [],
  ...over,
})

describe('game state machine', () => {
  it('starts idle', () => {
    expect(initialState.status).toBe('IDLE')
  })

  it('follows IDLE -> FETCHING_ARTICLE -> GENERATING -> PLAYING', () => {
    let s = reducer(initialState, { type: 'FETCH_START' })
    expect(s.status).toBe('FETCHING_ARTICLE')
    s = reducer(s, { type: 'GAME_LOADED', game: game({ status: 'ARTICLE_READY', scene: null }) })
    expect(s.status).toBe('GENERATING')
    expect(s.article.title).toBe('Test')
    s = reducer(s, { type: 'GAME_LOADED', game: game() })
    expect(s.status).toBe('PLAYING')
    expect(s.scene.choices).toHaveLength(3)
  })

  it('keeps the current scene visible while the next one is generated', () => {
    let s = reducer(initialState, { type: 'GAME_LOADED', game: game() })
    s = reducer(s, { type: 'GENERATE_START' })
    expect(s.status).toBe('GENERATING')
    expect(s.scene.turn).toBe(1)
  })

  it('advances turn by turn and completes with an ending', () => {
    let s = reducer(initialState, { type: 'GAME_LOADED', game: game({ turn: 5, scene: scene(5) }) })
    expect(s.turn).toBe(5)
    const done = game({
      status: 'COMPLETED',
      turn: 5,
      scene: null,
      ending: { title: 'T', narrative: 'n', lesson: 'l' },
      history: [1, 2, 3, 4, 5].map((t) => ({ turn: t, choiceId: 'A', choiceText: 'a' })),
    })
    s = reducer(s, { type: 'GAME_LOADED', game: done })
    expect(s.status).toBe('COMPLETED')
    expect(s.history).toHaveLength(5)
    expect(s.ending.title).toBe('T')
  })

  it('goes to ERROR with a retry action, and recovers on the next load', () => {
    const retry = { kind: 'choose', gameId: 'g1', turn: 1, choiceId: 'A' }
    let s = reducer(initialState, { type: 'GAME_LOADED', game: game() })
    s = reducer(s, { type: 'FAIL', error: { code: 'NETWORK', message: 'm', retryable: true }, retry })
    expect(s.status).toBe('ERROR')
    expect(s.retry).toEqual(retry)
    s = reducer(s, { type: 'GAME_LOADED', game: game({ turn: 2, scene: scene(2) }) })
    expect(s.status).toBe('PLAYING')
    expect(s.error).toBeNull()
    expect(s.retry).toBeNull()
  })

  it('RESET returns to the landing state and clears the old game', () => {
    let s = reducer(initialState, { type: 'GAME_LOADED', game: game() })
    s = reducer(s, { type: 'RESET' })
    expect(s).toEqual(initialState)
  })

  it('a new FETCH_START wipes the previous adventure (replay works without refresh)', () => {
    let s = reducer(initialState, {
      type: 'GAME_LOADED',
      game: game({ status: 'COMPLETED', ending: { title: 'T', narrative: 'n', lesson: 'l' }, scene: null }),
    })
    s = reducer(s, { type: 'FETCH_START' })
    expect(s.ending).toBeNull()
    expect(s.history).toEqual([])
    expect(s.status).toBe('FETCHING_ARTICLE')
  })

  it('ignores unknown actions', () => {
    const s = reducer(initialState, { type: 'NOPE' })
    expect(s).toBe(initialState)
  })
})
