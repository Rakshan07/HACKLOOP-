// Owner: Member 1. Props: { stage: 'FETCHING_ARTICLE' | 'GENERATING', articleTitle?: string }
import { useEffect, useState } from 'react'

const MESSAGES = {
  FETCHING_ARTICLE: [
    'Opening a random drawer…',
    'Asking Wikipedia for a file…',
    'Checking the file is not a stub…',
    'Blowing the dust off the cover…',
  ],
  GENERATING: [
    'Gemma is reading the file…',
    'Hunting for the strangest detail…',
    'Writing the next scene…',
    'Inventing three choices…',
  ],
}

export default function Loading({ stage, articleTitle }) {
  const messages = MESSAGES[stage] ?? MESSAGES.GENERATING
  const [index, setIndex] = useState(0)

  useEffect(() => {
    setIndex(0)
    const timer = setInterval(() => setIndex((i) => (i + 1) % messages.length), 2400)
    return () => clearInterval(timer)
  }, [stage, messages.length])

  const wikiDone = stage === 'GENERATING'

  return (
    <section className="reveal mx-auto max-w-3xl px-5 py-20 sm:px-10">
      <p className="sr-only" role="status">
        Loading, please wait.
      </p>
      <p className="font-mono text-xs text-dust">
        Archive / {articleTitle ? articleTitle : 'Unopened file'} / Loading
      </p>
      <h1 className="mt-4 font-display text-5xl font-light sm:text-7xl">
        {articleTitle ?? 'Finding your file'}
      </h1>

      <div className="callout mt-10 max-w-md font-mono text-sm leading-6">
        <p className="font-medium">{wikiDone ? 'Gemma at work' : 'Wikipedia'}</p>
        <p className="mt-2 min-h-12" aria-hidden="true">
          {messages[index]}
        </p>
      </div>

      <div className="mt-10 max-w-md">
        <div className="bar" aria-hidden="true" />
        <ol className="mt-5 space-y-2 font-mono text-xs">
          <li className={wikiDone ? 'text-bone' : 'text-signal'}>
            {wikiDone ? 'Done' : 'Now'}: fetch a random Wikipedia article
          </li>
          <li className={wikiDone ? 'text-signal' : 'text-dust'}>
            {wikiDone ? 'Now' : 'Next'}: Gemma writes your scene
          </li>
        </ol>
      </div>
    </section>
  )
}
