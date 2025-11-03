'use client';

import { useState } from 'react';
import { generateOutline } from '@/lib/api';
import type { OutlineResponse } from '@/types/api';
import FileSelector from '@/components/FileSelector';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorAlert from '@/components/ErrorAlert';
import BackButton from '@/components/BackButton';

export default function OutlinePage() {
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [combine, setCombine] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [outline, setOutline] = useState<OutlineResponse | null>(null);

  const handleGenerate = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one file');
      return;
    }

    setLoading(true);
    setError(null);
    setOutline(null);

    try {
      const response = await generateOutline(selectedFiles, combine);
      setOutline(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate outline');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <BackButton />
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Generate Outline</h1>
        <p className="text-gray-400">
          Generate hierarchical outlines from your documents
        </p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-6">
        <FileSelector
          selectedFiles={selectedFiles}
          onSelectionChange={setSelectedFiles}
          multiple={true}
        />

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="combine"
            checked={combine}
            onChange={(e) => setCombine(e.target.checked)}
            className="rounded border-gray-600 bg-gray-800 text-emerald-600 focus:ring-emerald-500"
          />
          <label htmlFor="combine" className="text-sm text-white">
            Combine outlines into a single hierarchical outline
          </label>
        </div>

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
            'Generate Outline'
          )}
        </button>

        {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}

        {outline && (
          <div className="mt-6 border-t border-gray-800 pt-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-white">Generated Outline</h2>
              <button
                onClick={() => {
                  const text = outline.combined_outline
                    ? outline.combined_outline
                    : Object.values(outline.individual_outlines || {}).join('\n\n');
                  copyToClipboard(text);
                }}
                className="text-sm text-emerald-400 hover:text-emerald-300"
              >
                Copy to Clipboard
              </button>
            </div>

            {outline.combined_outline ? (
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <pre className="whitespace-pre-wrap text-sm text-gray-200 font-mono">
                  {outline.combined_outline}
                </pre>
              </div>
            ) : (
              <div className="space-y-4">
                {Object.entries(outline.individual_outlines || {}).map(([filename, outlineText]) => (
                  <div key={filename} className="border border-gray-700 rounded-lg p-4 bg-gray-800">
                    <h3 className="text-lg font-medium text-white mb-2">{filename}</h3>
                    <div className="flex justify-end mb-2">
                      <button
                        onClick={() => copyToClipboard(outlineText)}
                        className="text-xs text-emerald-400 hover:text-emerald-300"
                      >
                        Copy
                      </button>
                    </div>
                    <pre className="whitespace-pre-wrap text-sm text-gray-200 font-mono bg-gray-900 rounded p-3">
                      {outlineText}
                    </pre>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

