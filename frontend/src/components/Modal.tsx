import React, { ReactNode } from 'react'

interface ModalProps {
  open: boolean
  title: string
  onClose: () => void
  children: ReactNode
}

export const Modal: React.FC<ModalProps> = ({ open, title, onClose, children }) => {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 overflow-y-auto">
      <div className="bg-gray-900 rounded-lg shadow-xl w-full max-w-2xl mt-10 border border-gray-800">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          <button className="text-gray-400 hover:text-white" onClick={onClose}>
            ✕
          </button>
        </div>
        <div className="p-4 text-sm text-gray-200">{children}</div>
      </div>
    </div>
  )
}
