// Owner: Member 2. Chooses which screen to show. Contains no styling of its own.
import Header from './components/Header'
import Landing from './components/Landing'
import Loading from './components/Loading'
import Gameplay from './components/Gameplay'
import Ending from './components/Ending'
import ErrorPanel from './components/ErrorPanel'
import { useGame } from './hooks/useGame'

export default function App() {
  const { state, startNew, playSame, choose, retry, goHome } = useGame()
  const { status, article, scene, ending, history, turn, totalTurns, error } = state

  let screen
  if (status === 'IDLE') {
    screen = <Landing onStart={startNew} />
  } else if (status === 'FETCHING_ARTICLE') {
    screen = <Loading stage="FETCHING_ARTICLE" />
  } else if ((status === 'PLAYING' || status === 'GENERATING') && scene) {
    // While Gemma writes the next scene we keep the current page visible and mark it busy.
    screen = (
      <Gameplay
        article={article}
        scene={scene}
        turn={turn}
        totalTurns={totalTurns}
        history={history}
        busy={status === 'GENERATING'}
        onChoose={choose}
        onHome={goHome}
      />
    )
  } else if (status === 'GENERATING') {
    screen = <Loading stage="GENERATING" articleTitle={article?.title} />
  } else if (status === 'COMPLETED' && ending) {
    screen = (
      <Ending
        article={article}
        ending={ending}
        history={history}
        onReplaySame={playSame}
        onNew={startNew}
      />
    )
  } else if (status === 'ERROR') {
    screen = <ErrorPanel error={error} onRetry={retry} onHome={goHome} />
  } else {
    screen = <ErrorPanel error={null} onRetry={null} onHome={goHome} />
  }

  return (
    <div className="min-h-dvh">
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <Header />
      <main id="main">{screen}</main>
    </div>
  )
}
