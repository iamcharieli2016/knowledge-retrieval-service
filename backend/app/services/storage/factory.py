"""
向量数据库工厂
"""
from typing import Dict, Any

from .base import BaseVectorDB
from .chroma_db import ChromaVectorDB


class VectorDBFactory:
    """向量数据库工厂类"""
    
    _databases: Dict[str, type] = {
        "chroma": ChromaVectorDB,
    }
    
    @classmethod
    def register_database(cls, name: str, db_class: type) -> None:
        """
        注册新的向量数据库
        
        Args:
            name: 数据库名称
            db_class: 数据库类
        """
        cls._databases[name] = db_class
    
    @classmethod
    def create_database(cls, provider: str, **config) -> BaseVectorDB:
        """
        创建向量数据库实例
        
        Args:
            provider: 提供商名称
            **config: 配置参数
            
        Returns:
            向量数据库实例
        """
        provider = provider.lower()
        
        if provider not in cls._databases:
            raise ValueError(f"Unsupported vector database provider: {provider}")
        
        db_class = cls._databases[provider]
        return db_class(**config)
    
    @classmethod
    def get_available_databases(cls) -> Dict[str, str]:
        """获取可用的向量数据库列表"""
        return {
            name: db_class.__doc__ or "No description"
            for name, db_class in cls._databases.items()
        }
