"""
API 路由
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from ..models.schemas import (
    FileUploadResponse, SearchRequest, SearchResponse,
    ConfigUpdateRequest, ConfigResponse, HealthResponse,
    StatisticsResponse, ErrorResponse, FileType, ProcessingStatus,
    AvailableModelsResponse, ModelInfo, AvailableVectorDBsResponse, VectorDBInfo
)
from ..core.config import Settings, get_settings
from ..services.knowledge_service import KnowledgeRetrievalService
from ..services.embeddings.factory import EmbedderFactory
from ..services.storage.factory import VectorDBFactory

# 创建路由器
router = APIRouter()

# 全局服务实例
_service: Optional[KnowledgeRetrievalService] = None


def get_service(settings: Settings = Depends(get_settings)) -> KnowledgeRetrievalService:
    """获取服务实例"""
    global _service
    if _service is None:
        _service = KnowledgeRetrievalService(settings)
    return _service


@router.post("/files/upload", response_model=FileUploadResponse, tags=["文件管理"])
async def upload_file(
    file: UploadFile = File(...),
    service: KnowledgeRetrievalService = Depends(get_service),
    settings: Settings = Depends(get_settings)
):
    """
    上传文件
    
    支持的文件类型:
    - 图片: JPG, PNG, GIF, BMP, WEBP
    - 文档: PDF, DOCX, TXT, MD
    - 视频: MP4, AVI, MOV, MKV (待实现)
    - 音频: MP3, WAV, AAC (待实现)
    """
    try:
        # 检查文件大小
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.file_processing.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.file_processing.max_file_size} bytes"
            )
        
        # 检查文件类型
        file_extension = Path(file.filename).suffix.lower()
        all_extensions = []
        for exts in settings.file_processing.allowed_extensions.values():
            all_extensions.extend(exts)
        
        if file_extension not in all_extensions:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type: {file_extension}"
            )
        
        # 确保上传目录存在
        upload_dir = Path(settings.file_processing.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 处理文件
        result = await service.upload_file(
            file_path=str(file_path),
            filename=file.filename
        )
        
        return FileUploadResponse(
            file_id=result["file_id"],
            filename=result["filename"],
            file_type=FileType(result["file_type"]),
            size=file_size,
            status=ProcessingStatus(result["status"]),
            upload_time=datetime.now(),
            message=f"File processed successfully in {result['processing_time']:.2f}s"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse, tags=["检索"])
async def search(
    request: SearchRequest,
    service: KnowledgeRetrievalService = Depends(get_service),
    settings: Settings = Depends(get_settings)
):
    """
    搜索相似内容
    
    可以通过以下方式之一进行搜索:
    - query: 文本查询
    - file_id: 使用已上传文件作为查询
    - query_vector: 直接提供查询向量
    """
    try:
        # 验证至少提供一个查询参数
        if not any([request.query, request.file_id, request.query_vector]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one of query, file_id, or query_vector must be provided"
            )
        
        # 执行搜索
        result = await service.search(
            query=request.query,
            file_id=request.file_id,
            query_vector=request.query_vector,
            top_k=request.top_k,
            threshold=request.threshold,
            filter=request.filter
        )
        
        return SearchResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during search: {str(e)}"
        )


@router.get("/config", response_model=ConfigResponse, tags=["配置管理"])
async def get_config(settings: Settings = Depends(get_settings)):
    """获取当前配置"""
    return ConfigResponse(
        service=settings.service.model_dump(),
        embedding=settings.embedding.model_dump(),
        vector_db=settings.vector_db.model_dump(),
        retrieval=settings.retrieval.model_dump(),
        file_processing=settings.file_processing.model_dump()
    )


@router.put("/config", tags=["配置管理"])
async def update_config(
    request: ConfigUpdateRequest,
    service: KnowledgeRetrievalService = Depends(get_service)
):
    """
    更新配置
    
    支持动态更新:
    - embedding_model: 嵌入模型
    - embedding_provider: 嵌入提供商
    - vector_db_provider: 向量数据库提供商
    - default_top_k: 默认返回结果数
    - similarity_threshold: 相似度阈值
    """
    try:
        updates = request.model_dump(exclude_none=True)
        service.update_config(updates)
        
        return {
            "status": "success",
            "message": "Configuration updated successfully",
            "updates": updates
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating configuration: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse, tags=["系统"])
async def health_check(
    service: KnowledgeRetrievalService = Depends(get_service),
    settings: Settings = Depends(get_settings)
):
    """健康检查"""
    components = {
        "embedder": "healthy" if service.embedder else "unavailable",
        "vector_db": "healthy" if service.vector_db else "unavailable",
    }
    
    status = "healthy" if all(v == "healthy" for v in components.values()) else "degraded"
    
    return HealthResponse(
        status=status,
        version=settings.service.version,
        timestamp=datetime.now(),
        components=components
    )


@router.get("/statistics", response_model=StatisticsResponse, tags=["系统"])
async def get_statistics(service: KnowledgeRetrievalService = Depends(get_service)):
    """获取统计信息"""
    stats = service.get_statistics()
    return StatisticsResponse(
        total_files=stats["total_files"],
        files_by_type=stats["files_by_type"],
        total_vectors=stats["total_vectors"],
        storage_used=stats["storage_used"],
        last_updated=datetime.now()
    )


@router.delete("/files/{file_id}", tags=["文件管理"])
async def delete_file(
    file_id: str,
    service: KnowledgeRetrievalService = Depends(get_service)
):
    """删除文件"""
    success = service.delete_file(file_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {file_id}"
        )
    
    return {
        "status": "success",
        "message": f"File {file_id} deleted successfully"
    }


@router.get("/models", response_model=AvailableModelsResponse, tags=["配置管理"])
async def get_available_models():
    """获取可用的嵌入模型列表"""
    models = [
        ModelInfo(
            name="sentence-transformers/all-MiniLM-L6-v2",
            provider="huggingface",
            dimension=384,
            description="Fast and efficient sentence embeddings",
            supported_types=[FileType.DOCUMENT]
        ),
        ModelInfo(
            name="openai/clip-vit-base-patch32",
            provider="huggingface",
            dimension=512,
            description="CLIP model for image and text",
            supported_types=[FileType.IMAGE, FileType.DOCUMENT]
        ),
    ]
    
    return AvailableModelsResponse(models=models)


@router.get("/databases", response_model=AvailableVectorDBsResponse, tags=["配置管理"])
async def get_available_databases():
    """获取可用的向量数据库列表"""
    databases = [
        VectorDBInfo(
            name="chroma",
            description="Lightweight vector database",
            features=["Easy to use", "No setup required", "Persistent storage"]
        ),
        VectorDBInfo(
            name="milvus",
            description="High-performance vector database",
            features=["Scalable", "High performance", "Rich features"]
        ),
        VectorDBInfo(
            name="qdrant",
            description="Modern vector search engine",
            features=["Fast search", "Filtering", "Cloud-native"]
        ),
        VectorDBInfo(
            name="faiss",
            description="Facebook AI Similarity Search",
            features=["Fast", "CPU/GPU support", "Memory efficient"]
        ),
    ]
    
    return AvailableVectorDBsResponse(databases=databases)


@router.get("/debug/retrieval-status", tags=["调试"])
async def get_retrieval_status(service: KnowledgeRetrievalService = Depends(get_service)):
    """获取检索系统状态（调试用）"""
    return {
        "hybrid_retriever_enabled": service.hybrid_retriever is not None,
        "multi_path_retriever_enabled": service.multi_path_retriever is not None,
        "hybrid_indexed": service._hybrid_indexed,
        "total_files": len(service.file_metadata),
        "retrieval_config": {
            "enable_hybrid": getattr(service.settings.retrieval, 'enable_hybrid', False),
            "enable_multi_path": getattr(service.settings.retrieval, 'enable_multi_path', False),
            "hybrid_alpha": getattr(service.settings.retrieval, 'hybrid_alpha', 0.5),
            "default_top_k": service.settings.retrieval.default_top_k,
            "similarity_threshold": service.settings.retrieval.similarity_threshold
        }
    }
