import React, { useCallback, useState } from 'react'
import { searchApi, type SearchRequest, type SearchResponse } from '../services/api'
import SearchForm from '../components/SearchForm'
import SearchResults from '../components/SearchResults'

const SearchPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [page, setPage] = useState(1)
  const [lastRequest, setLastRequest] = useState<SearchRequest | null>(null)

  const runSearch = useCallback(async (payload: SearchRequest) => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await searchApi.search(payload)
      setResults(data)
      setPage(payload.page ?? 1)
      setLastRequest(payload)
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Search failed')
    } finally {
      setLoading(false)
    }
  }, [])

  const handleSearch = (payload: SearchRequest) => {
    runSearch({ ...payload, page: 1 })
  }

  const handlePageChange = (nextPage: number) => {
    if (!lastRequest) return
    runSearch({ ...lastRequest, page: nextPage })
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-primary-900/30 rounded-lg p-6 mb-6">
        <h1 className="text-2xl font-bold text-dark-primary mb-2">Advanced Search</h1>
        <p className="text-gray-600 mb-4">Search across tips, assessments, and documents with filters.</p>
        <SearchForm onSearch={handleSearch} loading={loading} />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-4 mb-6 text-sm text-red-700">{error}</div>
      )}

      <div className="bg-primary-900/30 rounded-lg p-4">
        <SearchResults
          hits={results?.hits ?? []}
          total={results?.total ?? 0}
          page={page}
          pageSize={lastRequest?.page_size ?? 20}
          loading={loading}
          onPageChange={handlePageChange}
        />
        {results && (
          <p className="mt-3 text-xs text-gray-500">Backend: {results.used_backend} • Took {results.took_ms} ms</p>
        )}
      </div>
    </div>
  )
}

export default SearchPage
