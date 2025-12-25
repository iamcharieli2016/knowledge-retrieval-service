import { useState } from 'react'
import { Upload, Search, Settings, BarChart3, Database, Brain } from 'lucide-react'
import UploadTab from './components/UploadTab'
import SearchTab from './components/SearchTab'
import ConfigTab from './components/ConfigTab'
import StatsTab from './components/StatsTab'

function App() {
  const [activeTab, setActiveTab] = useState('upload')

  const tabs = [
    { id: 'upload', name: '上传文件', icon: Upload },
    { id: 'search', name: '检索', icon: Search },
    { id: 'stats', name: '统计', icon: BarChart3 },
    { id: 'config', name: '配置', icon: Settings },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-primary rounded-lg p-2">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  知识检索服务
                </h1>
                <p className="text-sm text-gray-500">
                  Knowledge Retrieval Service
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Database className="h-5 w-5 text-green-500" />
              <span className="text-sm text-gray-600">在线</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      flex-1 flex items-center justify-center space-x-2 px-6 py-4
                      border-b-2 font-medium text-sm transition-colors
                      ${
                        activeTab === tab.id
                          ? 'border-primary text-primary bg-blue-50'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }
                    `}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{tab.name}</span>
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'upload' && <UploadTab />}
            {activeTab === 'search' && <SearchTab />}
            {activeTab === 'stats' && <StatsTab />}
            {activeTab === 'config' && <ConfigTab />}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            © 2024 Knowledge Retrieval Service. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
