import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if needed
    const token = localStorage.getItem('api_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data)
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message)
    } else {
      // Something else happened
      console.error('Error:', error.message)
    }
    return Promise.reject(error)
  }
)

// API methods
export const uploadFile = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/files/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  return response.data
}

export const search = async (params: {
  query?: string
  file_id?: string
  top_k?: number
  threshold?: number
}) => {
  const response = await api.post('/search', params)
  return response.data
}

export const getConfig = async () => {
  const response = await api.get('/config')
  return response.data
}

export const updateConfig = async (config: any) => {
  const response = await api.put('/config', config)
  return response.data
}

export const getHealth = async () => {
  const response = await api.get('/health')
  return response.data
}

export const getStatistics = async () => {
  const response = await api.get('/statistics')
  return response.data
}

export const deleteFile = async (fileId: string) => {
  const response = await api.delete(`/files/${fileId}`)
  return response.data
}

export const getAvailableModels = async () => {
  const response = await api.get('/models')
  return response.data
}

export const getAvailableDatabases = async () => {
  const response = await api.get('/databases')
  return response.data
}

export default api
