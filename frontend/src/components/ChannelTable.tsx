import React from 'react'

export interface ChannelRow {
  id: number
  name?: string | null
  url?: string | null
  subscribers?: number | null
  language?: string | null
  emails?: string | null
  telegram?: string | null
  status: string
  updated_at?: string
}

interface ChannelTableProps {
  rows: ChannelRow[]
}

const statusColor: Record<string, string> = {
  new: 'bg-blue-900/60 text-blue-100 border border-blue-700',
  active: 'bg-emerald-900/60 text-emerald-100 border border-emerald-700',
  blacklisted: 'bg-rose-900/60 text-rose-100 border border-rose-700',
  archived: 'bg-gray-800 text-gray-100 border border-gray-700',
}

export const ChannelTable: React.FC<ChannelTableProps> = ({ rows }) => (
  <div className="overflow-x-auto border border-gray-800 rounded-lg">
    <table className="min-w-full text-sm">
      <thead className="bg-gray-800 text-gray-300">
        <tr>
          <th className="px-3 py-2 text-left">Name</th>
          <th className="px-3 py-2 text-left">Subscribers</th>
          <th className="px-3 py-2 text-left">Language</th>
          <th className="px-3 py-2 text-left">Emails</th>
          <th className="px-3 py-2 text-left">Telegram</th>
          <th className="px-3 py-2 text-left">Status</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id} className="border-t border-gray-800 hover:bg-gray-900/50">
            <td className="px-3 py-2 font-semibold text-white">
              {row.url ? (
                <a href={row.url} target="_blank" rel="noreferrer" className="hover:underline">
                  {row.name || row.url}
                </a>
              ) : (
                row.name
              )}
            </td>
            <td className="px-3 py-2">{row.subscribers ?? '–'}</td>
            <td className="px-3 py-2">{row.language || 'N/A'}</td>
            <td className="px-3 py-2">
              {row.emails ? (
                <span title={row.emails}>{row.emails.split(',').filter(Boolean).length} emails</span>
              ) : (
                '—'
              )}
            </td>
            <td className="px-3 py-2">
              {row.telegram ? (
                <a href={`https://t.me/${row.telegram.replace('@', '')}`} target="_blank" rel="noreferrer" className="text-sky-300 hover:underline">
                  {row.telegram}
                </a>
              ) : (
                '—'
              )}
            </td>
            <td className="px-3 py-2">
              <span className={`px-2 py-1 rounded-full text-xs uppercase tracking-wide ${statusColor[row.status] || 'bg-gray-800 text-gray-200 border border-gray-700'}`}>
                {row.status}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
)
