import React, { useEffect, useState } from 'react'
import { casesApi, InvestigationCase, CaseNoteItem } from '../services/api'
import { useToast } from '../contexts/ToastContext'

interface CaseNotesPanelProps {
  relatedEntityType: 'fraud_chain' | 'assessment' | 'pdf_check'
  relatedEntityId: string
}

const CaseNotesPanel: React.FC<CaseNotesPanelProps> = ({ relatedEntityType, relatedEntityId }) => {
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [caseItem, setCaseItem] = useState<InvestigationCase | null>(null)
  const [notes, setNotes] = useState<CaseNoteItem[]>([])
  const [newNote, setNewNote] = useState<string>('')
  const [author, setAuthor] = useState<string>('')
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null)
  const [editingAuthor, setEditingAuthor] = useState<string>('')
  const [editingContent, setEditingContent] = useState<string>('')
  const { addToast } = useToast()

  const loadOrCreateCase = async (createIfMissing = false) => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await casesApi.list({ related_entity_type: relatedEntityType, related_entity_id: relatedEntityId, limit: 1 })
      if (data && data.length > 0) {
        setCaseItem(data[0])
      } else if (createIfMissing) {
        const { data: created } = await casesApi.create({
          title: `Investigation for ${relatedEntityType} ${relatedEntityId.substring(0, 8)}`,
          description: 'Auto-created from Investigation view',
          related_entity_type: relatedEntityType,
          related_entity_id: relatedEntityId,
          status: 'open',
          priority: 'medium',
        })
        setCaseItem(created)
        addToast({ variant: 'success', description: 'Case created' })
      } else {
        setCaseItem(null)
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to load case')
      setCaseItem(null)
    } finally {
      setLoading(false)
    }
  }

  const loadNotes = async (caseId: string) => {
    try {
      const { data } = await casesApi.listNotes(caseId)
      setNotes(data)
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to load notes')
    }
  }

  useEffect(() => {
    if (!relatedEntityId) return
    loadOrCreateCase(false)
  }, [relatedEntityType, relatedEntityId])

  useEffect(() => {
    if (caseItem?.id) {
      loadNotes(caseItem.id)
    } else {
      setNotes([])
    }
  }, [caseItem?.id])

  const handleCreateCase = async () => {
    await loadOrCreateCase(true)
  }

  const handleAddNote = async () => {
    if (!caseItem?.id || !newNote.trim()) return
    try {
      const { data } = await casesApi.addNote(caseItem.id, { author: author || undefined, content: newNote.trim() })
      setNotes([data, ...notes])
      setNewNote('')
      addToast({ variant: 'success', description: 'Note added' })
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to add note')
      addToast({ variant: 'error', description: 'Failed to add note' })
    }
  }

  const handleUpdateCase = async (changes: Partial<Pick<InvestigationCase, 'title' | 'description' | 'status' | 'priority' | 'assigned_to'>>) => {
    if (!caseItem?.id) return
    try {
      const { data } = await casesApi.update(caseItem.id, changes as any)
      setCaseItem(data)
      addToast({ variant: 'success', description: 'Case updated' })
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to update case')
      addToast({ variant: 'error', description: 'Failed to update case' })
    }
  }

  const startEditNote = (note: CaseNoteItem) => {
    setEditingNoteId(note.id)
    setEditingAuthor(note.author || '')
    setEditingContent(note.content)
  }

  const cancelEditNote = () => {
    setEditingNoteId(null)
    setEditingAuthor('')
    setEditingContent('')
  }

  const saveEditNote = async () => {
    if (!caseItem?.id || !editingNoteId) return
    try {
      const { data } = await casesApi.updateNote(caseItem.id, editingNoteId, { author: editingAuthor || undefined, content: editingContent })
      setNotes((prev) => prev.map((n) => (n.id === data.id ? data : n)))
      cancelEditNote()
      addToast({ variant: 'success', description: 'Note updated' })
    } catch {
      addToast({ variant: 'error', description: 'Failed to update note' })
    }
  }

  const handleDeleteNote = async (noteId: string) => {
    if (!caseItem?.id) return
    try {
      await casesApi.deleteNote(caseItem.id, noteId)
      setNotes((prev) => prev.filter((n) => n.id !== noteId))
      addToast({ variant: 'success', description: 'Note deleted' })
    } catch {
      addToast({ variant: 'error', description: 'Failed to delete note' })
    }
  }

  return (
    <div className="space-y-3">
      {error && (
        <div className="p-2 rounded-md border border-rose-300 bg-rose-50 text-rose-800 text-xs">{error}</div>
      )}

      {!caseItem && !loading && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-contrast-500">No case exists for this item.</div>
          <button onClick={handleCreateCase} className="px-3 py-1.5 rounded bg-blue-600 text-white text-sm hover:bg-blue-700">Create Case</button>
        </div>
      )}

      {caseItem && (
        <div className="space-y-3">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
            <div className="flex-1">
              <input
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-dark-secondary dark:text-white dark:border-gray-600"
                value={caseItem.title}
                onChange={(e) => handleUpdateCase({ title: e.target.value })}
              />
              <textarea
                className="mt-2 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-dark-secondary dark:text-white dark:border-gray-600"
                placeholder="Case description"
                rows={2}
                value={caseItem.description || ''}
                onChange={(e) => handleUpdateCase({ description: e.target.value })}
              />
            </div>
            <div className="flex items-center gap-2 md:self-start">
              <select
                className="rounded-md border border-gray-300 px-2 py-1 text-sm dark:bg-dark-secondary dark:text-white dark:border-gray-600"
                value={caseItem.status}
                onChange={(e) => handleUpdateCase({ status: e.target.value as any })}
              >
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="closed">Closed</option>
              </select>
              <select
                className="rounded-md border border-gray-300 px-2 py-1 text-sm dark:bg-dark-secondary dark:text-white dark:border-gray-600"
                value={caseItem.priority}
                onChange={(e) => handleUpdateCase({ priority: e.target.value as any })}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
              <input
                type="text"
                placeholder="Assignee"
                className="rounded-md border border-gray-300 px-2 py-1 text-sm dark:bg-dark-secondary dark:text-white dark:border-gray-600"
                value={caseItem.assigned_to || ''}
                onChange={(e) => handleUpdateCase({ assigned_to: e.target.value })}
              />
            </div>
          </div>

          <div>
            <div className="mb-2 font-medium text-sm">Add note</div>
            <div className="flex flex-col md:flex-row gap-2">
              <input
                type="text"
                placeholder="Your name (optional)"
                className="md:w-48 rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-dark-secondary dark:text-white dark:border-gray-600"
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
              />
              <textarea
                placeholder="Write a note..."
                className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-dark-secondary dark:text-white dark:border-gray-600"
                rows={2}
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
              />
              <button
                onClick={handleAddNote}
                disabled={!newNote.trim()}
                className="self-start px-3 py-2 rounded bg-blue-600 text-white text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Add Note
              </button>
            </div>
          </div>

          <div>
            <div className="mb-2 font-medium text-sm">Notes</div>
            {notes.length === 0 ? (
              <div className="text-xs text-contrast-500">No notes yet.</div>
            ) : (
              <ul className="space-y-2 max-h-64 overflow-auto pr-1">
                {notes.map((n) => (
                  <li key={n.id} className="p-2 rounded border border-gray-200 dark:border-gray-700">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="text-xs text-contrast-500 mb-1">{n.author || 'Unknown'} · {new Date(n.created_at).toLocaleString()}</div>
                        {editingNoteId === n.id ? (
                          <div className="space-y-2">
                            <input
                              type="text"
                              className="w-full rounded-md border border-gray-300 px-2 py-1 text-sm dark:bg-dark-secondary dark:text-white dark:border-gray-600"
                              placeholder="Author (optional)"
                              value={editingAuthor}
                              onChange={(e) => setEditingAuthor(e.target.value)}
                            />
                            <textarea
                              className="w-full rounded-md border border-gray-300 px-2 py-1 text-sm dark:bg-dark-secondary dark:text-white dark:border-gray-600"
                              rows={3}
                              value={editingContent}
                              onChange={(e) => setEditingContent(e.target.value)}
                            />
                          </div>
                        ) : (
                          <div className="text-sm whitespace-pre-wrap">{n.content}</div>
                        )}
                      </div>
                      <div className="shrink-0 flex gap-2">
                        {editingNoteId === n.id ? (
                          <>
                            <button onClick={saveEditNote} className="px-2 py-1 rounded bg-emerald-600 text-white text-xs hover:bg-emerald-700">Save</button>
                            <button onClick={cancelEditNote} className="px-2 py-1 rounded bg-gray-200 text-xs dark:bg-gray-700">Cancel</button>
                          </>
                        ) : (
                          <>
                            <button onClick={() => startEditNote(n)} className="px-2 py-1 rounded bg-blue-600 text-white text-xs hover:bg-blue-700">Edit</button>
                            <button onClick={() => handleDeleteNote(n.id)} className="px-2 py-1 rounded bg-rose-600 text-white text-xs hover:bg-rose-700">Delete</button>
                          </>
                        )}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {caseItem && (
            <div className="flex items-center justify-between border-t pt-3 mt-2">
              <div className="text-xs text-contrast-500">
                Related: <span className="font-medium">{caseItem.related_entity_type}</span> · <span className="font-mono">{caseItem.related_entity_id}</span>
              </div>
              {caseItem.related_entity_type === 'fraud_chain' && caseItem.related_entity_id && (
                <button
                  onClick={() => { window.location.hash = `chain:${caseItem.related_entity_id}`; }}
                  className="px-3 py-1.5 rounded bg-gray-100 text-xs hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600"
                >
                  Open Related
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default CaseNotesPanel
