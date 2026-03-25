const ALLOWED_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".txt"];
const MAX_FILE_SIZE = 200 * 1024 * 1024; // 200MB (increased for large dictionary files)

export function validateFile(file: File): string | null {
  const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    return `Unsupported file format: ${ext}. Allowed: ${ALLOWED_EXTENSIONS.join(", ")}`;
  }
  if (file.size > MAX_FILE_SIZE) {
    return `File too large: ${(file.size / 1024 / 1024).toFixed(2)}MB. Max: 20MB`;
  }
  if (file.size === 0) {
    return "File is empty";
  }
  return null;
}

export function validateSheetTitle(title: string): string | null {
  if (title.length > 50) {
    return "Sheet title must be 50 characters or less";
  }
  return null;
}
