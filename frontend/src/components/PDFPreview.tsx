import { useState } from 'react'

interface PDFPreviewProps {
    file: File
    onClose: () => void
}

const PDFPreview = ({ file, onClose }: PDFPreviewProps) => {
    const [objectUrl] = useState(() => URL.createObjectURL(file))

    const handleClose = () => {
        URL.revokeObjectURL(objectUrl)
        onClose()
    }

    return (
        <div className="bg-primary-900/30  rounded-lg shadow-md p-4 mb-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-dark-primary">PDF Preview</h3>
                <button
                    onClick={handleClose}
                    className="text-gray-400 hover:text-gray-600 focus:outline-none"
                >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                </button>
            </div>

            <div className="border rounded-lg overflow-hidden">
                <iframe
                    src={objectUrl}
                    className="w-full h-96"
                    title={`Preview of ${file.name}`}
                />
            </div>

            <div className="mt-2 text-sm text-gray-600">
                <p><strong>File:</strong> {file.name}</p>
                <p><strong>Size:</strong> {(file.size / (1024 * 1024)).toFixed(2)} MB</p>
            </div>
        </div>
    )
}

export default PDFPreview