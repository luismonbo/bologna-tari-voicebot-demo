import { AppointmentsSection } from './components/AppointmentsSection'
import { LogsSection } from './components/LogsSection'
import './styles/App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>Demo TARI Voicebot</h1>
            <p className="header-subtitle">Comune di Bologna — Gestione Appuntamenti e Registri Chiamate</p>
          </div>
        </div>
      </header>

      <main className="app-main">
        <AppointmentsSection />
        <LogsSection />
      </main>

      <footer className="app-footer">
        <p>
          Assistente virtuale per informazioni sulla TARI e prenotazione appuntamenti presso l'Ufficio Tributi
        </p>
      </footer>
    </div>
  )
}

export default App
