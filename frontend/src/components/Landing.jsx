// Owner: Member 1. Props: { onStart: () => void, disabled?: boolean }

function Shuffle() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <path d="M16 3h5v5M4 20 21 3M21 16v5h-5M15 15l6 6M4 4l5 5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export default function Landing({ onStart, disabled = false }) {
  return (
    <section className="reveal mx-auto max-w-6xl px-5 pb-24 pt-10 sm:px-10">
      <p className="font-mono text-xs text-dust">Archive / Random drawer / Unopened</p>

      <div className="mt-5 flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <h1 className="font-display text-7xl font-light leading-[0.9] sm:text-9xl">Rabbit Hole</h1>
        <dl className="font-mono text-xs leading-6 text-dust lg:pt-4 lg:text-right">
          <dt className="text-bone">Source</dt>
          <dd>Wikipedia, chosen at random</dd>
          <dt className="mt-3 text-bone">Narrator</dt>
          <dd>Gemma 4, an open-weight model</dd>
          <dt className="mt-3 text-bone">Length</dt>
          <dd>Five decisions</dd>
        </dl>
      </div>

      <div className="mt-10 grid max-w-3xl gap-6 font-mono text-[13px] leading-6 text-bone/85 sm:grid-cols-2">
        <p>
          Every random Wikipedia article is a sealed file. Press the button and we open one,
          find its strangest detail, and turn it into an adventure you can play.
        </p>
        <p>
          You make five decisions. Each one changes what happens next, and at the end you see
          what really happened. The story is fiction. The facts in the file are not.
        </p>
      </div>

      <div className="mt-10 flex flex-wrap items-center gap-5">
        <button className="pill text-base" onClick={onStart} disabled={disabled}>
          <Shuffle />
          I’M BORED
        </button>
        <span className="font-mono text-xs text-dust">No sign-up. Takes about three minutes.</span>
      </div>

      {/* Decorative collage. Not interactive, hidden from screen readers. */}
      <div className="mt-16 flex flex-wrap items-end justify-center gap-y-8 lg:justify-start" aria-hidden="true">
        <div className="paper -mr-4 w-64 -rotate-3 bg-card-blue p-4 font-mono">
          <p className="font-display text-2xl tracking-wide text-[#1f46dc]">FIVE TURN LOAN</p>
          <p className="mt-1 text-[10px] text-[#1f46dc]">RETURN TO THE ENDING BEFORE CLOSING</p>
          <div className="mt-4 space-y-2 text-xs">
            <p className="border-b border-[#1f46dc]/40">Turn 1 ........ ?</p>
            <p className="border-b border-[#1f46dc]/40">Turn 3 ........ ?</p>
            <p className="border-b border-[#1f46dc]/40">Turn 5 ........ ?</p>
          </div>
        </div>

        <div className="matte relative z-10 w-72 rotate-[1.5deg] p-3">
          <div className="grid h-44 place-items-center bg-vault-2">
            <span className="font-display text-9xl font-light text-dust">?</span>
          </div>
          <p className="mt-2 font-mono text-[11px]">Subject: unknown. Opened at random.</p>
        </div>

        <div className="paper -ml-4 w-56 rotate-[4deg] bg-card-manila p-4 font-mono">
          <p className="font-display text-2xl">Folder 0001</p>
          <p className="mt-2 text-xs leading-5">Contents: one strange fact, three choices, and an ending nobody has seen.</p>
        </div>

        <div className="callout ml-8 w-60 font-mono text-xs leading-5">
          <p className="font-medium">How it works</p>
          <p className="mt-1">Random article, five choices, one ending.</p>
          <p className="mt-3 text-white/70">AI writes the story. Wikipedia keeps it honest.</p>
        </div>
      </div>
    </section>
  )
}
