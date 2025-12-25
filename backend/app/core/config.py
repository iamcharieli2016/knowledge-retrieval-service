"""
配置管理模块
"""
import os
from typing import Any, Dict, List, Optional
from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class ServiceConfig(BaseModel):
    """服务配置"""
    name: str = "knowledge-retrieval-service"
    version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000


class EmbeddingConfig(BaseModel):
    """嵌入模型配置"""
    provider: str = "huggingface"
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    dimension: int = 384
    batch_size: int = 32
    device: str = "cpu"
    models: Optional[Dict[str, Any]] = None


class VectorDBConfig(BaseModel):
    """向量数据库配置"""
    provider: str = "chroma"
    chroma: Optional[Dict[str, Any]] = None
    milvus: Optional[Dict[str, Any]] = None
    qdrant: Optional[Dict[str, Any]] = None
    faiss: Optional[Dict[str, Any]] = None


class RetrievalConfig(BaseModel):
    """检索配置"""
    default_top_k: int = 10
    max_top_k: int = 100
    min_top_k: int = 1
    similarity_threshold: float = 0.7
    enable_reranking: bool = False
    enable_hybrid: bool = False  # 启用混合检索
    hybrid_alpha: float = 0.5  # 向量检索权重
    enable_multi_path: bool = False  # 启用多路召回


class FileProcessingConfig(BaseModel):
    """文件处理配置"""
    upload_dir: str = "./data/uploads"
    max_file_size: int = 104857600  # 100MB
    allowed_extensions: Dict[str, List[str]] = {
        "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
        "document": [".pdf", ".docx", ".doc", ".txt", ".md"],
        "video": [".mp4", ".avi", ".mov", ".mkv", ".flv"],
        "audio": [".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"]
    }
    image: Optional[Dict[str, Any]] = None
    document: Optional[Dict[str, Any]] = None
    video: Optional[Dict[str, Any]] = None
    audio: Optional[Dict[str, Any]] = None


class DatabaseConfig(BaseModel):
    """数据库配置"""
    type: str = "sqlite"
    sqlite: Optional[Dict[str, str]] = {"path": "./data/metadata.db"}
    postgresql: Optional[Dict[str, Any]] = None
    mysql: Optional[Dict[str, Any]] = None


class CacheConfig(BaseModel):
    """缓存配置"""
    enabled: bool = True
    backend: str = "memory"
    redis: Optional[Dict[str, Any]] = None
    memory: Optional[Dict[str, Any]] = {"max_size": 1000, "ttl": 1800}


class SecurityConfig(BaseModel):
    """安全配置"""
    enable_auth: bool = False
    api_key: Optional[str] = None
    cors: Dict[str, Any] = {
        "enabled": True,
        "origins": ["http://localhost:3000", "http://localhost:8000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "headers": ["*"]
    }


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "./logs/app.log"
    max_size: int = 10485760
    backup_count: int = 5


class PerformanceConfig(BaseModel):
    """性能配置"""
    workers: int = 4
    max_connections: int = 100
    timeout: int = 30
    keepalive: int = 5


class MonitoringConfig(BaseModel):
    """监控配置"""
    enabled: bool = True
    prometheus: Optional[Dict[str, Any]] = None
    health_check: Optional[Dict[str, Any]] = {"enabled": True, "interval": 60}


class Settings(BaseSettings):
    """主配置类"""
    service: ServiceConfig = ServiceConfig()
    embedding: EmbeddingConfig = EmbeddingConfig()
    vector_db: VectorDBConfig = VectorDBConfig()
    retrieval: RetrievalConfig = RetrievalConfig()
    file_processing: FileProcessingConfig = FileProcessingConfig()
    database: DatabaseConfig = DatabaseConfig()
    cache: CacheConfig = CacheConfig()
    security: SecurityConfig = SecurityConfig()
    logging: LoggingConfig = LoggingConfig()
    performance: PerformanceConfig = PerformanceConfig()
    monitoring: MonitoringConfig = MonitoringConfig()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def from_yaml(cls, config_path: str = "config.yaml") -> "Settings":
        """从 YAML 文件加载配置"""
        # 尝试多个可能的配置文件路径
        possible_paths = [
            config_path,
            Path(__file__).parent.parent.parent.parent / config_path,
            Path(config_path).absolute()
        ]
        
        config_file = None
        for path in possible_paths:
            if Path(path).exists():
                config_file = path
                break
        
        if config_file is None:
            print(f"Warning: Config file not found, using default settings")
            return cls()
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)

    def update_config(self, updates: Dict[str, Any]) -> None:
        """动态更新配置"""
        for key, value in updates.items():
            if hasattr(self, key):
                if isinstance(getattr(self, key), BaseModel):
                    # 更新嵌套配置
                    current = getattr(self, key)
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if hasattr(current, sub_key):
                                setattr(current, sub_key, sub_value)
                else:
                    setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "service": self.service.model_dump(),
            "embedding": self.embedding.model_dump(),
            "vector_db": self.vector_db.model_dump(),
            "retrieval": self.retrieval.model_dump(),
            "file_processing": self.file_processing.model_dump(),
            "database": self.database.model_dump(),
            "cache": self.cache.model_dump(),
            "security": self.security.model_dump(),
            "logging": self.logging.model_dump(),
            "performance": self.performance.model_dump(),
            "monitoring": self.monitoring.model_dump()
        }


# 全局配置实例
settings = Settings.from_yaml()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings


def reload_settings(config_path: str = "config.yaml") -> Settings:
    """重新加载配置"""
    global settings
    settings = Settings.from_yaml(config_path)
    return settings
