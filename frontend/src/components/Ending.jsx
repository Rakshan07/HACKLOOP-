// Owner: Member 1.
// Props: { article, ending, history, onReplaySame(), onNew() }

export default function Ending({ article, ending, history, onReplaySame, onNew }) {
  return (
    <section className="reveal mx-auto max-w-6xl px-5 pb-24 pt-8 sm:px-10">
      <p className="font-mono text-xs text-dust">Archive / {article.title} / File closed</p>
      <h1 className="mt-4 font-display text-6xl font-light leading-[0.95] sm:text-8xl">The end</h1>
      <h2 className="mt-3 font-display text-3xl italic text-bone/90 sm:text-4xl">{ending.title}</h2>

      <div className="mt-10 grid gap-10 lg:grid-cols-[1fr_360px]">
        <div>
          <p className="max-w-2xl font-display text-3xl leading-snug sm:text-4xl">{ending.narrative}</p>

          <h3 className="mt-12 font-mono text-xs text-dust">Your path</h3>
          <ol className="mt-3 max-w-xl space-y-2 border-l border-white/20 pl-4 font-mono text-sm leading-6">
            {history.map((h) => (
              <li key={h.turn}>
                <span className="text-dust">Turn {h.turn}:</span> {h.choiceText}
              </li>
            ))}
          </ol>
        </div>

        <aside className="space-y-8">
          <div className="callout font-mono text-xs leading-5">
            <p className="text-sm font-medium">What was real</p>
            <p className="mt-2">{ending.lesson}</p>
          </div>

          <div className="paper bg-card-manila p-5 font-mono text-xs leading-5">
            <p className="font-display text-2xl">{article.title}</p>
            <p className="mt-2">{article.extract}</p>
            <p className="mt-4 border-t border-ink/30 pt-3">
              Text from Wikipedia, licensed{' '}
              <a className="underline" href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noreferrer">
                CC BY-SA 4.0
              </a>
              .{' '}
              <a className="underline" href={article.url} target="_blank" rel="noreferrer">
                Read the original article
              </a>
            </p>
          </div>
        </aside>
      </div>

      <div className="mt-12 flex flex-wrap items-center gap-4">
        <button type="button" className="pill" onClick={onReplaySame}>
          Play again
        </button>
        <button type="button" className="pill pill-outline" onClick={onNew}>
          Start another adventure
        </button>
        <span className="font-mono text-xs text-dust">Play again reopens the same article.</span>
      </div>
    </section>
  )
}
