interface SceneDescriptionTextareaProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function SceneDescriptionTextarea({ value, onChange, disabled }: SceneDescriptionTextareaProps) {
  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="font-semibold text-gray-900 mb-3">Scene Description (Optional)</h3>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder="e.g., 这是招商工业港口物流单，内容多为船舶机电/消防系统/备件等术语"
        rows={2}
        className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <p className="text-sm text-gray-500 mt-2">
        Domain context to improve extraction accuracy
      </p>
    </div>
  );
}
