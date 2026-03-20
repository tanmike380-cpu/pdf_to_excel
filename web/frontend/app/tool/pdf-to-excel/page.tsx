"use client";

import { useState } from "react";
import Header from "@/components/header";
import FileUploadCard from "@/components/file-upload-card";
import DocumentTypeSelect from "@/components/document-type-select";
import TargetColumnsInput from "@/components/target-columns-input";
import SceneDescriptionTextarea from "@/components/scene-description-textarea";
import TranslationRulesTextarea from "@/components/translation-rules-textarea";
import SheetTitleInput from "@/components/sheet-title-input";
import SubmitButton from "@/components/submit-button";
import ResultTable from "@/components/result-table";
import DownloadButton from "@/components/download-button";
import ErrorAlert from "@/components/error-alert";
import MissingFieldsCard from "@/components/missing-fields-card";
import LoadingStatus from "@/components/loading-status";
import { ToolFormState, ParseResultState } from "@/types/api";
import { parseFile, getDownloadUrl } from "@/lib/api";
import { validateFile, validateTranslationRules, validateSheetTitle } from "@/lib/validators";

export default function ToolPage() {
  const [form, setForm] = useState<ToolFormState>({
    file: null,
    documentType: "auto_detect",
    targetColumnsText: "",
    sceneDescription: "",
    translationRulesText: "",
    sheetTitle: "Extraction Result",
  });

  const [result, setResult] = useState<ParseResultState>({
    status: "idle",
    previewRows: [],
    previewColumns: [],
  });

  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const handleFileChange = (file: File | null) => {
    setForm((prev) => ({ ...prev, file }));
    setValidationErrors([]);
    setResult({ status: "idle", previewRows: [], previewColumns: [] });
  };

  const handleSubmit = async () => {
    // Validate
    const errors: string[] = [];

    if (!form.file) {
      errors.push("Please upload a file");
    } else {
      const fileError = validateFile(form.file);
      if (fileError) errors.push(fileError);
    }

    const ruleErrors = validateTranslationRules(form.translationRulesText);
    errors.push(...ruleErrors);

    const titleError = validateSheetTitle(form.sheetTitle);
    if (titleError) errors.push(titleError);

    if (errors.length > 0) {
      setValidationErrors(errors);
      return;
    }

    // Submit
    setValidationErrors([]);
    setResult({ status: "uploading", previewRows: [], previewColumns: [] });

    try {
      setResult((prev) => ({ ...prev, status: "processing" }));

      const response = await parseFile(form.file!, {
        documentType: form.documentType,
        targetColumns: form.targetColumnsText,
        sceneDescription: form.sceneDescription,
        translationRules: form.translationRulesText,
        sheetTitle: form.sheetTitle,
      });

      if (response.success) {
        setResult({
          status: "success",
          previewColumns: response.preview_columns || [],
          previewRows: response.preview_rows || [],
          downloadId: response.download_id,
          warnings: response.warnings,
          errors: response.missing_fields?.map((f) => `Field "${f}" not found in document`),
        });
      } else {
        setResult({
          status: "error",
          previewRows: [],
          previewColumns: [],
          errors: [response.message || "Extraction failed"],
        });
      }
    } catch (error) {
      setResult({
        status: "error",
        previewRows: [],
        previewColumns: [],
        errors: [error instanceof Error ? error.message : "An unexpected error occurred"],
      });
    }
  };

  const handleReset = () => {
    setForm({
      file: null,
      documentType: "auto_detect",
      targetColumnsText: "",
      sceneDescription: "",
      translationRulesText: "",
      sheetTitle: "Extraction Result",
    });
    setResult({ status: "idle", previewRows: [], previewColumns: [] });
    setValidationErrors([]);
  };

  return (
    <div className="min-h-screen">
      <Header />
      <main className="py-8 px-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold mb-6 text-gray-900">PDF to Excel Extractor</h1>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left: Input */}
            <div className="space-y-6">
              <FileUploadCard
                file={form.file}
                onFileChange={handleFileChange}
                disabled={result.status === "uploading" || result.status === "processing"}
              />

              <DocumentTypeSelect
                value={form.documentType}
                onChange={(v) => setForm((prev) => ({ ...prev, documentType: v }))}
                disabled={result.status === "uploading" || result.status === "processing"}
              />

              <TargetColumnsInput
                value={form.targetColumnsText}
                onChange={(v) => setForm((prev) => ({ ...prev, targetColumnsText: v }))}
                disabled={result.status === "uploading" || result.status === "processing"}
              />

              <SceneDescriptionTextarea
                value={form.sceneDescription}
                onChange={(v) => setForm((prev) => ({ ...prev, sceneDescription: v }))}
                disabled={result.status === "uploading" || result.status === "processing"}
              />

              <TranslationRulesTextarea
                value={form.translationRulesText}
                onChange={(v) => setForm((prev) => ({ ...prev, translationRulesText: v }))}
                disabled={result.status === "uploading" || result.status === "processing"}
              />

              <SheetTitleInput
                value={form.sheetTitle}
                onChange={(v) => setForm((prev) => ({ ...prev, sheetTitle: v }))}
                disabled={result.status === "uploading" || result.status === "processing"}
              />

              <SubmitButton
                onClick={handleSubmit}
                disabled={!form.file || result.status === "uploading" || result.status === "processing"}
                loading={result.status === "uploading" || result.status === "processing"}
              />

              {result.status === "success" && (
                <button
                  onClick={handleReset}
                  className="w-full py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Start Over
                </button>
              )}
            </div>

            {/* Right: Output */}
            <div className="space-y-6">
              {result.status === "uploading" && <LoadingStatus status="Uploading file..." />}
              {result.status === "processing" && <LoadingStatus status="Extracting and translating..." />}

              {validationErrors.length > 0 && <ErrorAlert errors={validationErrors} />}

              {result.status === "error" && result.errors && (
                <ErrorAlert errors={result.errors} />
              )}

              {result.status === "success" && (
                <>
                  {result.warnings && result.warnings.length > 0 && (
                    <MissingFieldsCard fields={result.warnings} />
                  )}

                  {result.previewColumns.length > 0 && (
                    <ResultTable columns={result.previewColumns} rows={result.previewRows} />
                  )}

                  {result.downloadId && <DownloadButton downloadUrl={getDownloadUrl(result.downloadId)} />}
                </>
              )}

              {result.status === "idle" && (
                <div className="bg-gray-100 rounded-lg p-8 text-center text-gray-500">
                  <p>Upload a file and click "Extract Data" to see results</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
