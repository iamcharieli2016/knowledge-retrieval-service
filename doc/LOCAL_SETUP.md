# 本地开发环境设置指南

## 📋 前置要求

确保您已安装：
- **Python 3.9+** - `python3 --version`
- **Node.js 16+** - `node --version`
- **npm** - `npm --version`

## 🚀 快速启动

### 方式一：使用启动脚本（推荐）

#### 1. 启动后端

在一个终端窗口中：

```bash
cd knowledge-retrieval-service
chmod +x start-backend.sh
./start-backend.sh
```

首次运行会：
- 创建 Python 虚拟环境
- 安装所有依赖包（可能需要 5-10 分钟）
- 下载 AI 模型（首次启动时自动下载）
- 启动 FastAPI 服务

**后端服务地址**：
- API: http://localhost:8000
- 文档: http://localhost:8000/docs

#### 2. 启动前端

在**另一个新终端窗口**中：

```bash
cd knowledge-retrieval-service
chmod +x start-frontend.sh
./start-frontend.sh
```

首次运行会：
- 安装 Node.js 依赖（可能需要 2-3 分钟）
- 启动 Vite 开发服务器

**前端服务地址**：
- UI: http://localhost:3000

### 方式二：手动启动

#### 后端手动启动

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 创建目录
mkdir -p ../data/uploads ../data/chroma ../logs

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端手动启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 📝 使用服务

### 1. 访问前端界面

打开浏览器访问：http://localhost:3000

您会看到 4 个标签页：
- **上传文件** - 上传图片、PDF、Word 等文件
- **检索** - 搜索相似内容
- **统计** - 查看系统统计信息
- **配置** - 调整系统参数

### 2. 测试 API

访问 API 文档：http://localhost:8000/docs

可以直接在文档中测试所有 API 端点。

### 3. 上传测试文件

```bash
# 使用 curl 上传文件
curl -X POST http://localhost:8000/api/v1/files/upload \
  -F "file=@/path/to/your/file.pdf"
```

### 4. 执行搜索

```bash
# 搜索相似内容
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "机器学习",
    "top_k": 5
  }'
```

## 🛠️ 常见问题

### Q: 后端启动失败，提示模块找不到

**A**: 确保虚拟环境已激活：
```bash
source backend/venv/bin/activate
pip list  # 查看已安装的包
```

### Q: 前端启动失败，提示端口被占用

**A**: 修改端口或关闭占用进程：
```bash
# 查找占用 3000 端口的进程
lsof -i :3000

# 或使用其他端口
npm run dev -- --port 3001
```

### Q: 首次启动很慢

**A**: 这是正常的，因为需要：
- 下载 Python 依赖包
- 下载 Node.js 依赖包
- 下载 AI 模型文件（约 100-500MB）

建议在网络良好的环境下进行首次启动。

### Q: 模型下载失败

**A**: 如果在国内，可能需要配置代理或使用镜像：

```bash
# 使用 HuggingFace 镜像（仅后端需要）
export HF_ENDPOINT=https://hf-mirror.com

# 然后重新启动后端
./start-backend.sh
```

### Q: 内存不足

**A**: 如果您的机器内存较小（< 8GB），可以：
1. 关闭其他应用程序
2. 使用更小的模型（修改 config.yaml）
3. 限制上传文件大小

## 🔧 开发调试

### 后端调试

```bash
# 激活虚拟环境
source backend/venv/bin/activate

# 查看日志
tail -f logs/app.log

# 运行测试（如果有）
pytest backend/tests/
```

### 前端调试

```bash
cd frontend

# 查看构建输出
npm run build

# 检查类型
npx tsc --noEmit
```

## 📊 性能优化

### 使用 GPU 加速（可选）

如果有 NVIDIA GPU：

1. 安装 PyTorch GPU 版本：
```bash
source backend/venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

2. 修改 `config.yaml`：
```yaml
embedding:
  device: "cuda"  # 从 "cpu" 改为 "cuda"
```

3. 重启后端服务

## 🧹 清理与重置

### 清理依赖

```bash
# 清理 Python 虚拟环境
rm -rf backend/venv

# 清理 Node 模块
rm -rf frontend/node_modules
```

### 清理数据

```bash
# 删除上传的文件和向量数据
rm -rf data/
rm -rf logs/
```

### 完全重置

```bash
# 停止所有服务（Ctrl+C）

# 清理所有依赖和数据
rm -rf backend/venv
rm -rf frontend/node_modules
rm -rf data/
rm -rf logs/

# 重新开始
./start-backend.sh  # 新终端
./start-frontend.sh # 新终端
```

## 🎯 下一步

1. **熟悉功能** - 上传几个文件，尝试搜索
2. **调整配置** - 在 `config.yaml` 中修改参数
3. **查看代码** - 理解项目结构和实现
4. **扩展功能** - 添加新的文件处理器或模型

## 💡 提示

- 后端和前端必须**同时运行**
- 首次启动需要下载模型，请耐心等待
- 建议使用两个终端窗口分别运行前后端
- 开发时代码修改会自动重载（热更新）

祝您使用愉快！🎉
