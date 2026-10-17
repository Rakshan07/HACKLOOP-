// Owner: Member 1. Renders each screen to HTML and checks what the player would see.
import { renderToString } from 'react-dom/server'
import { describe, expect, it } from 'vitest'
import Landing from './Landing'
import Loading from './Loading'
import Gameplay from './Gameplay'
import Ending from './Ending'
import ErrorPanel from './ErrorPanel'

const article = {
  title: 'Great Emu War',
  extract: 'A wildlife management operation in Western Australia in 1932.',
  url: 'https://en.wikipedia.org/wiki/Emu_War',
  thumbnailUrl: 'https://upload.wikimedia.org/emu.jpg',
}
const scene = {
  turn: 2,
  narrative: 'You crouch behind a fence as the birds approach.',
  fact: 'Soldiers used Lewis guns against the emus.',
  choices: [
    { id: 'A', text: 'Prepare an ambush' },
    { id: 'B', text: 'Study the emu movements' },
    { id: 'C', text: 'Attempt a ridiculous peace talk' },
  ],
}
// React's server renderer splits text with invisible <!-- --> markers; remove them before searching.
const render = (element) => renderToString(element).replace(/<!-- -->/g, '')
const noop = () => {}
const play = (over = {}) =>
  render(
    <Gameplay article={article} scene={scene} turn={2} totalTurns={5} history={[{ turn: 1, choiceId: 'A', choiceText: 'Load the truck' }]} busy={false} onChoose={noop} onHome={noop} {...over} />,
  )

describe('screens', () => {
  it('landing shows the brand and a working primary button', () => {
    const html = render(<Landing onStart={noop} />)
    expect(html).toContain('Rabbit Hole')
    expect(html).toMatch(/<button[^>]*>.*BORED/s)
    expect(html).not.toContain('disabled')
  })

  it('loading shows stage text and never a fake percentage', () => {
    const wiki = render(<Loading stage="FETCHING_ARTICLE" />)
    const gemma = render(<Loading stage="GENERATING" articleTitle="Great Emu War" />)
    expect(wiki).toContain('Opening a random drawer')
    expect(gemma).toContain('Gemma is reading the file')
    expect(gemma).toContain('Great Emu War')
    expect(wiki + gemma).not.toContain('%')
  })

  it('gameplay shows title, narrative, turn indicator and exactly three choice buttons', () => {
    const html = play()
    expect(html).toContain('Great Emu War')
    expect(html).toContain('You crouch behind a fence')
    expect(html).toContain('Turn 2 of 5')
    expect(html).toContain('Soldiers used Lewis guns')
    expect((html.match(/class="choice /g) ?? []).length).toBe(3)
    expect(html).toContain('Turn 1: Load the truck')
  })

  it('gameplay disables the choices and explains why while Gemma is busy', () => {
    const html = play({ busy: true })
    expect((html.match(/class="choice [^"]*"[^>]*disabled/g) ?? []).length).toBe(3)
    expect(html).toContain('Gemma is writing the next scene')
  })

  it('ending shows summary, Wikipedia attribution, link and both replay buttons', () => {
    const html = render(
      <Ending
        article={article}
        ending={{ title: 'The Last Stand', narrative: 'The emus won.', lesson: 'The operation failed in 1932.' }}
        history={[1, 2, 3, 4, 5].map((t) => ({ turn: t, choiceId: 'A', choiceText: `Decision ${t}` }))}
        onReplaySame={noop}
        onNew={noop}
      />,
    )
    expect(html).toContain('CC BY-SA 4.0')
    expect(html).toContain('href="https://en.wikipedia.org/wiki/Emu_War"')
    expect(html).toContain('Play again')
    expect(html).toContain('Start another adventure')
    for (let t = 1; t <= 5; t++) expect(html).toContain(`Decision ${t}`)
  })

  it('error panel offers retry only when the error is retryable', () => {
    const retryable = render(<ErrorPanel error={{ code: 'NETWORK', message: 'Cannot reach the server.', retryable: true }} onRetry={noop} onHome={noop} />)
    const fatal = render(<ErrorPanel error={{ code: 'GAME_NOT_FOUND', message: 'Expired.', retryable: false }} onRetry={noop} onHome={noop} />)
    expect(retryable).toContain('Try again')
    expect(retryable).toContain('Cannot reach the server.')
    expect(fatal).not.toContain('Try again')
    expect(fatal).toContain('Back to start')
    expect(retryable).toContain('role="alert"')
  })
})
