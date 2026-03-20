interface SheetTitleInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function SheetTitleInput({ value, onChange, disabled }: SheetTitleInputProps) {
  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="font-semibold text-gray-900 mb-3">Sheet Title</h3>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <p className="text-sm text-gray-500 mt-2">
        Title for the Excel sheet
      </p>
    </div>
  );
}
