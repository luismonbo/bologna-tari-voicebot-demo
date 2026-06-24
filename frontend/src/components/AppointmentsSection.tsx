import { useFetch } from '../hooks/useFetch'

interface Appointment {
  office: string
  date: string
  time: string
  citizen_name: string
  contact: string
  reason?: string
}

interface AppointmentsResponse {
  appointments: Appointment[]
}

export function AppointmentsSection() {
  const { data, loading, error, refetch } = useFetch<AppointmentsResponse>('/appointments')

  return (
    <section className="section">
      <div className="section-header">
        <h2>Appuntamenti Prenotati</h2>
        <button onClick={refetch} className="btn-refresh" title="Aggiorna">
          ⟳
        </button>
      </div>

      {loading && <p className="state-message">Caricamento...</p>}

      {error && (
        <p className="state-error">
          Non è stato possibile caricare gli appuntamenti.{' '}
          <button onClick={refetch} className="btn-inline">
            Riprova
          </button>
        </p>
      )}

      {!loading && !error && (!data?.appointments || data.appointments.length === 0) && (
        <p className="state-empty">Nessun appuntamento prenotato</p>
      )}

      {!loading && !error && data?.appointments && data.appointments.length > 0 && (
        <div className="table-wrapper">
          <table className="appointments-table">
            <thead>
              <tr>
                <th>Ufficio</th>
                <th>Data</th>
                <th>Orario</th>
                <th>Nome Cittadino</th>
                <th>Contatto</th>
                <th>Motivo</th>
              </tr>
            </thead>
            <tbody>
              {data.appointments.map((appt, idx) => (
                <tr key={idx}>
                  <td>{appt.office}</td>
                  <td>{formatDate(appt.date)}</td>
                  <td>{appt.time}</td>
                  <td>{appt.citizen_name}</td>
                  <td>{appt.contact}</td>
                  <td>{appt.reason || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

function formatDate(dateStr: string): string {
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('it-IT', { year: 'numeric', month: 'long', day: 'numeric' })
  } catch {
    return dateStr
  }
}
