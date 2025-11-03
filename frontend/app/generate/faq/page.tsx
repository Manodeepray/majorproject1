'use client';

import { useState } from 'react';
import { generateFAQ } from '@/lib/api';
import type { FAQResponse } from '@/types/api';
import FileSelector from '@/components/FileSelector';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorAlert from '@/components/ErrorAlert';
import BackButton from '@/components/BackButton';

export default function FAQPage() {
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [faqs, setFaqs] = useState<FAQResponse | null>(null);
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const handleGenerate = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one file');
      return;
    }

    setLoading(true);
    setError(null);
    setFaqs(null);

    try {
      const response = await generateFAQ(selectedFiles);
      setFaqs(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate FAQs');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <BackButton />
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Generate FAQ</h1>
        <p className="text-gray-400">
          Generate frequently asked questions from your documents
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
            'Generate FAQs'
          )}
        </button>

        {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}

        {faqs && faqs.faqs.length > 0 && (
          <div className="mt-6 border-t border-gray-800 pt-6">
            <h2 className="text-xl font-semibold text-white mb-4">
              Generated FAQs ({faqs.faqs.length})
            </h2>
            <div className="space-y-3">
              {faqs.faqs.map((faq, index) => (
                <div
                  key={index}
                  className="border border-gray-700 rounded-lg overflow-hidden bg-gray-800"
                >
                  <button
                    onClick={() => setOpenIndex(openIndex === index ? null : index)}
                    className="w-full px-4 py-3 text-left bg-gray-800 hover:bg-gray-700 transition-colors flex justify-between items-center"
                  >
                    <span className="font-medium text-white">{faq.question}</span>
                    <svg
                      className={`w-5 h-5 text-gray-500 transition-transform ${
                        openIndex === index ? 'transform rotate-180' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </button>
                  {openIndex === index && (
                    <div className="px-4 py-3 bg-gray-900 border-t border-gray-700">
                      <p className="text-gray-200 whitespace-pre-wrap mb-2">{faq.answer}</p>
                      <p className="text-xs text-gray-400">
                        Source: <span className="font-medium text-gray-300">{faq.source}</span>
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

