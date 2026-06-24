import { useState } from 'react'
import { useFetch } from '../hooks/useFetch'

interface Call {
  id: string
  timestamp: string
  duration: number
  citizen_name: string | null
  result: 'booked' | 'info' | 'error'
}

interface TranscriptEntry {
  role: 'citizen' | 'assistant'
  text: string
}

interface TranscriptResponse {
  transcript: TranscriptEntry[]
  metadata: {
    duration: number
    timestamp: string
    citizen_name: string | null
  }
}

interface CallCardProps {
  call: Call
}

export function CallCard({ call }: CallCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const { data: transcript, loading: transcriptLoading } = useFetch<TranscriptResponse>(
    isExpanded ? `/call/${call.id}/transcript` : null
  )

  const resultLabel = {
    booked: 'Prenotato',
    info: 'Informazione',
    error: 'Errore',
  }[call.result]

  const resultColor = {
    booked: '#4ade80',
    info: '#60a5fa',
    error: '#f87171',
  }[call.result]

  return (
    <div className="call-card">
      <button
        className="call-card-header"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
      >
        <div className="call-card-header-content">
          <span className="call-timestamp">{formatTimestamp(call.timestamp)}</span>
          <span className="call-duration">{formatDuration(call.duration)}</span>
          {call.citizen_name && <span className="call-citizen">{call.citizen_name}</span>}
          <span className="call-result" style={{ backgroundColor: resultColor }}>
            {resultLabel}
          </span>
        </div>
        <span className="call-expand-icon">{isExpanded ? '▾' : '▸'}</span>
      </button>

      {isExpanded && (
        <div className="call-card-body">
          {transcriptLoading && <p className="state-message">Caricamento trascrizione...</p>}

          {transcript && transcript.transcript && (
            <div className="transcript">
              {transcript.transcript.map((entry, idx) => (
                <div key={idx} className={`transcript-entry transcript-${entry.role}`}>
                  <span className="transcript-role">
                    {entry.role === 'citizen' ? 'Cittadino' : 'Assistente'}:
                  </span>
                  <p className="transcript-text">{entry.text}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function formatTimestamp(iso: string): string {
  try {
    const date = new Date(iso)
    return date.toLocaleString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}m ${secs}s`
}
