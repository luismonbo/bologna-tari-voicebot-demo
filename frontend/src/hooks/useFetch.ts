import { useState, useEffect, useRef } from 'react'

interface FetchState<T> {
  data: T | null
  loading: boolean
  error: Error | null
}

export function useFetch<T>(url: string | null): FetchState<T> & { refetch: () => void } {
  const [state, setState] = useState<FetchState<T>>({
    data: null,
    loading: true,
    error: null,
  })

  const ignoreRef = useRef(false)

  const fetchData = async () => {
    if (!url) {
      setState({ data: null, loading: false, error: null })
      return
    }

    ignoreRef.current = false
    setState({ data: null, loading: true, error: null })

    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
      const response = await fetch(`${backendUrl}${url}`)

      if (!ignoreRef.current) {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        const result = await response.json()
        setState({ data: result, loading: false, error: null })
      }
    } catch (err) {
      if (!ignoreRef.current) {
        setState({
          data: null,
          loading: false,
          error: err instanceof Error ? err : new Error('Unknown error'),
        })
      }
    }
  }

  useEffect(() => {
    fetchData()
    return () => {
      ignoreRef.current = true
    }
  }, [url])

  return {
    ...state,
    refetch: fetchData,
  }
}
