import React from "react";
import { UploadDialog } from "../components/UploadDialog";

function App() {
  const handleUploadComplete = () => {
    console.log("Upload completed!");
  };

  return (
    <div className="app">
      <h1>File Upload Service</h1>
      <UploadDialog onUploadComplete={handleUploadComplete} />
    </div>
  );
}

export default App;
