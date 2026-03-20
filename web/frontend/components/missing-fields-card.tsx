interface MissingFieldsCardProps {
  fields: string[];
}

export default function MissingFieldsCard({ fields }: MissingFieldsCardProps) {
  if (!fields.length) return null;

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
      <div className="flex items-start gap-3">
        <div className="text-2xl">⚠️</div>
        <div className="flex-1">
          <h3 className="font-semibold text-yellow-900 mb-2">Missing Fields</h3>
          <p className="text-sm text-yellow-700">
            The following fields were not found in the document: {fields.join(", ")}
          </p>
        </div>
      </div>
    </div>
  );
}
