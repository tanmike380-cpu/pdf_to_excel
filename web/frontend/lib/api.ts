import { ParseResponse } from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function parseFile(
  file: File,
  options: {
    documentType: string;
    targetColumns: string;
    sceneDescription: string;
    translationRules: string;
    sheetTitle: string;
  }
): Promise<ParseResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("document_type", options.documentType);
  formData.append("target_columns", options.targetColumns);
  formData.append("scene_description", options.sceneDescription);
  formData.append("translation_rules", options.translationRules);
  formData.append("sheet_title", options.sheetTitle);

  const response = await fetch(`${API_BASE}/parse`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json();
}

export function getDownloadUrl(fileId: string): string {
  return `${API_BASE}/download/${fileId}`;
}
