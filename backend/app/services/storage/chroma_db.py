"""
ChromaDB 实现
"""
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import chromadb
from chromadb.config import Settings

from .base import BaseVectorDB


class ChromaVectorDB(BaseVectorDB):
    """ChromaDB 向量数据库实现"""
    
    def __init__(self, **config):
        super().__init__(**config)
        self.persist_directory = config.get("persist_directory", "./data/chroma")
        self.connect()
    
    def connect(self) -> None:
        """连接到 ChromaDB"""
        try:
            self.client = chromadb.Client(Settings(
                persist_directory=self.persist_directory,
                anonymized_telemetry=False
            ))
            # 尝试获取或创建集合
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
            except:
                # 如果集合不存在，会在第一次插入时创建
                self.collection = None
        except Exception as e:
            print(f"Error connecting to ChromaDB: {e}")
            raise
    
    def create_collection(self, dimension: int, **kwargs) -> None:
        """创建集合"""
        try:
            # ChromaDB 会自动处理维度，不需要预先指定
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"dimension": dimension}
            )
        except Exception as e:
            print(f"Error creating collection: {e}")
            raise
    
    def insert(self, vectors: np.ndarray, metadatas: List[Dict[str, Any]], 
              ids: Optional[List[str]] = None) -> List[str]:
        """插入向量"""
        if self.collection is None:
            self.create_collection(dimension=vectors.shape[1])
        
        # 生成 ID（如果未提供）
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        
        # 转换向量为列表
        embeddings = vectors.tolist()
        
        # 清理 metadata - ChromaDB 不接受 None 值
        cleaned_metadatas = []
        for metadata in metadatas:
            cleaned = {k: v for k, v in metadata.items() if v is not None}
            # 确保所有值都是 ChromaDB 支持的类型
            for key, value in list(cleaned.items()):
                if not isinstance(value, (str, int, float, bool)):
                    cleaned[key] = str(value)
            cleaned_metadatas.append(cleaned)
        
        # 插入数据
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=cleaned_metadatas
            )
            return ids
        except Exception as e:
            print(f"Error inserting vectors: {e}")
            raise
    
    def search(self, query_vector: np.ndarray, top_k: int = 10,
              filter: Optional[Dict[str, Any]] = None) -> List[Tuple[str, float, Dict[str, Any]]]:
        """搜索相似向量"""
        if self.collection is None:
            return []
        
        # 确保查询向量是一维的
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)
        
        try:
            results = self.collection.query(
                query_embeddings=query_vector.tolist(),
                n_results=top_k,
                where=filter
            )
            
            # 格式化结果
            formatted_results = []
            if results['ids'] and len(results['ids']) > 0:
                for i, id in enumerate(results['ids'][0]):
                    score = 1.0 - results['distances'][0][i]  # ChromaDB 返回距离，转换为相似度
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    formatted_results.append((id, score, metadata))
            
            return formatted_results
        except Exception as e:
            print(f"Error searching vectors: {e}")
            return []
    
    def delete(self, ids: List[str]) -> bool:
        """删除向量"""
        if self.collection is None:
            return False
        
        try:
            self.collection.delete(ids=ids)
            return True
        except Exception as e:
            print(f"Error deleting vectors: {e}")
            return False
    
    def get_by_id(self, id: str) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]:
        """根据ID获取向量"""
        if self.collection is None:
            return None
        
        try:
            results = self.collection.get(
                ids=[id],
                include=["embeddings", "metadatas"]
            )
            
            if results['ids']:
                vector = np.array(results['embeddings'][0])
                metadata = results['metadatas'][0] if results['metadatas'] else {}
                return (vector, metadata)
            
            return None
        except Exception as e:
            print(f"Error getting vector by id: {e}")
            return None
    
    def count(self) -> int:
        """获取向量总数"""
        if self.collection is None:
            return 0
        
        try:
            return self.collection.count()
        except Exception as e:
            print(f"Error counting vectors: {e}")
            return 0
    
    def clear(self) -> None:
        """清空集合"""
        if self.collection is None:
            return
        
        try:
            # ChromaDB 不支持直接清空，需要删除并重新创建
            self.client.delete_collection(name=self.collection_name)
            self.collection = None
        except Exception as e:
            print(f"Error clearing collection: {e}")
    
    def close(self) -> None:
        """关闭连接"""
        # ChromaDB 不需要显式关闭
        pass
