import { useFetch } from '../hooks/useFetch'
import { CallCard } from './CallCard'

interface Call {
  id: string
  timestamp: string
  duration: number
  citizen_name: string | null
  result: 'booked' | 'info' | 'error'
}

interface CallsResponse {
  calls: Call[]
}

export function LogsSection() {
  const { data, loading, error, refetch } = useFetch<CallsResponse>('/calls/recent?limit=10')

  return (
    <section className="section">
      <div className="section-header">
        <h2>Trascrizioni Conversazioni</h2>
        <button onClick={refetch} className="btn-refresh" title="Aggiorna">
          ⟳
        </button>
      </div>

      {loading && <p className="state-message">Caricamento...</p>}

      {error && (
        <p className="state-error">
          Non è stato possibile caricare i registri delle chiamate.{' '}
          <button onClick={refetch} className="btn-inline">
            Riprova
          </button>
        </p>
      )}

      {!loading && !error && (!data?.calls || data.calls.length === 0) && (
        <p className="state-empty">Nessuna chiamata registrata</p>
      )}

      {!loading && !error && data?.calls && data.calls.length > 0 && (
        <div className="calls-list">
          {data.calls.map((call) => (
            <CallCard key={call.id} call={call} />
          ))}
        </div>
      )}
    </section>
  )
}
