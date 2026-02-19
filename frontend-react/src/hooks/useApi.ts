import { useState, useCallback } from 'react'
import apiClient from '../services/api'
import { APIError } from '../types'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: APIError | null
}

export const useApi = <T,>(url: string) => {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null
  })

  const fetchData = useCallback(async () => {
    setState({ data: null, loading: true, error: null })
    try {
      const response = await apiClient.get<T>(url)
      setState({ data: response.data, loading: false, error: null })
      return response.data
    } catch (error: unknown) {
      const apiError: APIError = {
        message: error instanceof Error ? error.message : 'An error occurred',
        code: 'UNKNOWN_ERROR'
      }
      setState({ data: null, loading: false, error: apiError })
      throw error
    }
  }, [url])

  return { ...state, fetchData }
}
