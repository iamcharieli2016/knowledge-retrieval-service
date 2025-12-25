#!/bin/bash

echo "🚀 启动知识检索服务 - 前端"
echo "================================"

# 进入前端目录
cd "$(dirname "$0")/frontend"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装 Node.js 依赖..."
    npm install
else
    echo "✅ 依赖已安装"
fi

# 启动服务
echo ""
echo "✅ 准备完成！"
echo "🌐 启动前端开发服务器..."
echo "   访问地址: http://localhost:3000"
echo ""

npm run dev
