"use client";

import { useRef } from "react";

interface FileUploadCardProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  disabled?: boolean;
}

export default function FileUploadCard({ file, onFileChange, disabled }: FileUploadCardProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    if (!disabled) {
      inputRef.current?.click();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0] || null;
    onFileChange(selectedFile);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (disabled) return;
    
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      onFileChange(droppedFile);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="font-semibold text-gray-900 mb-3">Upload File</h3>
      
      <div
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-colors
          ${disabled ? "opacity-50 cursor-not-allowed" : "hover:border-blue-500 hover:bg-blue-50"}
          ${file ? "border-green-500 bg-green-50" : "border-gray-300"}
        `}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={handleChange}
          disabled={disabled}
          className="hidden"
        />
        
        {file ? (
          <div>
            <div className="text-4xl mb-2">✓</div>
            <p className="font-medium text-gray-900">{file.name}</p>
            <p className="text-sm text-gray-500 mt-1">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        ) : (
          <div>
            <div className="text-4xl mb-2">📤</div>
            <p className="font-medium text-gray-900">Drop file here or click to upload</p>
            <p className="text-sm text-gray-500 mt-1">
              Supports PDF, PNG, JPG, JPEG
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
