interface TargetColumnsInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function TargetColumnsInput({ value, onChange, disabled }: TargetColumnsInputProps) {
  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="font-semibold text-gray-900 mb-3">Target Columns (Optional)</h3>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder="e.g., 文件名, 页码, PO号, 品名, 数量, 单位"
        rows={2}
        className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <p className="text-sm text-gray-500 mt-2">
        Comma-separated list of columns to extract. Leave empty for auto-detection.
      </p>
    </div>
  );
}
