import React, { useState } from 'react'
import { Modal } from './Modal'

interface DiscoverySettingsModalProps {
  open: boolean
  onClose: () => void
  onStart: (keywords: string[], opts: { maxNew: number; minSubs: number; minLongform: number; maxAge: number; denyLangs: string[]; runUntilStopped: boolean; autoEnrich: boolean }) => void
}

const LANG_OPTIONS = ['EN', 'DE', 'HI', 'ES', 'FR', 'TR']

export const DiscoverySettingsModal: React.FC<DiscoverySettingsModalProps> = ({ open, onClose, onStart }) => {
  const [keywords, setKeywords] = useState('crypto\ncrypto trading\nbitcoin')
  const [maxNew, setMaxNew] = useState(5)
  const [minSubs, setMinSubs] = useState(1000)
  const [minLongform, setMinLongform] = useState(5)
  const [maxAge, setMaxAge] = useState(30)
  const [denyLangs, setDenyLangs] = useState<string[]>([])
  const [runUntilStopped, setRunUntilStopped] = useState(true)
  const [autoEnrich, setAutoEnrich] = useState(true)

  const handleLangToggle = (lang: string) => {
    setDenyLangs((prev) => (prev.includes(lang) ? prev.filter((l) => l !== lang) : [...prev, lang]))
  }

  const handleStart = () => {
    const keywordList = keywords
      .split('\n')
      .map((k) => k.trim())
      .filter(Boolean)
    onStart(keywordList, { maxNew, minSubs, minLongform, maxAge, denyLangs, runUntilStopped, autoEnrich })
    onClose()
  }

  return (
    <Modal open={open} onClose={onClose} title="Discovery Settings">
      <div className="space-y-4">
        <div>
          <label className="text-sm text-gray-300">Keywords</label>
          <textarea
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-md p-3 text-sm text-gray-100 mt-2"
            rows={4}
          />
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <label className="space-y-1">
            <span>Max new channels per run</span>
            <input type="number" value={maxNew} onChange={(e) => setMaxNew(Number(e.target.value))} className="w-full bg-gray-800 border border-gray-700 rounded-md p-2" />
          </label>
          <label className="space-y-1">
            <span>Min subscribers</span>
            <input type="number" value={minSubs} onChange={(e) => setMinSubs(Number(e.target.value))} className="w-full bg-gray-800 border border-gray-700 rounded-md p-2" />
          </label>
          <label className="space-y-1">
            <span>Min long-form videos</span>
            <input type="number" value={minLongform} onChange={(e) => setMinLongform(Number(e.target.value))} className="w-full bg-gray-800 border border-gray-700 rounded-md p-2" />
          </label>
          <label className="space-y-1">
            <span>Max last upload age (days)</span>
            <input type="number" value={maxAge} onChange={(e) => setMaxAge(Number(e.target.value))} className="w-full bg-gray-800 border border-gray-700 rounded-md p-2" />
          </label>
        </div>
        <div>
          <span className="text-sm text-gray-300">Deny languages</span>
          <div className="flex flex-wrap gap-2 mt-2">
            {LANG_OPTIONS.map((lang) => (
              <button
                key={lang}
                onClick={() => handleLangToggle(lang)}
                className={`px-3 py-1 rounded-md border ${denyLangs.includes(lang) ? 'bg-red-600/80 border-red-500' : 'bg-gray-800 border-gray-700'}`}
              >
                {lang}
              </button>
            ))}
          </div>
        </div>
        <div className="flex flex-col space-y-2">
          <label className="flex items-center space-x-2">
            <input type="checkbox" checked={runUntilStopped} onChange={(e) => setRunUntilStopped(e.target.checked)} />
            <span>Run until stopped</span>
          </label>
          <label className="flex items-center space-x-2">
            <input type="checkbox" checked={autoEnrich} onChange={(e) => setAutoEnrich(e.target.checked)} />
            <span>Auto-enrich discovered channels</span>
          </label>
        </div>
        <div className="flex justify-end space-x-3">
          <button className="px-4 py-2 rounded-md bg-gray-700" onClick={onClose}>
            Cancel
          </button>
          <button className="px-4 py-2 rounded-md bg-emerald-600" onClick={handleStart}>
            Start discovery
          </button>
        </div>
      </div>
    </Modal>
  )
}
