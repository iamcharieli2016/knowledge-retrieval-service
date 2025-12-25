import { useState, useEffect } from 'react'
import { Settings, Save, RefreshCw } from 'lucide-react'
import { getConfig, updateConfig } from '../services/api'

export default function ConfigTab() {
  const [config, setConfig] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [embeddingModel, setEmbeddingModel] = useState('')
  const [vectorDbProvider, setVectorDbProvider] = useState('')
  const [defaultTopK, setDefaultTopK] = useState(10)
  const [threshold, setThreshold] = useState(0.7)

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    setLoading(true)
    try {
      const data = await getConfig()
      setConfig(data)
      setEmbeddingModel(data.embedding?.model_name || '')
      setVectorDbProvider(data.vector_db?.provider || '')
      setDefaultTopK(data.retrieval?.default_top_k || 10)
      setThreshold(data.retrieval?.similarity_threshold || 0.7)
    } catch (error: any) {
      console.error('Load config error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await updateConfig({
        embedding_model: embeddingModel,
        vector_db_provider: vectorDbProvider,
        default_top_k: defaultTopK,
        similarity_threshold: threshold
      })
      alert('配置已更新成功！')
      await loadConfig()
    } catch (error: any) {
      console.error('Update config error:', error)
      alert('更新失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSaving(false)
    }
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
          <Settings className="h-6 w-6 text-primary" />
          <h2 className="text-xl font-semibold text-gray-900">系统配置</h2>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 flex items-center space-x-2"
        >
          {saving ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <Save className="h-4 w-4" />
          )}
          <span>{saving ? '保存中...' : '保存配置'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 嵌入模型配置 */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">嵌入模型</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                模型名称
              </label>
              <input
                type="text"
                value={embeddingModel}
                onChange={(e) => setEmbeddingModel(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="sentence-transformers/all-MiniLM-L6-v2"
              />
              <p className="mt-1 text-xs text-gray-500">
                当前: {config?.embedding?.model_name}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                提供商
              </label>
              <p className="text-sm text-gray-600">
                {config?.embedding?.provider || 'N/A'}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                向量维度
              </label>
              <p className="text-sm text-gray-600">
                {config?.embedding?.dimension || 'N/A'}
              </p>
            </div>
          </div>
        </div>

        {/* 向量数据库配置 */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">向量数据库</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                数据库类型
              </label>
              <select
                value={vectorDbProvider}
                onChange={(e) => setVectorDbProvider(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              >
                <option value="chroma">ChromaDB</option>
                <option value="milvus">Milvus</option>
                <option value="qdrant">Qdrant</option>
                <option value="faiss">FAISS</option>
              </select>
              <p className="mt-1 text-xs text-gray-500">
                当前: {config?.vector_db?.provider}
              </p>
            </div>
          </div>
        </div>

        {/* 检索配置 */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">检索配置</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                默认返回数量 (Top K)
              </label>
              <input
                type="number"
                value={defaultTopK}
                onChange={(e) => setDefaultTopK(parseInt(e.target.value))}
                min="1"
                max="100"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
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

        {/* 服务信息 */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">服务信息</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                服务名称
              </label>
              <p className="text-sm text-gray-600">
                {config?.service?.name || 'N/A'}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                版本
              </label>
              <p className="text-sm text-gray-600">
                {config?.service?.version || 'N/A'}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                调试模式
              </label>
              <p className="text-sm text-gray-600">
                {config?.service?.debug ? '开启' : '关闭'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
