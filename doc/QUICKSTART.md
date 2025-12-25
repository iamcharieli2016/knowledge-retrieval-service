# 快速开始指南

## 📋 系统要求

- Python 3.9+
- Node.js 16+
- Docker & Docker Compose (可选)

## 🚀 快速启动

### 方式一：使用 Docker (推荐)

最简单的启动方式，一键启动所有服务：

```bash
# 1. 克隆或进入项目目录
cd knowledge-retrieval-service

# 2. 启动所有服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

服务地址：
- 前端界面: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 方式二：手动安装

#### 1. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制配置文件
cp .env.example .env

# 启动后端服务
cd ..
python -m backend.app.main
# 或使用 uvicorn
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 前端设置

在新的终端窗口中：

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 📝 基本使用

### 1. 上传文件

访问 http://localhost:3000，进入"上传文件"标签：

1. 点击或拖拽文件到上传区域
2. 支持的文件类型：
   - 图片: JPG, PNG, GIF, BMP, WEBP
   - 文档: PDF, DOCX, TXT, MD
   - 视频: MP4, AVI, MOV (待实现)
   - 音频: MP3, WAV, AAC (待实现)
3. 等待处理完成

### 2. 搜索内容

切换到"检索"标签：

1. 输入搜索关键词
2. 调整参数：
   - Top K: 返回结果数量 (1-100)
   - 相似度阈值: 过滤低相似度结果 (0-1)
3. 点击"搜索"按钮
4. 查看匹配结果和相似度分数

### 3. 查看统计

切换到"统计"标签查看：
- 总文件数
- 总向量数
- 存储使用量
- 文件类型分布

### 4. 配置管理

切换到"配置"标签进行设置：
- 更换嵌入模型
- 切换向量数据库
- 调整默认参数

## 🔧 配置说明

编辑 `config.yaml` 文件来自定义配置：

```yaml
# 嵌入模型
embedding:
  provider: "huggingface"
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cpu"  # 或 "cuda" for GPU

# 向量数据库
vector_db:
  provider: "chroma"  # chroma, milvus, qdrant, faiss
  
# 检索设置
retrieval:
  default_top_k: 10
  similarity_threshold: 0.7
```

## 🧪 API 测试

### 使用 curl

```bash
# 上传文件
curl -X POST http://localhost:8000/api/v1/files/upload \
  -F "file=@/path/to/your/file.pdf"

# 搜索
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "搜索内容",
    "top_k": 10,
    "threshold": 0.7
  }'

# 获取配置
curl http://localhost:8000/api/v1/config

# 健康检查
curl http://localhost:8000/api/v1/health
```

### 使用 Python

```python
import requests

# 上传文件
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/files/upload',
        files={'file': f}
    )
    print(response.json())

# 搜索
response = requests.post(
    'http://localhost:8000/api/v1/search',
    json={
        'query': '机器学习',
        'top_k': 5,
        'threshold': 0.8
    }
)
print(response.json())
```

## 📊 性能优化

### 使用 GPU 加速

编辑 `config.yaml`：

```yaml
embedding:
  device: "cuda"  # 使用 GPU
```

需要安装 PyTorch GPU 版本：

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 使用生产级数据库

对于大规模数据，建议使用 Milvus 或 Qdrant：

```yaml
vector_db:
  provider: "milvus"
  milvus:
    host: "localhost"
    port: 19530
```

## 🐛 故障排除

### 后端启动失败

1. 检查 Python 版本: `python --version` (需要 3.9+)
2. 确认所有依赖已安装: `pip list`
3. 查看日志文件: `logs/app.log`

### 前端启动失败

1. 检查 Node 版本: `node --version` (需要 16+)
2. 删除 node_modules 重新安装: `rm -rf node_modules && npm install`
3. 清除缓存: `npm cache clean --force`

### 模型下载慢

第一次运行会下载模型文件，可能需要几分钟。可以：

1. 使用代理
2. 手动下载模型并放到缓存目录
3. 使用更小的模型

### 内存不足

如果遇到内存问题：

1. 使用更小的模型
2. 减小 batch_size
3. 限制上传文件大小

## 📚 更多资源

- [完整文档](./README.md)
- [API 文档](http://localhost:8000/docs)
- [配置参考](./config.yaml)

## 💡 提示

1. 首次启动会下载模型，需要等待几分钟
2. GPU 加速可以显著提高处理速度
3. 建议使用 Docker 方式部署，更简单可靠
4. 生产环境请修改默认配置和密钥
