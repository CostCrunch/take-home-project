"use client";

import { UploadDialog } from "@/components/UploadDialog";

export default function Home() {
  const handleUploadComplete = () => {
    console.log("Upload completed!");
  };

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">
          CostCrunch File Upload Service
        </h1>
        <UploadDialog onUploadComplete={handleUploadComplete} />
      </div>
    </main>
  );
}
