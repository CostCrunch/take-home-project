"use client";

import { useState } from "react";
import { useDropzone } from "react-dropzone";

interface UploadDialogProps {
  onUploadComplete?: () => void;
}

interface ProcessedFile {
  filename: string;
  status: "uploading" | "completed" | "failed";
  message?: string;
}

export function UploadDialog({ onUploadComplete }: UploadDialogProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [processedFiles, setProcessedFiles] = useState<ProcessedFile[]>([]);

  // Bug 1: No file type validation
  const onDrop = (acceptedFiles: File[]) => {
    setSelectedFiles((prev) => [...prev, ...acceptedFiles]);
  };

  // Bug 2: No file removal functionality
  const removeFile = (fileToRemove: File) => {
    // TODO: Implement file removal
  };

  const handleSubmit = async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      // Bug 3: No file size check
      selectedFiles.forEach((file) => {
        formData.append("files", file);
      });

      // Bug 4: No proper error handling for network issues
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed with status ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("Response body is not readable");
      }

      // Bug 5: No proper progress tracking
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split("\n").filter((line) => line.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);

            // Bug 6: Inconsistent state updates
            if (data.type === "progress") {
              setProcessedFiles(data.processed_files);
            } else if (data.type === "complete") {
              // Bug 7: No cleanup after completion
              setProcessedFiles(data.files);
              setIsUploading(false);
              if (onUploadComplete) {
                onUploadComplete();
              }
            }
          } catch (e) {
            console.error("Error parsing chunk:", e);
          }
        }
      }
    } catch (error) {
      // Bug 8: Generic error message
      setError("Upload failed");
      setIsUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    // Bug 9: No file type restrictions
    // Bug 10: No multiple file handling configuration
  });

  return (
    <div className="upload-dialog">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? "active" : ""} ${
          isUploading ? "uploading" : ""
        }`}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the files here ...</p>
        ) : isUploading ? (
          <p>Upload in progress...</p>
        ) : (
          <p>Drag & drop files here, or click to select files</p>
        )}
      </div>

      {/* Bug 11: No file list display */}
      {selectedFiles.length > 0 && (
        <div className="selected-files">
          <h4 className="text-lg font-semibold mb-2">Selected Files:</h4>
          <ul>
            {selectedFiles.map((file) => (
              <li key={file.name} className="flex justify-between items-center">
                <span>{file.name}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Bug 12: No progress display */}
      {processedFiles.length > 0 && (
        <div className="processed-files">
          <h4 className="text-lg font-semibold mb-2">Processed Files:</h4>
          <ul>
            {processedFiles.map((file) => (
              <li key={file.filename}>
                {file.filename} - {file.status}
                {file.message && <span> ({file.message})</span>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {error && (
        // Bug 13: No error clearing functionality
        <div className="error">{error}</div>
      )}

      {/* Bug 14: No disabled state during upload */}
      <button
        onClick={handleSubmit}
        className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
      >
        {isUploading ? "Uploading..." : "Upload Files"}
      </button>
    </div>
  );
}
