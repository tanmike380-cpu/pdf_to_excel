interface DownloadButtonProps {
  downloadUrl: string;
}

export default function DownloadButton({ downloadUrl }: DownloadButtonProps) {
  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="font-semibold text-gray-900 mb-3">Download Excel</h3>
      <a
        href={downloadUrl}
        download
        className="inline-flex items-center gap-2 bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        Download Excel File
      </a>
    </div>
  );
}
