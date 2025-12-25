# 模型选择指南

## 📊 可用模型对比

### 1. CLIP 模型（推荐 - 多模态）

**模型名称**: `openai/clip-vit-base-patch32`

**支持功能**:
- ✅ **文本嵌入** - 支持文本检索
- ✅ **图片嵌入** - 支持以图搜图
- ✅ **跨模态检索** - 文本搜图片，图片搜文本

**优点**:
- 同时支持文本和图片
- 可以进行跨模态检索
- 适合多媒体内容检索

**缺点**:
- 模型较大（约 600MB）
- 文本检索精度略低于专用文本模型
- 需要更多计算资源

**最佳使用场景**:
- 需要处理图片和文档的混合场景
- 需要以图搜图功能
- 需要用文字描述搜索图片

**配置**:
```yaml
embedding:
  model_name: "openai/clip-vit-base-patch32"
  dimension: 512
  device: "cpu"  # 或 "mps" (Apple Silicon) / "cuda" (NVIDIA GPU)
```

---

### 2. Sentence Transformers（纯文本）

**模型名称**: `sentence-transformers/all-MiniLM-L6-v2`

**支持功能**:
- ✅ **文本嵌入** - 专注文本检索
- ❌ 不支持图片

**优点**:
- 模型小（约 90MB）
- 下载快速
- 文本检索精度高
- 资源占用少

**缺点**:
- 只能处理文本
- 不能处理图片文件

**最佳使用场景**:
- 只需要文档检索（PDF、Word、TXT）
- 资源受限的环境
- 快速原型开发

**配置**:
```yaml
embedding:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  dimension: 384
  device: "cpu"
```

---

### 3. 其他可选模型

#### 中文优化模型
```yaml
# 适合中文文本
embedding:
  model_name: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  dimension: 384
```

#### 更大的 CLIP 模型
```yaml
# 更高精度，但更慢
embedding:
  model_name: "openai/clip-vit-large-patch14"
  dimension: 768
```

#### 小型 CLIP 模型
```yaml
# 更快速，但精度略低
embedding:
  model_name: "openai/clip-vit-base-patch16"
  dimension: 512
```

---

## 🚀 当前配置

### 已设置为：CLIP 模型

当前系统配置使用 **`openai/clip-vit-base-patch32`**，可以：

✅ 上传并检索 PDF、Word、TXT 文档
✅ 上传并检索 JPG、PNG、GIF 等图片
✅ 用文本搜索图片
✅ 用图片搜索文档
✅ 以图搜图

---

## 🔧 如何切换模型

### 方法一：修改配置文件

编辑 `config.yaml`：

```yaml
embedding:
  model_name: "你想用的模型名称"
  dimension: 对应的维度
```

然后重启服务：
```bash
./start-backend.sh
```

### 方法二：通过 API 动态更新

```bash
curl -X POST http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
  }'
```

**注意**: 切换模型后，需要重新上传文件重新生成嵌入向量。

---

## 💾 模型缓存

首次使用模型时会自动下载并缓存到：
```
~/.cache/huggingface/hub/
```

后续启动会直接使用缓存，无需重新下载。

---

## 🌐 下载加速

### 使用国内镜像

启动脚本已自动配置：
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### 手动设置（如果需要）

```bash
# Linux/macOS
export HF_ENDPOINT=https://hf-mirror.com

# Windows (PowerShell)
$env:HF_ENDPOINT="https://hf-mirror.com"
```

---

## ⚡ 性能优化

### 使用 GPU 加速

#### Apple Silicon (M1/M2/M3)
```yaml
embedding:
  device: "mps"  # Metal Performance Shaders
```

#### NVIDIA GPU
```yaml
embedding:
  device: "cuda"
```

需要安装 CUDA 版本的 PyTorch：
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### CPU
```yaml
embedding:
  device: "cpu"  # 默认，兼容性最好
```

---

## 📝 模型下载大小参考

| 模型 | 大小 | 下载时间* |
|------|------|----------|
| all-MiniLM-L6-v2 | ~90MB | 1-2 分钟 |
| clip-vit-base-patch32 | ~600MB | 5-10 分钟 |
| clip-vit-large-patch14 | ~1.7GB | 15-30 分钟 |
| paraphrase-multilingual | ~470MB | 5-10 分钟 |

*使用镜像加速，实际速度取决于网络

---

## 🎯 推荐配置

### 场景一：只处理文档
```yaml
embedding:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  dimension: 384
```

### 场景二：文档 + 图片（推荐）
```yaml
embedding:
  model_name: "openai/clip-vit-base-patch32"
  dimension: 512
```

### 场景三：中文为主
```yaml
embedding:
  model_name: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  dimension: 384
```

---

## ❓ 常见问题

**Q: 切换模型后之前的数据怎么办？**
A: 需要重新上传文件，因为不同模型的向量维度和语义空间不同。

**Q: 可以同时使用多个模型吗？**
A: 可以，在 `config.yaml` 中为不同文件类型配置不同模型：
```yaml
embedding:
  models:
    image:
      model_name: "openai/clip-vit-base-patch32"
    text:
      model_name: "sentence-transformers/all-MiniLM-L6-v2"
```

**Q: 模型下载失败怎么办？**
A: 使用镜像 `export HF_ENDPOINT=https://hf-mirror.com`

**Q: 如何知道模型是否支持图片？**
A: 只有 CLIP 系列模型支持图片，其他都是纯文本模型。

---

## 📚 更多信息

- [HuggingFace Models](https://huggingface.co/models)
- [Sentence Transformers](https://www.sbert.net/)
- [CLIP Paper](https://arxiv.org/abs/2103.00020)
