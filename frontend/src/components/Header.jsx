// Owner: Member 1. Props: none.
export default function Header() {
  return (
    <header className="border-b border-white/10">
      <div className="mx-auto grid max-w-6xl grid-cols-[1fr_auto_1fr] items-center px-5 py-4 sm:px-10">
        <span className="hidden font-mono text-xs text-dust sm:block">Wikipedia, replayed</span>
        <span className="font-display text-3xl italic sm:col-start-2 col-span-3 sm:col-span-1 text-center">
          rabbit hole
        </span>
        <span className="hidden text-right font-mono text-xs text-dust sm:block">
          Narrated by Gemma 4
        </span>
      </div>
    </header>
  )
}
