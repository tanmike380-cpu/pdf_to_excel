// ===== Parse Types =====

export type ParseResponse = {
  success: boolean;
  preview_columns?: string[];
  preview_rows?: Record<string, string>[];
  warnings?: string[];
  missing_fields?: string[];
  download_id?: string;
  error_code?: string;
  message?: string;
};

export type ToolFormState = {
  file: File | null;
  documentType: string;
  targetColumnsText: string;
  sceneDescription: string;
  sheetTitle: string;
  // Vocabulary selection
  vocabId: string;
  // Legacy translation rules (optional override)
  translationRulesText: string;
};

export type ParseResultState = {
  status: "idle" | "uploading" | "processing" | "success" | "error";
  previewRows: Record<string, string>[];
  previewColumns: string[];
  downloadId?: string;
  warnings?: string[];
  errors?: string[];
};

// ===== Vocabulary Types =====

export type VocabEntry = {
  english: string;
  chinese: string;
  source?: string;
};

export type VocabInfo = {
  id: string;
  name: string;
  description: string;
  entry_count: number;
  created_at: string;
  file_name?: string;
};

export type VocabDetail = VocabInfo & {
  entries: VocabEntry[];
};

export type VocabListResponse = {
  success: boolean;
  vocabularies: VocabInfo[];
  message?: string;
};

export type VocabBuildResponse = {
  success: boolean;
  vocab_id?: string;
  entry_count?: number;
  preview_entries?: VocabEntry[];
  message?: string;
};

export type VocabBuildFormState = {
  file: File | null;
  name: string;
  description: string;
  extractionPrompt: string;
};

export type VocabBuildState = {
  status: "idle" | "uploading" | "building" | "success" | "error";
  vocabId?: string;
  entryCount?: number;
  previewEntries?: VocabEntry[];
  error?: string;
};
