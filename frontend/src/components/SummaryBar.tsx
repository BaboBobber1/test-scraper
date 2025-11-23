import React from 'react'

interface SummaryBarProps {
  total: number
  active: number
  archived: number
  blacklisted: number
  runningKeyword?: string | null
}

export const SummaryBar: React.FC<SummaryBarProps> = ({ total, active, archived, blacklisted, runningKeyword }) => (
  <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
    <div className="p-3 rounded-lg bg-gray-800 border border-gray-700">
      <div className="text-xs text-gray-400">Total</div>
      <div className="text-2xl font-semibold">{total}</div>
    </div>
    <div className="p-3 rounded-lg bg-emerald-900/40 border border-emerald-700">
      <div className="text-xs text-gray-400">Active</div>
      <div className="text-2xl font-semibold">{active}</div>
    </div>
    <div className="p-3 rounded-lg bg-gray-800 border border-gray-700">
      <div className="text-xs text-gray-400">Archived</div>
      <div className="text-2xl font-semibold">{archived}</div>
    </div>
    <div className="p-3 rounded-lg bg-rose-900/50 border border-rose-700">
      <div className="text-xs text-gray-200">Blacklisted</div>
      <div className="text-2xl font-semibold">{blacklisted}</div>
    </div>
    <div className="p-3 rounded-lg bg-sky-900/40 border border-sky-700 md:col-span-1 col-span-2">
      <div className="text-xs text-gray-400">Discovery Status</div>
      <div className="text-sm font-medium">{runningKeyword ? `Running: ${runningKeyword}` : 'Idle'}</div>
    </div>
  </div>
)
