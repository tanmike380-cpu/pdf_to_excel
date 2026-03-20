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
  translationRulesText: string;
  sheetTitle: string;
};

export type ParseResultState = {
  status: "idle" | "uploading" | "processing" | "success" | "error";
  previewRows: Record<string, string>[];
  previewColumns: string[];
  downloadId?: string;
  warnings?: string[];
  errors?: string[];
};
