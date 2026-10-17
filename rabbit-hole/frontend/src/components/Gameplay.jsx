// Owner: Member 1.
// Props: { article, scene, turn, totalTurns, history, busy, onChoose(choiceId), onHome() }
import { useEffect, useRef, useState } from 'react'

const CARD_STYLES = ['choice-blue', 'choice-manila', 'choice-rose']

export function TurnTracker({ turn, totalTurns }) {
  return (
    <ol className="flex gap-2" aria-label={`Turn ${turn} of ${totalTurns}`}>
      {Array.from({ length: totalTurns }, (_, i) => {
        const n = i + 1
        const state = n < turn ? 'done' : n === turn ? 'current' : 'todo'
        const cls =
          state === 'done'
            ? 'bg-signal text-ink'
            : state === 'current'
              ? 'text-signal ring-2 ring-signal'
              : 'text-dust ring-1 ring-white/25'
        return (
          <li
            key={n}
            aria-current={state === 'current' ? 'step' : undefined}
            className={`grid h-8 w-8 place-items-center rounded-full font-mono text-xs ${cls}`}
          >
            {n}
          </li>
        )
      })}
    </ol>
  )
}

export function ChoiceCard({ choice, index, disabled, onChoose }) {
  return (
    <li>
      <button
        type="button"
        className={`choice w-full ${CARD_STYLES[index % CARD_STYLES.length]}`}
        disabled={disabled}
        onClick={() => onChoose(choice.id)}
      >
        <span className="font-mono text-[11px] uppercase tracking-wide opacity-70">Option {choice.id}</span>
        <span className="text-[15px] leading-6">{choice.text}</span>
        <span className="mt-auto font-mono text-[11px] opacity-60">Press {index + 1}</span>
      </button>
    </li>
  )
}

export default function Gameplay({ article, scene, turn, totalTurns, history, busy, onChoose, onHome }) {
  const [confirming, setConfirming] = useState(false)
  const [imageOk, setImageOk] = useState(true)
  const stayRef = useRef(null)

  // Keys 1, 2, 3 pick a card (keyboard and desktop shortcut).
  useEffect(() => {
    if (busy || confirming) return undefined
    const onKey = (e) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return
      const index = ['1', '2', '3'].indexOf(e.key)
      if (index >= 0 && scene.choices[index]) onChoose(scene.choices[index].id)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [busy, confirming, scene, onChoose])

  useEffect(() => {
    if (confirming) stayRef.current?.focus()
  }, [confirming])

  return (
    <section className="mx-auto max-w-6xl px-5 pb-24 pt-8 sm:px-10" aria-busy={busy}>
      <p className="font-mono text-xs text-dust">
        Archive / {article.title} / Turn {turn} of {totalTurns}
      </p>

      <div className="mt-4 flex items-start justify-between gap-4">
        <h1 className="font-display text-5xl font-light leading-[0.95] sm:text-7xl">{article.title}</h1>
        <button
          type="button"
          className="close-dot shrink-0"
          aria-label="Leave this adventure"
          onClick={() => setConfirming(true)}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" aria-hidden="true">
            <path d="M5 5l14 14M19 5 5 19" strokeLinecap="round" />
          </svg>
        </button>
      </div>

      {confirming && (
        <div className="mt-5 flex flex-wrap items-center gap-4 rounded-2xl border border-white/20 p-4" role="group" aria-label="Confirm leaving">
          <p className="font-mono text-sm">Leave this adventure? Your progress will be lost.</p>
          <button type="button" ref={stayRef} className="pill" onClick={() => setConfirming(false)}>
            Keep playing
          </button>
          <button type="button" className="pill pill-outline" onClick={onHome}>
            Leave
          </button>
        </div>
      )}

      <div className="mt-6">
        <TurnTracker turn={turn} totalTurns={totalTurns} />
      </div>

      <div className="mt-10 grid gap-10 lg:grid-cols-[1fr_340px]">
        <div key={scene.turn} className="reveal">
          <p className="max-w-2xl font-display text-3xl leading-snug sm:text-4xl">{scene.narrative}</p>
          <p className="mt-4 max-w-xl font-mono text-xs leading-5 text-dust">
            The story is fiction inspired by a real article. The blue note is the real part.
          </p>

          {history.length > 0 && (
            <ol className="mt-8 max-w-xl space-y-1 border-l border-white/20 pl-4 font-mono text-xs leading-5 text-dust">
              {history.map((h) => (
                <li key={h.turn}>
                  Turn {h.turn}: {h.choiceText}
                </li>
              ))}
            </ol>
          )}
        </div>

        <aside className="space-y-8">
          {article.thumbnailUrl && imageOk && (
            <div className="matte w-full max-w-xs -rotate-2 p-3">
              <img
                src={article.thumbnailUrl}
                alt=""
                loading="lazy"
                referrerPolicy="no-referrer"
                onError={() => setImageOk(false)}
                className="h-48 w-full object-cover grayscale-[35%] sepia-[20%]"
              />
              <p className="mt-2 font-mono text-[11px]">Image from the Wikipedia article.</p>
            </div>
          )}
          <div className="callout font-mono text-xs leading-5">
            <p className="text-sm font-medium">From the file</p>
            <p className="mt-2">{scene.fact}</p>
            <p className="mt-4 text-white/70">Wikipedia: {article.title}</p>
          </div>
        </aside>
      </div>

      <div className="mt-12">
        <h2 className="font-mono text-xs text-dust">What do you do?</h2>
        <ul className="mt-5 grid gap-6 sm:grid-cols-3">
          {scene.choices.map((choice, i) => (
            <ChoiceCard key={`${scene.turn}-${choice.id}`} choice={choice} index={i} disabled={busy} onChoose={onChoose} />
          ))}
        </ul>
        {busy && (
          <div className="mt-8 max-w-md" role="status">
            <p className="font-mono text-xs text-signal">Gemma is writing the next scene…</p>
            <div className="bar mt-3" aria-hidden="true" />
          </div>
        )}
      </div>
    </section>
  )
}
