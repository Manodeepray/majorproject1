import type { FileStatusItem } from '@/types/api';

interface StatusBadgeProps {
  status: FileStatusItem['status'];
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const statusConfig: Record<string, { bg: string; text: string; label: string }> = {
    processed: {
      bg: 'bg-emerald-900/30',
      text: 'text-emerald-300',
      label: 'Processed',
    },
    pending: {
      bg: 'bg-yellow-900/30',
      text: 'text-yellow-300',
      label: 'Pending',
    },
    error: {
      bg: 'bg-red-900/30',
      text: 'text-red-300',
      label: 'Error',
    },
  };

  const config = statusConfig[status] || {
    bg: 'bg-gray-800',
    text: 'text-gray-300',
    label: status || 'Unknown',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}
    >
      {config.label}
    </span>
  );
}

