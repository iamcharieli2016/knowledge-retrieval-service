#!/bin/bash

echo "🚀 启动知识检索服务 - 后端"
echo "================================"

# 配置 HuggingFace 镜像（国内加速）
export HF_ENDPOINT=https://hf-mirror.com
echo "✓ 已配置 HuggingFace 镜像加速"

# 进入后端目录
cd "$(dirname "$0")/backend"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要的目录
echo "📁 创建数据目录..."
mkdir -p ../data/uploads
mkdir -p ../data/chroma
mkdir -p ../logs

# 启动服务
echo ""
echo "✅ 准备完成！"
echo "🌐 启动 FastAPI 服务..."
echo "   访问地址: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
