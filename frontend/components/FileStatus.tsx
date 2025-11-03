'use client';

import { useState, useEffect } from 'react';
import { getFileStatus, deleteFiles } from '@/lib/api';
import type { FileStatusResponse } from '@/types/api';
import StatusBadge from './StatusBadge';
import LoadingSpinner from './LoadingSpinner';
import ErrorAlert from './ErrorAlert';
import Modal from './Modal';
import { HiDocumentText } from 'react-icons/hi';

interface FileStatusProps {
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export default function FileStatus({
  autoRefresh = true,
  refreshInterval = 5000,
}: FileStatusProps) {
  const [fileStatus, setFileStatus] = useState<FileStatusResponse>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const fetchFileStatus = async () => {
    try {
      setError(null);
      const status = await getFileStatus();
      setFileStatus(status);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch file status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFileStatus();

    if (autoRefresh) {
      const interval = setInterval(fetchFileStatus, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const handleSelectFile = (filename: string) => {
    setSelectedFiles((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(filename)) {
        newSet.delete(filename);
      } else {
        newSet.add(filename);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (selectedFiles.size === Object.keys(fileStatus).length) {
      setSelectedFiles(new Set());
    } else {
      setSelectedFiles(new Set(Object.keys(fileStatus)));
    }
  };

  const handleDelete = async () => {
    if (selectedFiles.size === 0) return;

    try {
      await deleteFiles(Array.from(selectedFiles));
      setSelectedFiles(new Set());
      setShowDeleteModal(false);
      await fetchFileStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete files');
    }
  };

  const processedCount = Object.values(fileStatus).filter(
    (item) => item.status === 'processed'
  ).length;
  const pendingCount = Object.values(fileStatus).filter(
    (item) => item.status === 'pending'
  ).length;
  const errorCount = Object.values(fileStatus).filter(
    (item) => item.status === 'error'
  ).length;

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}

      {Object.keys(fileStatus).length === 0 ? (
        <div className="text-center py-16">
          <HiDocumentText className="w-16 h-16 mx-auto text-gray-500 mb-4" />
          <p className="text-gray-300 mb-2 text-lg">Saved sources will appear here</p>
          <p className="text-sm text-gray-500 px-4">Click Add source above to add PDFs, websites, text, videos, or audio files. Or import a file directly from Google Drive.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {Object.entries(fileStatus).map(([filename, status]) => (
            <div
              key={filename}
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-800 transition-colors cursor-pointer group"
            >
              <input
                type="checkbox"
                checked={selectedFiles.has(filename)}
                onChange={(e) => {
                  e.stopPropagation();
                  handleSelectFile(filename);
                }}
                className="rounded border-gray-600 bg-gray-800 text-emerald-600 focus:ring-emerald-500 flex-shrink-0"
              />
              <div className="flex-1 min-w-0">
                <div className="text-sm text-gray-300 truncate">{filename}</div>
                <div className="flex items-center gap-2 mt-1">
                  <StatusBadge status={status.status} />
                  {status.timestamp && (
                    <span className="text-xs text-gray-500">
                      {new Date(status.timestamp).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
          {selectedFiles.size > 0 && (
            <div className="pt-4 border-t border-gray-800">
              <button
                onClick={() => setShowDeleteModal(true)}
                className="w-full px-4 py-2 text-sm bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Delete ({selectedFiles.size})
              </button>
            </div>
          )}
        </div>
      )}

      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Delete Files"
        onConfirm={handleDelete}
        confirmLabel="Delete"
        cancelLabel="Cancel"
      >
        <p className="text-gray-300">
          Are you sure you want to delete {selectedFiles.size} file(s)? This action
          cannot be undone.
        </p>
        <ul className="mt-4 list-disc list-inside text-sm text-gray-400">
          {Array.from(selectedFiles).map((filename) => (
            <li key={filename}>{filename}</li>
          ))}
        </ul>
      </Modal>
    </div>
  );
}

