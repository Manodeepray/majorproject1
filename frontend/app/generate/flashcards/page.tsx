'use client';

import { useState } from 'react';
import { generateFlashcards } from '@/lib/api';
import type { FlashcardResponse, Flashcard } from '@/types/api';
import FileSelector from '@/components/FileSelector';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorAlert from '@/components/ErrorAlert';
import BackButton from '@/components/BackButton';

export default function FlashcardsPage() {
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [flashcards, setFlashcards] = useState<FlashcardResponse | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  const handleGenerate = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one file');
      return;
    }

    setLoading(true);
    setError(null);
    setFlashcards(null);
    setCurrentIndex(0);
    setIsFlipped(false);

    try {
      const response = await generateFlashcards(selectedFiles);
      setFlashcards(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate flashcards');
    } finally {
      setLoading(false);
    }
  };

  const currentCard = flashcards?.flashcards[currentIndex];

  const handleNext = () => {
    setCurrentIndex((prev) =>
      flashcards ? Math.min(flashcards.flashcards.length - 1, prev + 1) : prev
    );
    setIsFlipped(false);
  };

  const handlePrevious = () => {
    setCurrentIndex((prev) => Math.max(0, prev - 1));
    setIsFlipped(false);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <BackButton />
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Generate Flashcards</h1>
        <p className="text-gray-400">
          Create flashcards from your documents for studying
        </p>
      </div>

      {!flashcards ? (
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
              'Generate Flashcards'
            )}
          </button>

          {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold text-white">
              Card {currentIndex + 1} of {flashcards.flashcards.length}
            </h2>
            <p className="text-sm text-gray-400">
              Source: {currentCard?.source}
            </p>
          </div>

          <div className="relative h-96 perspective-1000">
            <div
              className={`relative w-full h-full transform-style-preserve-3d transition-transform duration-500 ${
                isFlipped ? 'rotate-y-180' : ''
              }`}
            >
              {/* Front of card */}
              <div
                className={`absolute inset-0 backface-hidden ${
                  !isFlipped ? 'rotate-y-0' : 'rotate-y-180'
                }`}
              >
                <div className="bg-gray-800 border-2 border-emerald-500 rounded-lg shadow-lg p-8 h-full flex flex-col justify-center items-center cursor-pointer"
                  onClick={() => setIsFlipped(true)}
                >
                  <div className="text-center">
                    <p className="text-sm text-gray-400 mb-4">Front</p>
                    <p className="text-2xl font-medium text-white">
                      {currentCard?.front}
                    </p>
                  </div>
                  <p className="text-xs text-gray-500 mt-8">Click to flip</p>
                </div>
              </div>

              {/* Back of card */}
              <div
                className={`absolute inset-0 backface-hidden ${
                  isFlipped ? 'rotate-y-0' : 'rotate-y-180'
                }`}
              >
                <div className="bg-emerald-900/30 border-2 border-emerald-500 rounded-lg shadow-lg p-8 h-full flex flex-col justify-center items-center cursor-pointer"
                  onClick={() => setIsFlipped(false)}
                >
                  <div className="text-center">
                    <p className="text-sm text-emerald-400 mb-4">Back</p>
                    <p className="text-2xl font-medium text-white">
                      {currentCard?.back}
                    </p>
                  </div>
                  <p className="text-xs text-emerald-500 mt-8">Click to flip</p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-center gap-4">
            <button
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              className="px-6 py-2 bg-gray-800 text-gray-300 rounded-lg hover:bg-gray-700 disabled:bg-gray-900 disabled:text-gray-600 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <button
              onClick={() => setIsFlipped(!isFlipped)}
              className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
            >
              {isFlipped ? 'Show Front' : 'Show Back'}
            </button>
            <button
              onClick={handleNext}
              disabled={currentIndex === flashcards.flashcards.length - 1}
              className="px-6 py-2 bg-gray-800 text-gray-300 rounded-lg hover:bg-gray-700 disabled:bg-gray-900 disabled:text-gray-600 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>

          <button
            onClick={() => {
              setFlashcards(null);
              setCurrentIndex(0);
              setIsFlipped(false);
            }}
            className="w-full px-4 py-2 bg-gray-800 text-gray-300 rounded-lg hover:bg-gray-700 transition-colors"
          >
            Generate New Flashcards
          </button>
        </div>
      )}
    </div>
  );
}

