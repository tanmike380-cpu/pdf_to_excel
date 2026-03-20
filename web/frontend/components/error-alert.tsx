interface ErrorAlertProps {
  errors: string[];
}

export default function ErrorAlert({ errors }: ErrorAlertProps) {
  if (!errors.length) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6">
      <div className="flex items-start gap-3">
        <div className="text-2xl">⚠️</div>
        <div className="flex-1">
          <h3 className="font-semibold text-red-900 mb-2">Errors</h3>
          <ul className="list-disc list-inside space-y-1">
            {errors.map((error, idx) => (
              <li key={idx} className="text-sm text-red-700">
                {error}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
