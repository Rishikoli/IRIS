import React, { useState } from 'react'
import { type SearchRequest } from '../services/api'
import Card, { CardHeader, CardTitle, CardContent } from './ui/Card'
import Badge from './ui/Badge'
import Toolbar from './ui/Toolbar'

interface Props {
  defaultPageSize?: number
  onSearch: (payload: SearchRequest) => void
  loading?: boolean
}

const SearchForm: React.FC<Props> = ({ onSearch, loading = false, defaultPageSize = 20 }) => {
  const [query, setQuery] = useState('')
  const ENTITY_OPTIONS = ['tips', 'assessments', 'documents'] as const
  const RISK_OPTIONS = ['High', 'Medium', 'Low'] as const

  const [entities, setEntities] = useState<Array<typeof ENTITY_OPTIONS[number]>>(['tips', 'assessments', 'documents'])
  const [riskLevels, setRiskLevels] = useState<Array<typeof RISK_OPTIONS[number]>>([])
  const [dateFrom, setDateFrom] = useState<string>('')
  const [dateTo, setDateTo] = useState<string>('')
  const [fuzzy, setFuzzy] = useState<boolean>(true)
  const [maxEdits, setMaxEdits] = useState<number>(2)
  const [pageSize, setPageSize] = useState<number>(defaultPageSize)

  const toggleArrayValue = <T,>(arr: T[], value: T) =>
    arr.includes(value) ? arr.filter(v => v !== value) : [...arr, value]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const payload: SearchRequest = {
      query: query.trim(),
      entities,
      filters: {
        risk_levels: riskLevels.length ? riskLevels : undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      },
      fuzzy: { enabled: fuzzy, max_edits: maxEdits },
      page: 1,
      page_size: pageSize,
    }
    onSearch(payload)
  }

  return (
    <Card className="bg-background-50">
      <CardHeader>
        <CardTitle>Search</CardTitle>
        <div className="hidden md:flex items-center gap-2 text-xs text-contrast-500 overflow-x-auto whitespace-nowrap">
          <span>Entities</span>
          {entities.map(e => (
            <Badge key={e} className="capitalize">{e}</Badge>
          ))}
        </div>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-contrast-600 mb-1">Query</label>
            <input
              type="text"
              className="w-full px-4 py-2.5 rounded-lg border border-contrast-200 bg-white focus:outline-none focus:ring-2 focus:ring-primary-300 placeholder-contrast-400"
              placeholder="Search tips, assessments, documents..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
            <div className="md:col-span-4">
              <p className="text-xs font-medium text-contrast-600 mb-2">Entities</p>
              <div className="flex flex-wrap gap-3">
                {ENTITY_OPTIONS.map((ent) => (
                  <label key={ent} className="flex items-center gap-2 text-sm whitespace-nowrap">
                    <input
                      type="checkbox"
                      className="h-4 w-4 rounded border-contrast-300 text-primary-600 focus:ring-primary-500"
                      checked={entities.includes(ent)}
                      onChange={() => setEntities(prev => toggleArrayValue(prev, ent))}
                    />
                    <span className="capitalize">{ent}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="md:col-span-4">
              <p className="text-xs font-medium text-contrast-600 mb-2">Risk Levels</p>
              <div className="flex flex-wrap gap-3">
                {RISK_OPTIONS.map((level) => (
                  <label key={level} className="flex items-center gap-2 text-sm whitespace-nowrap">
                    <input
                      type="checkbox"
                      className="h-4 w-4 rounded border-contrast-300 text-primary-600 focus:ring-primary-500"
                      checked={riskLevels.includes(level)}
                      onChange={() => setRiskLevels(prev => toggleArrayValue(prev, level))}
                    />
                    <span>{level}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="md:col-span-4">
              <p className="text-xs font-medium text-contrast-600 mb-2">Date range</p>
              <div className="flex flex-wrap gap-2">
                <input type="date" className="px-3 py-2 border border-contrast-200 rounded-lg min-w-[140px] flex-1 focus:ring-primary-300 focus:outline-none" value={dateFrom} onChange={(e)=>setDateFrom(e.target.value)} />
                <input type="date" className="px-3 py-2 border border-contrast-200 rounded-lg min-w-[140px] flex-1 focus:ring-primary-300 focus:outline-none" value={dateTo} onChange={(e)=>setDateTo(e.target.value)} />
              </div>
            </div>
          </div>

          <Toolbar className="bg-white flex-wrap">
            <div className="flex flex-wrap items-center gap-4">
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" className="h-4 w-4 rounded border-contrast-300 text-primary-600 focus:ring-primary-500" checked={fuzzy} onChange={(e)=>setFuzzy(e.target.checked)} />
                <span>Fuzzy</span>
              </label>
              <label className="flex items-center gap-2 text-sm">
                <span className="text-contrast-600">Max edits</span>
                <input type="number" min={0} max={2} className="w-20 px-2 py-1.5 border border-contrast-200 rounded-lg" value={maxEdits} onChange={(e)=>setMaxEdits(Number(e.target.value))} />
              </label>
              <label className="flex items-center gap-2 text-sm">
                <span className="text-contrast-600">Page size</span>
                <select className="px-2 py-1.5 border border-contrast-200 rounded-lg" value={pageSize} onChange={(e)=>setPageSize(Number(e.target.value))}>
                  {[10,20,50].map(n => <option key={n} value={n}>{n}</option>)}
                </select>
              </label>
            </div>

            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="inline-flex items-center justify-center px-4 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-50"
            >
              {loading ? 'Searching…' : 'Search'}
            </button>
          </Toolbar>
        </form>
      </CardContent>
    </Card>
  )
}

export default SearchForm
