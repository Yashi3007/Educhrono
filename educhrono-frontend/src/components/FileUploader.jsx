import { useState } from "react";

const FileUploader = ({ label, onUpload, onDownloadTemplate }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUploadClick = async () => {
    if (!selectedFile) {
      alert("Please select a file before uploading.");
      return;
    }
    setUploading(true);
    try {
      await onUpload(selectedFile);
      setSelectedFile(null);
    } catch {
      alert("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
  };

  return (
    <div className="border rounded-lg p-5 shadow-sm bg-gray-50 hover:bg-gray-100 transition">
      <h4 className="text-lg font-semibold text-gray-700 mb-3">{label}</h4>

      <div className="flex flex-col sm:flex-row items-center gap-3">
        <input
          type="file"
          accept=".xlsx, .xls"
          onChange={handleFileChange}
          className="w-full sm:w-auto border border-gray-300 rounded-md p-2 text-sm"
        />

        <div className="flex gap-2">
          <button
            onClick={handleUploadClick}
            disabled={!selectedFile || uploading}
            className={`${
              uploading
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700"
            } text-white px-4 py-2 rounded-md text-sm`}
          >
            {uploading ? "Uploading..." : "Upload"}
          </button>

          <button
            onClick={handleReset}
            disabled={!selectedFile}
            className={`${
              selectedFile
                ? "bg-red-500 hover:bg-red-600"
                : "bg-gray-300 cursor-not-allowed"
            } text-white px-4 py-2 rounded-md text-sm`}
          >
            Reset
          </button>
        </div>
      </div>

      {/* File Preview */}
      {selectedFile && (
        <p className="text-sm mt-2 text-gray-600">
          Selected: <span className="font-medium">{selectedFile.name}</span>
        </p>
      )}

      {/* Template Download */}
      <div className="mt-3">
        <button
          onClick={onDownloadTemplate}
          className="text-blue-600 text-sm font-semibold hover:underline"
        >
          📥 Download Template
        </button>
      </div>
    </div>
  );
};

export default FileUploader;
