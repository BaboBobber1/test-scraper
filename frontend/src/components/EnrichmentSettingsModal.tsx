import React, { useState } from 'react'
import { Modal } from './Modal'

interface EnrichmentSettings {
  email_enabled: boolean
  email_mode: 'CHANNEL_ONLY' | 'VIDEOS_ONLY' | 'FULL'
  language_enabled: boolean
  language_mode: 'BASIC' | 'PRECISE'
  refresh_channel_metadata: boolean
  update_last_upload: boolean
}

interface EnrichmentSettingsModalProps {
  open: boolean
  onClose: () => void
  onSave: (settings: EnrichmentSettings, scope: string) => void
}

export const EnrichmentSettingsModal: React.FC<EnrichmentSettingsModalProps> = ({ open, onClose, onSave }) => {
  const [settings, setSettings] = useState<EnrichmentSettings>({
    email_enabled: true,
    email_mode: 'FULL',
    language_enabled: true,
    language_mode: 'PRECISE',
    refresh_channel_metadata: true,
    update_last_upload: true,
  })
  const [scope, setScope] = useState('active')

  const handleSave = () => {
    onSave(settings, scope)
    onClose()
  }

  return (
    <Modal open={open} onClose={onClose} title="Enrichment Settings">
      <div className="space-y-4 text-sm">
        <div className="space-y-2">
          <span className="text-gray-300">Scope</span>
          <div className="flex items-center space-x-3">
            <label className="flex items-center space-x-2">
              <input type="radio" name="scope" value="active" checked={scope === 'active'} onChange={(e) => setScope(e.target.value)} />
              <span>Current filter only</span>
            </label>
            <label className="flex items-center space-x-2">
              <input type="radio" name="scope" value="all" checked={scope === 'all'} onChange={(e) => setScope(e.target.value)} />
              <span>All active channels</span>
            </label>
          </div>
        </div>

        <div className="space-y-2">
          <label className="flex items-center space-x-2">
            <input type="checkbox" checked={settings.email_enabled} onChange={(e) => setSettings({ ...settings, email_enabled: e.target.checked })} />
            <span>Email enrichment</span>
          </label>
          <select
            value={settings.email_mode}
            onChange={(e) => setSettings({ ...settings, email_mode: e.target.value as EnrichmentSettings['email_mode'] })}
            className="bg-gray-800 border border-gray-700 rounded-md p-2"
          >
            <option value="CHANNEL_ONLY">Channel description only (fast)</option>
            <option value="VIDEOS_ONLY">Recent long-form video descriptions only</option>
            <option value="FULL">Channel + recent long-form videos (full)</option>
          </select>
        </div>

        <div className="space-y-2">
          <label className="flex items-center space-x-2">
            <input type="checkbox" checked={settings.language_enabled} onChange={(e) => setSettings({ ...settings, language_enabled: e.target.checked })} />
            <span>Language detection</span>
          </label>
          <select
            value={settings.language_mode}
            onChange={(e) => setSettings({ ...settings, language_mode: e.target.value as EnrichmentSettings['language_mode'] })}
            className="bg-gray-800 border border-gray-700 rounded-md p-2"
          >
            <option value="BASIC">Basic (fast)</option>
            <option value="PRECISE">Precise (slower, more accurate)</option>
          </select>
        </div>

        <div className="flex flex-col space-y-2">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={settings.refresh_channel_metadata}
              onChange={(e) => setSettings({ ...settings, refresh_channel_metadata: e.target.checked })}
            />
            <span>Refresh channel metadata</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={settings.update_last_upload}
              onChange={(e) => setSettings({ ...settings, update_last_upload: e.target.checked })}
            />
            <span>Update last upload/activity</span>
          </label>
        </div>

        <div className="flex justify-end space-x-3">
          <button className="px-4 py-2 rounded-md bg-gray-700" onClick={onClose}>
            Cancel
          </button>
          <button className="px-4 py-2 rounded-md bg-emerald-600" onClick={handleSave}>
            Save / Start enrichment
          </button>
        </div>
      </div>
    </Modal>
  )
}
