const ALLOWED_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".txt"];
const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB

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

export function validateTranslationRules(text: string): string[] {
  const errors: string[] = [];
  if (!text.trim()) return errors;
  
  const lines = text.trim().split("\n");
  lines.forEach((line, i) => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) return;
    if (!trimmed.includes("=")) {
      errors.push(`Line ${i + 1}: missing '=', expected format 'key=value'`);
    } else {
      const [key, ...rest] = trimmed.split("=");
      if (!key.trim()) {
        errors.push(`Line ${i + 1}: empty key`);
      }
      if (!rest.join("=").trim()) {
        errors.push(`Line ${i + 1}: empty value`);
      }
    }
  });
  return errors;
}

export function validateSheetTitle(title: string): string | null {
  if (title.length > 50) {
    return "Sheet title must be 50 characters or less";
  }
  return null;
}
