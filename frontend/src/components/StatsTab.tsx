import { useState, useEffect } from 'react'
import { BarChart3, File, Database, HardDrive, RefreshCw } from 'lucide-react'
import { getStatistics } from '../services/api'

export default function StatsTab() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    setLoading(true)
    try {
      const data = await getStatistics()
      setStats(data)
    } catch (error: any) {
      console.error('Load stats error:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <RefreshCw className="h-8 w-8 text-primary animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <BarChart3 className="h-6 w-6 text-primary" />
          <h2 className="text-xl font-semibold text-gray-900">统计信息</h2>
        </div>
        <button
          onClick={loadStats}
          className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center space-x-2"
        >
          <RefreshCw className="h-4 w-4" />
          <span>刷新</span>
        </button>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">总文件数</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {stats?.total_files || 0}
              </p>
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <File className="h-8 w-8 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">总向量数</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {stats?.total_vectors || 0}
              </p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <Database className="h-8 w-8 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">存储使用</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {formatBytes(stats?.storage_used || 0)}
              </p>
            </div>
            <div className="bg-purple-100 rounded-full p-3">
              <HardDrive className="h-8 w-8 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">文件类型</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {Object.keys(stats?.files_by_type || {}).length}
              </p>
            </div>
            <div className="bg-orange-100 rounded-full p-3">
              <BarChart3 className="h-8 w-8 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* 文件类型分布 */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-4">文件类型分布</h3>
        <div className="space-y-4">
          {stats?.files_by_type && Object.entries(stats.files_by_type).map(([type, count]: [string, any]) => {
            const total = stats.total_files || 1
            const percentage = ((count / total) * 100).toFixed(1)
            
            return (
              <div key={type}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700 capitalize">
                    {type}
                  </span>
                  <span className="text-sm text-gray-500">
                    {count} ({percentage}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary h-2 rounded-full transition-all duration-300"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            )
          })}
          
          {(!stats?.files_by_type || Object.keys(stats.files_by_type).length === 0) && (
            <p className="text-center text-gray-500 py-4">暂无数据</p>
          )}
        </div>
      </div>

      {/* 最后更新时间 */}
      {stats?.last_updated && (
        <div className="text-center text-sm text-gray-500">
          最后更新: {new Date(stats.last_updated).toLocaleString('zh-CN')}
        </div>
      )}
    </div>
  )
}
