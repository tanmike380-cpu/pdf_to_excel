"use client";

import { useState } from "react";
import { VocabBuildState, VocabBuildFormState, VocabEntry } from "@/types/api";
import { buildVocab } from "@/lib/api";

interface VocabBuilderProps {
  onBuildSuccess: (vocabId: string) => void;
  disabled?: boolean;
}

const DEFAULT_PROMPT = `这是一本船舶机电英语词典，请从中抽取所有的英文术语和对应的中文翻译。

抽取规则：
1. 每个条目必须包含英文术语和中文翻译
2. 保持原有大小写格式
3. 跳过纯中文或纯英文的条目
4. 优先抽取技术术语，跳过通用词汇`;

export default function VocabBuilder({ onBuildSuccess, disabled }: VocabBuilderProps) {
  const [expanded, setExpanded] = useState(false);
  const [form, setForm] = useState<VocabBuildFormState>({
    file: null,
    name: "",
    description: "",
    extractionPrompt: DEFAULT_PROMPT,
  });
  const [state, setState] = useState<VocabBuildState>({ status: "idle" });

  const handleFileChange = (file: File | null) => {
    setForm((prev) => ({ ...prev, file }));
    // Auto-fill name from filename
    if (file && !form.name) {
      const baseName = file.name.replace(/\.[^/.]+$/, "");
      setForm((prev) => ({ ...prev, name: baseName }));
    }
  };

  const handleBuild = async () => {
    if (!form.file || !form.name || !form.extractionPrompt) {
      setState({ status: "error", error: "请填写所有必填项" });
      return;
    }

    setState({ status: "uploading" });

    try {
      const response = await buildVocab(form.file, {
        name: form.name,
        description: form.description,
        extractionPrompt: form.extractionPrompt,
      });

      if (response.success && response.vocab_id) {
        setState({
          status: "success",
          vocabId: response.vocab_id,
          entryCount: response.entry_count,
          previewEntries: response.preview_entries,
        });
        onBuildSuccess(response.vocab_id);
      } else {
        setState({
          status: "error",
          error: response.message || "构建失败",
        });
      }
    } catch (e) {
      setState({
        status: "error",
        error: e instanceof Error ? e.message : "构建失败",
      });
    }
  };

  const handleReset = () => {
    setForm({
      file: null,
      name: "",
      description: "",
      extractionPrompt: DEFAULT_PROMPT,
    });
    setState({ status: "idle" });
    setExpanded(false);
  };

  if (!expanded) {
    return (
      <div className="bg-gray-50 rounded-lg border border-dashed border-gray-300 p-4">
        <button
          onClick={() => setExpanded(true)}
          disabled={disabled}
          className="w-full text-center text-gray-600 hover:text-gray-900 disabled:opacity-50"
        >
          <span className="text-lg">➕ 构建新术语库</span>
          <p className="text-sm mt-1">上传词典文件，用AI自动抽取术语对</p>
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">📖 构建新术语库</h3>
        <button
          onClick={handleReset}
          disabled={state.status === "uploading" || state.status === "building"}
          className="text-sm text-gray-500 hover:text-gray-700 disabled:opacity-50"
        >
          取消
        </button>
      </div>

      <div className="space-y-4">
        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            词典文件 <span className="text-red-500">*</span>
          </label>
          <div
            onClick={() => !disabled && document.getElementById("vocab-file-input")?.click()}
            className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
              ${form.file ? "border-green-500 bg-green-50" : "border-gray-300 hover:border-blue-500 hover:bg-blue-50"}
              ${disabled || state.status === "uploading" || state.status === "building" ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            <input
              id="vocab-file-input"
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.xlsx,.xls,.txt,.csv"
              onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
              className="hidden"
              disabled={disabled || state.status === "uploading" || state.status === "building"}
            />
            {form.file ? (
              <div>
                <div className="text-2xl">✅</div>
                <p className="font-medium text-gray-900">{form.file.name}</p>
                <p className="text-sm text-gray-500">{(form.file.size / 1024).toFixed(1)} KB</p>
              </div>
            ) : (
              <div>
                <div className="text-4xl mb-2">📤</div>
                <p className="font-medium text-gray-900">点击上传词典文件</p>
                <p className="text-sm text-gray-500 mt-1">支持 PDF, Excel, 图片, TXT, CSV</p>
              </div>
            )}
          </div>
        </div>

        {/* Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            术语库名称 <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={form.name}
            onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
            placeholder="例如：船舶机电术语库"
            disabled={disabled || state.status === "uploading" || state.status === "building"}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">描述 (可选)</label>
          <input
            type="text"
            value={form.description}
            onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
            placeholder="术语库用途说明"
            disabled={disabled || state.status === "uploading" || state.status === "building"}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
        </div>

        {/* Extraction Prompt */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            术语抽取规则 <span className="text-red-500">*</span>
          </label>
          <textarea
            value={form.extractionPrompt}
            onChange={(e) => setForm((prev) => ({ ...prev, extractionPrompt: e.target.value }))}
            rows={5}
            disabled={disabled || state.status === "uploading" || state.status === "building"}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <p className="text-sm text-gray-500 mt-1">
            描述如何从词典中抽取术语对。AI 会按照这个规则处理每一页。
          </p>
        </div>

        {/* Status */}
        {(state.status === "uploading" || state.status === "building") && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
            <div className="animate-pulse text-blue-600">
              {state.status === "uploading" ? "上传中..." : "正在抽取术语..."}
            </div>
            <p className="text-sm text-blue-500 mt-1">这可能需要几分钟，请耐心等待</p>
          </div>
        )}

        {state.status === "error" && state.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700 font-medium">构建失败</p>
            <p className="text-sm text-red-600 mt-1">{state.error}</p>
          </div>
        )}

        {state.status === "success" && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-700 font-medium">✅ 构建成功！</p>
            <p className="text-sm text-green-600 mt-1">
              共抽取 {state.entryCount} 条术语，已自动选择此术语库
            </p>
            {state.previewEntries && state.previewEntries.length > 0 && (
              <div className="mt-3 max-h-40 overflow-y-auto text-sm">
                <table className="w-full">
                  <thead className="text-gray-600 border-b">
                    <tr>
                      <th className="text-left py-1">英文</th>
                      <th className="text-left py-1">中文</th>
                    </tr>
                  </thead>
                  <tbody>
                    {state.previewEntries.slice(0, 10).map((entry, i) => (
                      <tr key={i} className="border-b border-gray-100">
                        <td className="py-1 pr-2">{entry.english}</td>
                        <td className="py-1">{entry.chinese}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Build Button */}
        {state.status !== "success" && (
          <button
            onClick={handleBuild}
            disabled={
              disabled ||
              !form.file ||
              !form.name ||
              !form.extractionPrompt ||
              state.status === "uploading" ||
              state.status === "building"
            }
            className={`w-full py-3 px-6 rounded-lg font-medium transition-colors
              ${
                !form.file || !form.name || !form.extractionPrompt
                  ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                  : "bg-blue-600 text-white hover:bg-blue-700"
              }
              ${state.status === "uploading" || state.status === "building" ? "animate-pulse" : ""}`}
          >
            {state.status === "uploading"
              ? "上传中..."
              : state.status === "building"
              ? "构建中..."
              : "开始构建术语库"}
          </button>
        )}
      </div>
    </div>
  );
}
