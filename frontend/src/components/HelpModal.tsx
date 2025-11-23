import React from 'react'
import { Modal } from './Modal'

interface HelpModalProps {
  open: boolean
  onClose: () => void
}

export const HelpModal: React.FC<HelpModalProps> = ({ open, onClose }) => (
  <Modal open={open} onClose={onClose} title="Help & FAQ">
    <div className="space-y-3 leading-relaxed">
      <p>
        Discovery scrapes YouTube search results for your keywords. It extracts video cards, resolves their channel IDs, and
        inserts new channels into SQLite for mass harvesting.
      </p>
      <p>
        Each keyword maintains its own continuation token and exhaustion counter. When several pages yield no fresh channels,
        the keyword is marked as exhausted until you restart discovery.
      </p>
      <p>
        Enrichment loads channel about pages and recent long-form videos, refreshing metadata, last upload timestamps, emails,
        Telegram handles, and language heuristics.
      </p>
      <ul className="list-disc list-inside space-y-2 text-gray-200">
        <li>Emails are pulled from about pages, links, and recent video descriptions.</li>
        <li>Telegram handles are normalized into @handles regardless of whether links or plain text were found.</li>
        <li>Language detection supports fast (basic) and precise (uses video titles) modes.</li>
        <li>Filters can blacklist channels with too few subscribers, no long-form videos, stale uploads, or denied languages.</li>
      </ul>
      <div className="space-y-1 text-gray-300">
        <p><strong>Why are some channels blacklisted?</strong> They violated one of the configured filters when discovered.</p>
        <p><strong>Why do Hindi channels appear?</strong> Disable Hindi in deny languages and rerun discovery or blacklist manually.</p>
        <p><strong>Why is an email missing?</strong> It may be obfuscated or lives in older uploads; rerun enrichment in FULL mode.</p>
        <p><strong>How do I backup data?</strong> Export a bundle from Import/Export; you can import it later to restore.</p>
      </div>
    </div>
  </Modal>
)
