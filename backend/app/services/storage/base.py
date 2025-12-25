"""
向量数据库基类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


class BaseVectorDB(ABC):
    """向量数据库基类"""
    
    def __init__(self, **config):
        """
        初始化向量数据库
        
        Args:
            **config: 配置参数
        """
        self.config = config
        self.client = None
        self.collection_name = config.get("collection_name", "knowledge_base")
        
    @abstractmethod
    def connect(self) -> None:
        """连接到数据库"""
        pass
    
    @abstractmethod
    def create_collection(self, dimension: int, **kwargs) -> None:
        """
        创建集合
        
        Args:
            dimension: 向量维度
            **kwargs: 其他参数
        """
        pass
    
    @abstractmethod
    def insert(self, vectors: np.ndarray, metadatas: List[Dict[str, Any]], 
              ids: Optional[List[str]] = None) -> List[str]:
        """
        插入向量
        
        Args:
            vectors: 向量数组
            metadatas: 元数据列表
            ids: ID列表（可选）
            
        Returns:
            插入的ID列表
        """
        pass
    
    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int = 10,
              filter: Optional[Dict[str, Any]] = None) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        搜索相似向量
        
        Args:
            query_vector: 查询向量
            top_k: 返回结果数量
            filter: 过滤条件
            
        Returns:
            结果列表 [(id, score, metadata), ...]
        """
        pass
    
    @abstractmethod
    def delete(self, ids: List[str]) -> bool:
        """
        删除向量
        
        Args:
            ids: ID列表
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]:
        """
        根据ID获取向量
        
        Args:
            id: 向量ID
            
        Returns:
            (向量, 元数据) 或 None
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """获取向量总数"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """清空集合"""
        pass
    
    def close(self) -> None:
        """关闭连接"""
        pass
