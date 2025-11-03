'use client';

import Link from 'next/link';

export default function BackButton() {
  return (
    <Link
      href="/"
      className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4"
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
      <span>Back to Dashboard</span>
    </Link>
  );
}


