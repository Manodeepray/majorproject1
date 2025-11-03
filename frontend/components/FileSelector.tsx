'use client';

import { useState, useEffect } from 'react';
import { getFileStatus } from '@/lib/api';
import type { FileStatusResponse } from '@/types/api';
import LoadingSpinner from './LoadingSpinner';
import StatusBadge from './StatusBadge';

interface FileSelectorProps {
  selectedFiles: string[];
  onSelectionChange: (files: string[]) => void;
  multiple?: boolean;
}

export default function FileSelector({
  selectedFiles,
  onSelectionChange,
  multiple = true,
}: FileSelectorProps) {
  const [fileStatus, setFileStatus] = useState<FileStatusResponse>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const status = await getFileStatus();
        setFileStatus(status);
      } catch (err) {
        console.error('Failed to fetch file status:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchFiles();
  }, []);

  const processedFiles = Object.entries(fileStatus).filter(
    ([_, status]) => status.status === 'processed'
  );

  const handleToggle = (filename: string) => {
    if (multiple) {
      if (selectedFiles.includes(filename)) {
        onSelectionChange(selectedFiles.filter((f) => f !== filename));
      } else {
        onSelectionChange([...selectedFiles, filename]);
      }
    } else {
      onSelectionChange([filename]);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <LoadingSpinner />
      </div>
    );
  }

  if (processedFiles.length === 0) {
    return (
      <div className="bg-yellow-900/20 border border-yellow-800 rounded-lg p-4">
        <p className="text-yellow-300">
          No processed files available. Please upload and wait for files to be processed.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-white mb-2">
        Select Files {multiple && '(multiple selection)'}
      </label>
      <div className="border border-gray-700 rounded-lg divide-y divide-gray-700 max-h-64 overflow-y-auto bg-gray-800">
        {processedFiles.map(([filename, status]) => (
          <label
            key={filename}
            className="flex items-center px-4 py-3 hover:bg-gray-700 cursor-pointer"
          >
            <input
              type={multiple ? 'checkbox' : 'radio'}
              checked={selectedFiles.includes(filename)}
              onChange={() => handleToggle(filename)}
              className="rounded border-gray-600 bg-gray-800 text-emerald-600 focus:ring-emerald-500"
            />
            <div className="ml-3 flex-1">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-white">{filename}</span>
                <StatusBadge status={status.status} />
              </div>
            </div>
          </label>
        ))}
      </div>
      {selectedFiles.length > 0 && (
        <p className="text-sm text-gray-400 mt-2">
          {selectedFiles.length} file(s) selected
        </p>
      )}
    </div>
  );
}

