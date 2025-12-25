import { useState } from 'react'
import { Search, Loader2, FileText, Image, Video, Music } from 'lucide-react'
import { search } from '../services/api'

export default function SearchTab() {
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(10)
  const [threshold, setThreshold] = useState(0.0)  // 降低默认阈值，显示所有结果
  const [searching, setSearching] = useState(false)
  const [results, setResults] = useState<any[]>([])
  const [queryTime, setQueryTime] = useState(0)

  const handleSearch = async () => {
    if (!query.trim()) return

    setSearching(true)
    try {
      const response = await search({
        query,
        top_k: topK,
        threshold
      })
      setResults(response.results)
      setQueryTime(response.query_time)
    } catch (error: any) {
      console.error('Search error:', error)
      alert('搜索失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSearching(false)
    }
  }

  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case 'image':
        return <Image className="h-8 w-8 text-blue-500" />
      case 'document':
        return <FileText className="h-8 w-8 text-green-500" />
      case 'video':
        return <Video className="h-8 w-8 text-purple-500" />
      case 'audio':
        return <Music className="h-8 w-8 text-pink-500" />
      default:
        return <FileText className="h-8 w-8 text-gray-500" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Search Input */}
      <div className="space-y-4">
        <div className="flex space-x-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="输入搜索内容..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={searching}
          />
          <button
            onClick={handleSearch}
            disabled={searching || !query.trim()}
            className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {searching ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Search className="h-5 w-5" />
            )}
            <span>搜索</span>
          </button>
        </div>

        {/* Search Options */}
        <div className="flex space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              返回结果数 (Top K)
            </label>
            <input
              type="number"
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value))}
              min="1"
              max="100"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              相似度阈值
            </label>
            <input
              type="number"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              min="0"
              max="1"
              step="0.1"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              搜索结果 ({results.length})
            </h3>
            <p className="text-sm text-gray-500">
              查询时间: {(queryTime * 1000).toFixed(2)}ms
            </p>
          </div>
          <div className="space-y-3">
            {results.map((result, index) => (
              <div
                key={index}
                className="flex items-start space-x-4 p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
              >
                <div className="flex-shrink-0">
                  {getFileIcon(result.file_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {result.filename}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        类型: {result.file_type} · ID: {result.file_id}
                      </p>
                    </div>
                    <div className="ml-4 flex-shrink-0">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                        {(result.similarity * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {searching && (
        <div className="text-center py-12">
          <Loader2 className="h-12 w-12 text-primary animate-spin mx-auto" />
          <p className="mt-4 text-gray-600">搜索中...</p>
        </div>
      )}

      {!searching && results.length === 0 && query && (
        <div className="text-center py-12 text-gray-500">
          暂无搜索结果
        </div>
      )}
    </div>
  )
}
