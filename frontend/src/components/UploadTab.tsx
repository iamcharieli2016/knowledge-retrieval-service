import { useState, useCallback } from 'react'
import { Upload, File, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { uploadFile } from '../services/api'

export default function UploadTab() {
  const [dragActive, setDragActive] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([])

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      await handleFiles(files)
    }
  }, [])

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (files.length > 0) {
      await handleFiles(files)
    }
  }

  const handleFiles = async (files: File[]) => {
    setUploading(true)
    
    for (const file of files) {
      try {
        const result = await uploadFile(file)
        setUploadedFiles(prev => [{
          ...result,
          name: file.name,
          size: file.size,
          status: 'success'
        }, ...prev])
      } catch (error: any) {
        setUploadedFiles(prev => [{
          name: file.name,
          size: file.size,
          status: 'error',
          error: error.response?.data?.detail || error.message
        }, ...prev])
      }
    }
    
    setUploading(false)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center transition-colors
          ${dragActive ? 'border-primary bg-blue-50' : 'border-gray-300'}
          ${uploading ? 'opacity-50 pointer-events-none' : ''}
        `}
      >
        <input
          type="file"
          multiple
          onChange={handleFileInput}
          className="hidden"
          id="file-upload"
          disabled={uploading}
        />
        <label htmlFor="file-upload" className="cursor-pointer">
          <div className="flex flex-col items-center space-y-4">
            <div className="bg-primary/10 rounded-full p-4">
              {uploading ? (
                <Loader2 className="h-12 w-12 text-primary animate-spin" />
              ) : (
                <Upload className="h-12 w-12 text-primary" />
              )}
            </div>
            <div>
              <p className="text-lg font-medium text-gray-900">
                {uploading ? '上传中...' : '拖拽文件到此处或点击上传'}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                支持图片、文档、视频、音频等多种格式
              </p>
            </div>
          </div>
        </label>
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">已上传文件</h3>
          <div className="space-y-2">
            {uploadedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
              >
                <div className="flex items-center space-x-3 flex-1">
                  <File className="h-8 w-8 text-gray-400" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.name || file.filename}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)} · {file.file_type}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {file.status === 'success' ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-500" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
