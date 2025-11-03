'use client';

import { useState } from 'react';
import { summarize } from '@/lib/api';
import type { SummarizeResponse } from '@/types/api';
import FileSelector from '@/components/FileSelector';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorAlert from '@/components/ErrorAlert';
import BackButton from '@/components/BackButton';

export default function SummarizePage() {
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [summaries, setSummaries] = useState<SummarizeResponse | null>(null);

  const handleGenerate = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one file');
      return;
    }

    setLoading(true);
    setError(null);
    setSummaries(null);

    try {
      const response = await summarize(selectedFiles);
      setSummaries(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate summaries');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <BackButton />
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Summarize Documents</h1>
        <p className="text-gray-400">
          Generate summaries for your uploaded documents
        </p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-6">
        <FileSelector
          selectedFiles={selectedFiles}
          onSelectionChange={setSelectedFiles}
          multiple={true}
        />

        <button
          onClick={handleGenerate}
          disabled={loading || selectedFiles.length === 0}
          className="w-full bg-emerald-600 text-white py-2 px-4 rounded-lg hover:bg-emerald-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
        >
          {loading ? (
            <>
              <LoadingSpinner size="sm" />
              <span className="ml-2">Generating...</span>
            </>
          ) : (
            'Generate Summaries'
          )}
        </button>

        {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}

        {summaries && summaries.summaries.length > 0 && (
          <div className="mt-6 border-t border-gray-800 pt-6">
            <h2 className="text-xl font-semibold text-white mb-4">Generated Summaries</h2>
            <div className="space-y-4">
              {summaries.summaries.map((item) => (
                <div key={item.filename} className="border border-gray-700 rounded-lg p-4 bg-gray-800">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="text-lg font-medium text-white">{item.filename}</h3>
                    <button
                      onClick={() => copyToClipboard(item.summary)}
                      className="text-sm text-emerald-400 hover:text-emerald-300"
                    >
                      Copy
                    </button>
                  </div>
                  <div className="bg-gray-900 rounded-lg p-4">
                    <p className="text-gray-200 whitespace-pre-wrap">{item.summary}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

