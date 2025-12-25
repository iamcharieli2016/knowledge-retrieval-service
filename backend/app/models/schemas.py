"""
数据模型定义
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class FileType(str, Enum):
    """文件类型枚举"""
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"


class ProcessingStatus(str, Enum):
    """处理状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    file_id: str = Field(..., description="文件唯一标识")
    filename: str = Field(..., description="文件名")
    file_type: FileType = Field(..., description="文件类型")
    size: int = Field(..., description="文件大小（字节）")
    status: ProcessingStatus = Field(..., description="处理状态")
    upload_time: datetime = Field(default_factory=datetime.now, description="上传时间")
    message: str = Field(default="File uploaded successfully", description="消息")


class FileMetadata(BaseModel):
    """文件元数据"""
    file_id: str
    filename: str
    file_type: FileType
    file_path: str
    size: int
    mime_type: str
    upload_time: datetime
    processing_time: Optional[float] = None
    vector_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    status: ProcessingStatus = ProcessingStatus.PENDING


class SearchRequest(BaseModel):
    """搜索请求"""
    query: Optional[str] = Field(None, description="文本查询")
    file_id: Optional[str] = Field(None, description="文件ID作为查询")
    query_vector: Optional[List[float]] = Field(None, description="直接提供查询向量")
    top_k: int = Field(10, ge=1, le=100, description="返回结果数量")
    threshold: float = Field(0.0, ge=0.0, le=1.0, description="相似度阈值")
    filter: Optional[Dict[str, Any]] = Field(None, description="过滤条件")
    
    # Pydantic V2: 验证器已通过 Field 的 ge/le 参数实现，无需额外验证
    
    @model_validator(mode='after')
    def validate_query_input(self):
        """验证查询输入 - 至少需要一个"""
        if not any([self.query, self.file_id, self.query_vector]):
            raise ValueError("At least one of query, file_id, or query_vector must be provided")
        return self


class SearchResult(BaseModel):
    """搜索结果"""
    file_id: str = Field(..., description="文件ID")
    filename: str = Field(..., description="文件名")
    file_type: FileType = Field(..., description="文件类型")
    similarity: float = Field(..., description="相似度分数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    thumbnail_url: Optional[str] = Field(None, description="缩略图URL")


class SearchResponse(BaseModel):
    """搜索响应"""
    results: List[SearchResult] = Field(..., description="搜索结果列表")
    total: int = Field(..., description="总结果数")
    query_time: float = Field(..., description="查询时间（秒）")


class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    embedding_model: Optional[str] = Field(None, description="嵌入模型名称")
    embedding_provider: Optional[str] = Field(None, description="嵌入提供商")
    vector_db_provider: Optional[str] = Field(None, description="向量数据库提供商")
    default_top_k: Optional[int] = Field(None, ge=1, le=100, description="默认返回结果数")
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="相似度阈值")


class ConfigResponse(BaseModel):
    """配置响应"""
    service: Dict[str, Any]
    embedding: Dict[str, Any]
    vector_db: Dict[str, Any]
    retrieval: Dict[str, Any]
    file_processing: Dict[str, Any]


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="版本号")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    components: Dict[str, str] = Field(default_factory=dict, description="组件状态")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    detail: Optional[Any] = Field(None, description="详细信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class StatisticsResponse(BaseModel):
    """统计信息响应"""
    total_files: int = Field(..., description="总文件数")
    files_by_type: Dict[str, int] = Field(..., description="按类型分组的文件数")
    total_vectors: int = Field(..., description="总向量数")
    storage_used: int = Field(..., description="存储使用量（字节）")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")


class BatchUploadRequest(BaseModel):
    """批量上传请求"""
    file_ids: List[str] = Field(..., description="文件ID列表")


class BatchSearchRequest(BaseModel):
    """批量搜索请求"""
    queries: List[SearchRequest] = Field(..., description="搜索请求列表")


class BatchSearchResponse(BaseModel):
    """批量搜索响应"""
    results: List[SearchResponse] = Field(..., description="搜索结果列表")
    total_time: float = Field(..., description="总查询时间（秒）")


class ModelInfo(BaseModel):
    """模型信息"""
    name: str = Field(..., description="模型名称")
    provider: str = Field(..., description="提供商")
    dimension: int = Field(..., description="向量维度")
    description: Optional[str] = Field(None, description="描述")
    supported_types: List[FileType] = Field(..., description="支持的文件类型")


class AvailableModelsResponse(BaseModel):
    """可用模型响应"""
    models: List[ModelInfo] = Field(..., description="可用模型列表")


class VectorDBInfo(BaseModel):
    """向量数据库信息"""
    name: str = Field(..., description="数据库名称")
    description: Optional[str] = Field(None, description="描述")
    features: List[str] = Field(..., description="特性列表")


class AvailableVectorDBsResponse(BaseModel):
    """可用向量数据库响应"""
    databases: List[VectorDBInfo] = Field(..., description="可用数据库列表")
