interface DocumentTypeSelectProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function DocumentTypeSelect({ value, onChange, disabled }: DocumentTypeSelectProps) {
  const options = [
    { value: "auto_detect", label: "Auto Detect" },
    { value: "shipping_document", label: "Shipping Document" },
    { value: "invoice", label: "Invoice" },
    { value: "packing_list", label: "Packing List" },
    { value: "bill_of_lading", label: "Bill of Lading" },
    { value: "custom", label: "Custom" },
  ];

  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="font-semibold text-gray-900 mb-3">Document Type</h3>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      <p className="text-sm text-gray-500 mt-2">
        Select the document type for better extraction accuracy
      </p>
    </div>
  );
}
