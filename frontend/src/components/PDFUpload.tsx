import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

interface PDFUploadProps {
  onFileSelect: (file: File) => void
  loading?: boolean
  disabled?: boolean
}

const PDFUpload = ({ onFileSelect, loading = false, disabled = false }: PDFUploadProps) => {
  const [fileName, setFileName] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFileName(acceptedFiles[0].name)
      onFileSelect(acceptedFiles[0])
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
    disabled: disabled || loading,
    noClick: true, // Required to use open()
    noKeyboard: true,
  })

  return (
    <div className="space-y-4">
      {/* Dropzone Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center transition-colors
          ${isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${disabled || loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        <input {...getInputProps()} />

        <div className={`text-gray-400 ${isDragActive ? 'text-blue-500' : ''}`}>
          {loading ? (
            <div className="flex justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
              <path 
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round" 
              />
            </svg>
          )}
        </div>

        <div>
          {loading ? (
            <p className="text-gray-600">Processing PDF...</p>
          ) : isDragActive ? (
            <p className="text-blue-600 font-medium">Drop the PDF file here</p>
          ) : (
            <>
              <p className="text-gray-600">Drag and drop your PDF file here</p>
              <p className="text-sm text-gray-500 mt-2">PDF files up to 10MB</p>
            </>
          )}
        </div>
      </div>

      {/* Choose File Button */}
      {!loading && (
        <div className="text-center">
          <button
            type="button"
            onClick={open} // <-- THIS now works
            className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={disabled}
          >
            Choose File
          </button>
          {fileName && <p className="text-sm text-green-600 mt-2">Selected: {fileName}</p>}
        </div>
      )}
    </div>
  )
}

export default PDFUpload
