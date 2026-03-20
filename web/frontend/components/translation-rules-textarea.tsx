interface TranslationRulesTextareaProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function TranslationRulesTextarea({ value, onChange, disabled }: TranslationRulesTextareaProps) {
  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="font-semibold text-gray-900 mb-3">Translation Rules (Optional)</h3>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={`e.g., "PRESSURE GAUGE"="压力表"\\n"FIRE PUMP"="消防泵"`}
        rows={3}
        className="w-full border border-gray-300 rounded-lg px-4 py-2 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <p className="text-sm text-gray-500 mt-2">
        Custom translation rules (one per line, format: "English"="中文")
      </p>
    </div>
  );
}
