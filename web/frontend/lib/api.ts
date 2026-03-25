import { 
  ParseResponse, 
  VocabListResponse, 
  VocabBuildResponse,
  VocabDetail 
} from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

// ===== Parse API =====

export async function parseFile(
  file: File,
  options: {
    documentType: string;
    targetColumns: string;
    sceneDescription: string;
    translationRules: string;
    sheetTitle: string;
    vocabId: string;
  }
): Promise<ParseResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("document_type", options.documentType);
  formData.append("target_columns", options.targetColumns);
  formData.append("scene_description", options.sceneDescription);
  formData.append("translation_rules", options.translationRules);
  formData.append("sheet_title", options.sheetTitle);
  formData.append("vocab_id", options.vocabId);

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

// ===== Vocabulary API =====

export async function listVocabs(): Promise<VocabListResponse> {
  const response = await fetch(`${API_BASE}/vocab`, {
    method: "GET",
  });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json();
}

export async function getVocab(vocabId: string): Promise<VocabDetail> {
  const response = await fetch(`${API_BASE}/vocab/${vocabId}`, {
    method: "GET",
  });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json();
}

export async function deleteVocab(vocabId: string): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_BASE}/vocab/${vocabId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json();
}

export async function buildVocab(
  file: File,
  options: {
    name: string;
    description: string;
    extractionPrompt: string;
  }
): Promise<VocabBuildResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("name", options.name);
  formData.append("description", options.description);
  formData.append("extraction_prompt", options.extractionPrompt);

  const response = await fetch(`${API_BASE}/vocab/build`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json();
}
