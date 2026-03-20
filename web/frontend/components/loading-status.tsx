interface LoadingStatusProps {
  status: string;
}

export default function LoadingStatus({ status }: LoadingStatusProps) {
  return (
    <div className="bg-blue-50 rounded-lg p-8 text-center">
      <div className="inline-flex items-center gap-3">
        <svg className="animate-spin h-6 w-6 text-blue-600" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        <span className="text-lg font-medium text-gray-900">{status}</span>
      </div>
      <p className="text-sm text-gray-500 mt-2">
        This may take a few minutes for large documents
      </p>
    </div>
  );
}
