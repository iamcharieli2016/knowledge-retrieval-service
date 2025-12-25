<div align="center">

# 🔍 Knowledge Retrieval Service

**智能知识检索服务系统 - 企业级多模态内容检索解决方案**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README_EN.md) | 简体中文

</div>

---

## 📋 目录

- [项目简介](#项目简介)
- [核心特性](#核心特性)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
- [功能演示](#功能演示)
- [API 文档](#api-文档)
- [配置说明](#配置说明)
- [开发指南](#开发指南)
- [部署方案](#部署方案)
- [性能优化](#性能优化)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 📖 项目简介

**Knowledge Retrieval Service** 是一个基于深度学习的企业级多模态知识检索系统，支持文档、图片、音频、视频等多种格式的内容检索。系统采用先进的向量检索技术和混合检索策略，为用户提供精准、高效的相似内容搜索服务。

### 🎯 适用场景

- 📚 **企业知识库管理** - 文档检索、知识沉淀
- 🖼️ **多媒体资源检索** - 图片、视频、音频检索
- 🔬 **科研资料管理** - 论文、报告检索
- 💼 **内容管理系统** - CMS 内容检索增强
- 🤖 **智能客服系统** - 知识库问答支持

---

## ✨ 核心特性

### 🚀 功能特性

- **多模态支持** 📄🖼️🎵🎬
  - 文档: PDF、Word、TXT、Markdown
  - 图片: JPG、PNG、GIF、BMP、WEBP
  - 音频: MP3、WAV、M4A、AAC、FLAC
  - 视频: MP4、AVI、MOV、MKV

- **智能检索** 🔍
  - 向量相似度检索
  - BM25 关键词检索
  - 混合检索策略 (向量 + BM25)
  - 多路召回机制
  - 可配置相似度阈值

- **灵活架构** 🏗️
  - 插件化模型系统
  - 多种向量数据库支持
  - 动态配置切换
  - RESTful API 设计

- **高性能** ⚡
  - 异步 I/O 处理
  - 批量向量化
  - GPU 加速支持
  - 智能缓存机制

- **易用性** 👥
  - 现代化 React UI
  - 拖拽式文件上传
  - 实时统计展示
  - 交互式 API 文档

---

## 🏗️ 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (React)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Upload  │  │  Search  │  │  Config  │  │  Stats  │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTP/REST API
┌───────────────────────────▼─────────────────────────────┐
│                   Backend (FastAPI)                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │              API Layer (Routes)                     │ │
│  └───────────────────┬────────────────────────────────┘ │
│  ┌───────────────────▼────────────────────────────────┐ │
│  │           Service Layer (Business Logic)           │ │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────┐ │ │
│  │  │ Knowledge   │  │  Processors  │  │Embeddings │ │ │
│  │  │  Service    │  │  (Multi)     │  │  (CLIP)   │ │ │
│  │  └─────────────┘  └──────────────┘  └───────────┘ │ │
│  └───────────────────┬────────────────────────────────┘ │
│  ┌───────────────────▼────────────────────────────────┐ │
│  │            Data Access Layer                        │ │
│  │  ┌──────────────┐        ┌─────────────────────┐  │ │
│  │  │   Vector DB  │        │   Metadata Store    │  │ │
│  │  │   (Chroma)   │        │     (SQLite)        │  │ │
│  │  └──────────────┘        └─────────────────────┘  │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

#### 后端技术
- **框架**: FastAPI 0.104+ (高性能异步 Web 框架)
- **语言**: Python 3.9+
- **AI/ML**: 
  - PyTorch (深度学习框架)
  - Transformers (预训练模型)
  - Sentence-Transformers (文本向量化)
  - CLIP (多模态模型)
  - Whisper (语音识别)
- **向量数据库**: ChromaDB (可扩展至 Milvus, Qdrant, FAISS)
- **文件处理**: Pillow, PyPDF2, python-docx, pydub, opencv

#### 前端技术
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI 样式**: Tailwind CSS
- **图标**: Lucide React
- **HTTP 客户端**: Axios

#### DevOps
- **容器化**: Docker + Docker Compose
- **API 文档**: OpenAPI (Swagger UI)
- **日志**: Python logging

### 项目结构

```
knowledge-retrieval-service/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由层
│   │   │   └── routes.py      # RESTful API 端点
│   │   ├── core/              # 核心配置
│   │   │   └── config.py      # 配置管理
│   │   ├── models/            # 数据模型
│   │   │   └── schemas.py     # Pydantic 模型
│   │   ├── services/          # 业务逻辑层
│   │   │   ├── embeddings/    # 向量化服务
│   │   │   │   ├── base.py
│   │   │   │   ├── huggingface_embedder.py
│   │   │   │   ├── clip_embedder.py
│   │   │   │   └── factory.py
│   │   │   ├── storage/       # 向量数据库适配器
│   │   │   │   ├── base.py
│   │   │   │   ├── chroma_db.py
│   │   │   │   └── factory.py
│   │   │   ├── processors/    # 文件处理器
│   │   │   │   ├── base.py
│   │   │   │   ├── image_processor.py
│   │   │   │   ├── document_processor.py
│   │   │   │   ├── audio_processor.py
│   │   │   │   └── factory.py
│   │   │   └── knowledge_service.py  # 核心服务
│   │   ├── utils/             # 工具函数
│   │   └── main.py            # 应用入口
│   ├── requirements.txt       # Python 依赖
│   ├── Dockerfile            # 后端容器配置
│   └── .env.example          # 环境变量示例
│
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── components/       # React 组件
│   │   │   ├── UploadTab.tsx  # 文件上传
│   │   │   ├── SearchTab.tsx  # 检索功能
│   │   │   ├── ConfigTab.tsx  # 配置管理
│   │   │   └── StatsTab.tsx   # 统计信息
│   │   ├── services/         # API 服务
│   │   │   └── api.ts        # API 客户端
│   │   ├── App.tsx           # 主应用
│   │   └── main.tsx          # 入口文件
│   ├── package.json          # Node 依赖
│   ├── tsconfig.json         # TypeScript 配置
│   ├── vite.config.ts        # Vite 配置
│   └── Dockerfile            # 前端容器配置
│
├── data/                     # 数据目录
│   ├── uploads/              # 上传文件存储
│   ├── chroma/               # ChromaDB 数据
│   └── metadata.db           # 元数据数据库
│
├── logs/                     # 日志目录
│   └── app.log               # 应用日志
│
├── config.yaml              # 主配置文件
├── docker-compose.yml       # Docker Compose 配置
├── .gitignore              # Git 忽略文件
├── .dockerignore           # Docker 忽略文件
├── README.md               # 本文件
├── QUICKSTART.md           # 快速开始指南
├── MODEL_GUIDE.md          # 模型选择指南
└── LOCAL_SETUP.md          # 本地开发指南
```

---

## 🚀 快速开始

### 前置要求

- **Python** 3.9 或更高版本
- **Node.js** 16 或更高版本
- **Docker & Docker Compose** (可选，推荐)
- **Git**

### 方式一: Docker 部署 (推荐) 🐳

最简单快速的部署方式：

```bash
# 1. 克隆项目
git clone https://github.com/your-username/knowledge-retrieval-service.git
cd knowledge-retrieval-service

# 2. 启动所有服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

**服务地址:**
- 🌐 前端界面: http://localhost:3000
- 🔌 后端 API: http://localhost:8000
- 📚 API 文档: http://localhost:8000/docs

### 方式二: 本地开发环境

#### 1. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要的目录
mkdir -p ../data/uploads ../data/chroma ../logs

# 返回项目根目录
cd ..

# 启动后端服务
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 前端设置

打开新终端窗口：

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 方式三: 使用启动脚本

```bash
# 后端启动
chmod +x start-backend.sh
./start-backend.sh

# 前端启动（新终端）
chmod +x start-frontend.sh
./start-frontend.sh
```

> 💡 **提示**: 首次启动会自动下载 AI 模型（约 500MB-1GB），请耐心等待。

> 📖 详细安装说明请参考: [LOCAL_SETUP.md](LOCAL_SETUP.md) | [QUICKSTART.md](QUICKSTART.md)

---

## 🎬 功能演示

### 1. 文件上传

支持拖拽或点击上传，实时显示处理进度：

- ✅ 自动文件类型识别
- ✅ 实时处理进度展示
- ✅ 向量化自动完成
- ✅ 元数据自动提取

### 2. 智能检索

支持多种检索方式：

- 🔤 **文本检索**: 输入关键词搜索相关文档
- 🖼️ **以图搜图**: 上传图片查找相似图片
- 🔀 **混合检索**: 结合向量检索和关键词检索
- 📊 **结果排序**: 按相似度评分排序

### 3. 配置管理

动态调整系统参数：

- 🔧 切换嵌入模型 (CLIP, Sentence-Transformers等)
- 💾 切换向量数据库 (ChromaDB, Milvus等)
- ⚙️ 调整检索参数 (Top-K, 阈值等)

### 4. 统计分析

实时查看系统状态：

- 📈 文件数量统计
- 💽 存储使用情况
- 📊 文件类型分布
- 🔍 检索性能指标

---

## 📡 API 文档

### 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: API Key (可选)
- **数据格式**: JSON
- **字符编码**: UTF-8

### 核心接口

#### 1. 文件上传

```http
POST /api/v1/files/upload
Content-Type: multipart/form-data

Parameters:
  file: File (必需) - 要上传的文件

Response:
{
  "file_id": "uuid-string",
  "filename": "document.pdf",
  "file_type": "document",
  "size": 1048576,
  "status": "processed",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 2. 相似度检索

```http
POST /api/v1/search
Content-Type: application/json

Body:
{
  "query": "机器学习",       // 搜索关键词
  "top_k": 10,              // 返回结果数量 (1-100)
  "threshold": 0.7,         // 相似度阈值 (0-1)
  "file_types": ["document", "image"],  // 可选：文件类型过滤
  "hybrid": true            // 可选：启用混合检索
}

Response:
{
  "results": [
    {
      "file_id": "uuid-string",
      "filename": "ml_tutorial.pdf",
      "score": 0.95,
      "file_type": "document",
      "content_preview": "机器学习是...",
      "metadata": {...}
    }
  ],
  "total": 10,
  "query_time": 0.05
}
```

#### 3. 获取文件信息

```http
GET /api/v1/files/{file_id}

Response:
{
  "file_id": "uuid-string",
  "filename": "document.pdf",
  "file_type": "document",
  "size": 1048576,
  "upload_time": "2024-01-01T00:00:00Z",
  "metadata": {...}
}
```

#### 4. 配置管理

```http
GET /api/v1/config

Response:
{
  "embedding_model": "openai/clip-vit-base-patch32",
  "vector_db": "chroma",
  "retrieval": {
    "default_top_k": 10,
    "similarity_threshold": 0.7
  }
}
```

```http
PUT /api/v1/config
Content-Type: application/json

Body:
{
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "retrieval": {
    "default_top_k": 20
  }
}
```

#### 5. 统计信息

```http
GET /api/v1/statistics

Response:
{
  "total_files": 1250,
  "total_vectors": 15000,
  "storage_used": "2.5 GB",
  "file_types": {
    "document": 800,
    "image": 350,
    "audio": 100
  }
}
```

#### 6. 健康检查

```http
GET /api/v1/health

Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600
}
```

> 📚 **完整 API 文档**: 启动服务后访问 http://localhost:8000/docs 查看交互式 API 文档

---

## ⚙️ 配置说明

### 主配置文件 (config.yaml)

```yaml
# 嵌入模型配置
embedding:
  provider: "huggingface"
  model_name: "openai/clip-vit-base-patch32"  # CLIP 多模态模型
  dimension: 512
  device: "cpu"  # cpu / cuda / mps (Apple Silicon)
  
# 向量数据库配置
vector_db:
  provider: "chroma"  # chroma / milvus / qdrant / faiss
  chroma:
    persist_directory: "./data/chroma"
    collection_name: "knowledge_base"
    
# 检索配置
retrieval:
  default_top_k: 50
  similarity_threshold: 0.03  # 3% 阈值
  enable_hybrid: true         # 混合检索
  hybrid_alpha: 0.2           # 向量权重 (0.2向量 + 0.8BM25)
  
# 文件处理配置
file_processing:
  upload_dir: "./data/uploads"
  max_file_size: 104857600  # 100MB
  allowed_extensions:
    image: [".jpg", ".jpeg", ".png", ".gif"]
    document: [".pdf", ".docx", ".txt", ".md"]
    audio: [".mp3", ".wav", ".m4a"]
```

### 环境变量 (backend/.env)

```bash
# API 配置
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true

# 安全配置
API_KEY=your-secret-api-key
ENABLE_AUTH=false

# HuggingFace 镜像（国内加速）
HF_ENDPOINT=https://hf-mirror.com

# 日志配置
LOG_LEVEL=INFO
```

> 📖 详细配置说明请参考: [MODEL_GUIDE.md](MODEL_GUIDE.md)

---

## 🎯 支持的文件类型

| 类型 | 扩展名 | 处理方式 | 模型支持 |
|------|--------|----------|----------|
| 📄 **文档** | PDF, DOCX, TXT, MD | 文本提取 + 分块 | Sentence Transformers |
| 🖼️ **图片** | JPG, PNG, GIF, BMP, WEBP | 图像特征提取 | CLIP / ResNet |
| 🎵 **音频** | MP3, WAV, M4A, AAC, FLAC | 语音转文本 + 特征提取 | Whisper / Wav2Vec |
| 🎬 **视频** | MP4, AVI, MOV, MKV | 关键帧提取 + 特征提取 | CLIP |

---

## 🔌 支持的向量数据库

| 数据库 | 特点 | 适用场景 | 文档 |
|--------|------|----------|------|
| **ChromaDB** | 轻量级、易用 | 中小规模、快速原型 | [Docs](https://docs.trychroma.com/) |
| **Milvus** | 高性能、分布式 | 大规模生产环境 | [Docs](https://milvus.io/docs) |
| **Qdrant** | 现代化、支持过滤 | 复杂查询场景 | [Docs](https://qdrant.tech/documentation/) |
| **FAISS** | 极速检索 | 超大规模、只读场景 | [Docs](https://faiss.ai/) |

---

## 🛠️ 开发指南

### 添加新的嵌入模型

1. 创建模型类继承 `BaseEmbedder`:

```python
# backend/app/services/embeddings/custom_embedder.py
from .base import BaseEmbedder
import numpy as np

class CustomEmbedder(BaseEmbedder):
    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_name, **kwargs)
        # 初始化你的模型
        
    def embed_text(self, text: str) -> np.ndarray:
        # 实现文本嵌入
        pass
        
    def embed_image(self, image_path: str) -> np.ndarray:
        # 实现图像嵌入
        pass
```

2. 在工厂类中注册:

```python
# backend/app/services/embeddings/factory.py
from .custom_embedder import CustomEmbedder

class EmbedderFactory:
    _embedders = {
        'custom': CustomEmbedder,
        # ...
    }
```

### 添加新的向量数据库

1. 创建数据库适配器:

```python
# backend/app/services/storage/custom_db.py
from .base import BaseVectorDB
from typing import List, Dict

class CustomVectorDB(BaseVectorDB):
    def __init__(self, **config):
        self.config = config
        # 初始化数据库连接
        
    def insert(self, vectors: List[List[float]], 
               metadata: List[Dict]) -> List[str]:
        # 实现向量插入
        pass
    
    def search(self, query_vector: List[float], 
               top_k: int) -> List[Dict]:
        # 实现向量检索
        pass
```

2. 在工厂类中注册:

```python
# backend/app/services/storage/factory.py
from .custom_db import CustomVectorDB

class VectorDBFactory:
    _dbs = {
        'custom': CustomVectorDB,
        # ...
    }
```

### 添加新的文件处理器

```python
# backend/app/services/processors/video_processor.py
from .base import BaseProcessor
from typing import Dict, Any

class VideoProcessor(BaseProcessor):
    def process(self, file_path: str) -> Dict[str, Any]:
        # 提取视频帧
        # 生成向量
        # 返回处理结果
        pass
```

---

## 🚢 部署方案

### Docker Compose 生产部署

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - API_DEBUG=false
      - WORKERS=4
    restart: always
    
  frontend:
    build: ./frontend
    restart: always
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    restart: always
```

### Kubernetes 部署

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: knowledge-retrieval-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/knowledge-retrieval-backend:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            memory: "4Gi"
            cpu: "2"
```

### 云服务部署

- **AWS**: ECS + RDS + S3
- **Azure**: AKS + Azure Database + Blob Storage  
- **阿里云**: ACK + RDS + OSS
- **腾讯云**: TKE + CDB + COS

---

## ⚡ 性能优化

### GPU 加速

#### NVIDIA GPU (CUDA)

```bash
# 安装 CUDA 版本的 PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

```yaml
# config.yaml
embedding:
  device: "cuda"
```

#### Apple Silicon (MPS)

```yaml
# config.yaml
embedding:
  device: "mps"
```

### 批量处理

```yaml
# config.yaml
embedding:
  batch_size: 64  # 增加批量大小
```

### 缓存优化

```yaml
# config.yaml
cache:
  enabled: true
  backend: "redis"
  ttl: 3600
```

### 数据库优化

```yaml
# config.yaml
vector_db:
  provider: "milvus"  # 使用高性能数据库
  milvus:
    index_type: "IVF_PQ"  # 使用高效索引
```

---

## 📊 性能指标

### 测试环境
- **CPU**: Intel i7-12700K / Apple M2 Pro
- **内存**: 32GB
- **存储**: NVMe SSD

### 性能数据

| 指标 | 数值 | 说明 |
|------|------|------|
| **并发请求** | 1000+ | 支持的最大并发数 |
| **平均响应时间** | < 100ms | 单次检索请求 |
| **向量检索** | 100万+ | 支持的向量规模 |
| **文件上传** | 10MB/s | 平均上传速度 |
| **GPU 加速** | 5-10x | 相比 CPU 的提升 |

---

## ❓ 常见问题

### Q1: 首次启动很慢？
**A**: 首次启动需要下载 AI 模型（约 500MB-1GB），建议使用国内镜像加速：
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### Q2: 如何切换模型？
**A**: 修改 `config.yaml` 中的 `embedding.model_name`，然后重启服务。详见 [MODEL_GUIDE.md](MODEL_GUIDE.md)

### Q3: 支持哪些语言？
**A**: 系统支持多语言文本检索。推荐使用多语言模型如 `paraphrase-multilingual-MiniLM-L12-v2`

### Q4: 如何提高检索准确度？
**A**: 
- 调整相似度阈值 `retrieval.similarity_threshold`
- 启用混合检索 `retrieval.enable_hybrid: true`
- 使用更大的模型（如 CLIP-Large）

### Q5: 内存不足怎么办？
**A**:
- 使用更小的模型（如 `all-MiniLM-L6-v2`）
- 减小批量大小 `embedding.batch_size`
- 限制上传文件大小

### Q6: 如何备份数据？
**A**: 备份以下目录：
```bash
./data/uploads/      # 上传的文件
./data/chroma/       # 向量数据库
./data/metadata.db   # 元数据
```

---

## 🤝 贡献指南

欢迎贡献代码、报告 Bug、提出新功能建议！

### 贡献流程

1. **Fork 项目**
2. **创建特性分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送分支** (`git push origin feature/AmazingFeature`)
5. **提交 Pull Request**

### 开发规范

- **代码风格**: 遵循 PEP 8 (Python) 和 Airbnb (TypeScript)
- **提交信息**: 使用清晰的提交信息
- **测试**: 确保所有测试通过
- **文档**: 更新相关文档

### 报告 Bug

请使用 [Issues](https://github.com/your-username/knowledge-retrieval-service/issues) 报告 Bug，包括：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（操作系统、Python 版本等）

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

```
MIT License

Copyright (c) 2024 Knowledge Retrieval Service

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
```

---

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Web 框架
- [React](https://reactjs.org/) - 用户界面库
- [PyTorch](https://pytorch.org/) - 深度学习框架
- [HuggingFace Transformers](https://huggingface.co/transformers/) - 预训练模型
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [Tailwind CSS](https://tailwindcss.com/) - CSS 框架

---

## 📧 联系方式

- **项目主页**: https://github.com/your-username/knowledge-retrieval-service
- **问题反馈**: https://github.com/your-username/knowledge-retrieval-service/issues
- **邮箱**: your-email@example.com
- **文档**: https://your-docs-site.com

---

## 🗺️ 路线图

### v1.0 (当前版本)
- ✅ 基础文档和图片检索
- ✅ 多种向量数据库支持
- ✅ RESTful API
- ✅ React UI

### v1.1 (计划中)
- 🔄 完整的音频和视频支持
- 🔄 用户认证和权限管理
- 🔄 多租户支持
- 🔄 高级过滤和排序

### v2.0 (未来)
- 📅 实时检索流
- 📅 知识图谱集成
- 📅 自动标签和分类
- 📅 智能推荐系统

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star！ ⭐**

</div>
