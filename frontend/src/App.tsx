import React, { useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { QuickstartModal } from './components/QuickstartModal'
import { DiscoverySettingsModal } from './components/DiscoverySettingsModal'
import { EnrichmentSettingsModal } from './components/EnrichmentSettingsModal'
import { HelpModal } from './components/HelpModal'
import { ChannelTable, ChannelRow } from './components/ChannelTable'
import { SummaryBar } from './components/SummaryBar'

const api = async (path: string, opts?: RequestInit) => {
  const res = await fetch(path, opts)
  if (!res.ok) throw new Error('Request failed')
  return res.json()
}

function App() {
  const client = useQueryClient()
  const [quickstartOpen, setQuickstartOpen] = useState(false)
  const [discoveryOpen, setDiscoveryOpen] = useState(false)
  const [enrichmentOpen, setEnrichmentOpen] = useState(false)
  const [helpOpen, setHelpOpen] = useState(false)

  const statsQuery = useQuery(['stats'], () => api('/api/stats'), { refetchInterval: 4000 })
  const channelsQuery = useQuery(['channels'], () => api('/api/channels'))

  const startDiscovery = async (keywords: string[], runUntilStopped: boolean, autoEnrich: boolean) => {
    await api('/api/discovery/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ keywords, run_until_stopped: runUntilStopped, auto_enrich: autoEnrich }),
    })
    client.invalidateQueries({ queryKey: ['stats'] })
  }

  const startDiscoveryAdvanced = async (
    keywords: string[],
    opts: { maxNew: number; minSubs: number; minLongform: number; maxAge: number; denyLangs: string[]; runUntilStopped: boolean; autoEnrich: boolean },
  ) => {
    await startDiscovery(keywords, opts.runUntilStopped, opts.autoEnrich)
  }

  const startEnrichment = async (settings: any, scope: string) => {
    await api('/api/enrich/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scope, settings }),
    })
    client.invalidateQueries({ queryKey: ['channels'] })
  }

  const channels: ChannelRow[] = useMemo(() => channelsQuery.data || [], [channelsQuery.data])

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <div className="max-w-6xl mx-auto px-4 py-6">
        <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold text-white">Crypto YouTube Harvester</h1>
            <p className="text-gray-400 text-sm">Mass scrape crypto channels, detect contact data, and enrich at scale.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button className="px-4 py-2 bg-emerald-600 rounded-md" onClick={() => setQuickstartOpen(true)}>
              Quickstart
            </button>
            <button className="px-4 py-2 bg-blue-700 rounded-md" onClick={() => setDiscoveryOpen(true)}>
              Discover
            </button>
            <button className="px-4 py-2 bg-indigo-700 rounded-md" onClick={() => setEnrichmentOpen(true)}>
              Enrich
            </button>
            <button className="px-4 py-2 bg-gray-700 rounded-md" onClick={() => setHelpOpen(true)}>
              Help
            </button>
          </div>
        </header>

        {statsQuery.data && (
          <SummaryBar
            total={statsQuery.data.total}
            active={statsQuery.data.active}
            archived={statsQuery.data.archived}
            blacklisted={statsQuery.data.blacklisted}
            runningKeyword={statsQuery.data.running_keyword}
          />
        )}

        <div className="flex items-center justify-between mb-3">
          <div className="text-sm text-gray-400">Channels</div>
          <div className="flex gap-2">
            <button className="px-3 py-1 rounded-md bg-gray-800 border border-gray-700" onClick={() => client.invalidateQueries({ queryKey: ['channels'] })}>
              Refresh
            </button>
            <button className="px-3 py-1 rounded-md bg-gray-800 border border-gray-700" onClick={() => api('/api/export/bundle').then((bundle) => alert(JSON.stringify(bundle, null, 2)))}>
              Export
            </button>
          </div>
        </div>

        {channelsQuery.isLoading ? (
          <div className="text-gray-400">Loading channels…</div>
        ) : (
          <ChannelTable rows={channels} />
        )}
      </div>

      <QuickstartModal open={quickstartOpen} onClose={() => setQuickstartOpen(false)} onStart={startDiscovery} />
      <DiscoverySettingsModal open={discoveryOpen} onClose={() => setDiscoveryOpen(false)} onStart={startDiscoveryAdvanced} />
      <EnrichmentSettingsModal open={enrichmentOpen} onClose={() => setEnrichmentOpen(false)} onSave={startEnrichment} />
      <HelpModal open={helpOpen} onClose={() => setHelpOpen(false)} />
    </div>
  )
}

export default App
