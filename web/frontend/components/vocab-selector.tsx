"use client";

import { useState, useEffect } from "react";
import { VocabInfo } from "@/types/api";
import { listVocabs } from "@/lib/api";

interface VocabSelectorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function VocabSelector({ value, onChange, disabled }: VocabSelectorProps) {
  const [vocabs, setVocabs] = useState<VocabInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadVocabs();
  }, []);

  const loadVocabs = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listVocabs();
      if (response.success) {
        setVocabs(response.vocabularies);
      } else {
        setError(response.message || "Failed to load vocabularies");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load vocabularies");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-900">📚 术语库 (可选)</h3>
        <button
          onClick={loadVocabs}
          disabled={loading || disabled}
          className="text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50"
        >
          {loading ? "加载中..." : "刷新"}
        </button>
      </div>

      {error && (
        <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {error}
        </div>
      )}

      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled || loading}
        className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <option value="">不使用术语库 (仅用AI翻译)</option>
        {vocabs.map((vocab) => (
          <option key={vocab.id} value={vocab.id}>
            {vocab.name} ({vocab.entry_count} 条术语)
          </option>
        ))}
      </select>

      {vocabs.length === 0 && !loading && (
        <p className="text-sm text-amber-600 mt-2">
          暂无术语库。你可以在下方"构建新术语库"区域上传词典文件构建。
        </p>
      )}

      <p className="text-sm text-gray-500 mt-2">
        选择术语库后，翻译时会优先使用术语库中的标准化翻译。
      </p>
    </div>
  );
}
