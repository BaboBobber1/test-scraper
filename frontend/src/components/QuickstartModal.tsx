import React, { useState } from 'react'
import { Modal } from './Modal'

interface QuickstartModalProps {
  open: boolean
  onClose: () => void
  onStart: (keywords: string[], runUntilStopped: boolean, autoEnrich: boolean) => void
}

const defaultKeywords = ['crypto', 'crypto trading', 'bitcoin']

export const QuickstartModal: React.FC<QuickstartModalProps> = ({ open, onClose, onStart }) => {
  const [keywordText, setKeywordText] = useState(defaultKeywords.join('\n'))
  const [runUntilStopped, setRunUntilStopped] = useState(true)
  const [autoEnrich, setAutoEnrich] = useState(true)

  const handleStart = () => {
    const keywords = keywordText
      .split('\n')
      .map((k) => k.trim())
      .filter(Boolean)
    onStart(keywords, runUntilStopped, autoEnrich)
    onClose()
  }

  return (
    <Modal open={open} onClose={onClose} title="Quickstart Discovery">
      <div className="space-y-4">
        <div>
          <label className="text-sm text-gray-300">Keywords (one per line)</label>
          <textarea
            value={keywordText}
            onChange={(e) => setKeywordText(e.target.value)}
            className="w-full mt-2 bg-gray-800 border border-gray-700 rounded-md p-3 text-sm text-gray-100"
            rows={4}
          />
        </div>
        <div className="flex items-center space-x-3">
          <input type="checkbox" checked={runUntilStopped} onChange={(e) => setRunUntilStopped(e.target.checked)} />
          <span>Run until stopped</span>
        </div>
        <div className="flex items-center space-x-3">
          <input type="checkbox" checked={autoEnrich} onChange={(e) => setAutoEnrich(e.target.checked)} />
          <span>Auto-enrich discovered channels</span>
        </div>
        <p className="text-xs text-gray-400">
          Default enrichment: Email FULL + Precise Language detection.
        </p>
        <div className="flex justify-end space-x-3">
          <button className="px-4 py-2 rounded-md bg-gray-700" onClick={onClose}>
            Cancel
          </button>
          <button className="px-4 py-2 rounded-md bg-emerald-600" onClick={handleStart}>
            Start Quickstart
          </button>
        </div>
      </div>
    </Modal>
  )
}
