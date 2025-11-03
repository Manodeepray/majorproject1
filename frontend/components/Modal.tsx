'use client';

import { useEffect } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
}

export default function Modal({
  isOpen,
  onClose,
  title,
  children,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
}: ModalProps) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleConfirm = () => {
    if (onConfirm) {
      onConfirm();
    }
    onClose();
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      onClick={onClose}
    >
      <div
        className="bg-gray-900 border border-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-6 py-4 border-b border-gray-800">
          <h2 className="text-xl font-semibold text-white">{title}</h2>
        </div>
        <div className="px-6 py-4">{children}</div>
        {(onConfirm || onCancel) && (
          <div className="px-6 py-4 border-t border-gray-800 flex justify-end gap-3">
            {onCancel && (
              <button
                onClick={handleCancel}
                className="px-4 py-2 text-gray-300 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors"
              >
                {cancelLabel}
              </button>
            )}
            {onConfirm && (
              <button
                onClick={handleConfirm}
                className="px-4 py-2 text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 transition-colors"
              >
                {confirmLabel}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

