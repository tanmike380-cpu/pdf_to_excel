interface ResultTableProps {
  columns: string[];
  rows: Record<string, string>[];
}

export default function ResultTable({ columns, rows }: ResultTableProps) {
  if (!columns.length || !rows.length) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="font-semibold text-gray-900 mb-3">
        Preview ({rows.length} rows)
      </h3>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {rows.slice(0, 10).map((row, rowIdx) => (
              <tr key={rowIdx} className={rowIdx % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                {columns.map((col, colIdx) => (
                  <td key={colIdx} className="px-4 py-2 text-sm text-gray-900 whitespace-nowrap">
                    {row[col] || ""}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rows.length > 10 && (
        <p className="text-sm text-gray-500 mt-2">
          Showing first 10 rows of {rows.length} total
        </p>
      )}
    </div>
  );
}
