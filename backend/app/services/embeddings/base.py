"""
嵌入服务基类
"""
from abc import ABC, abstractmethod
from typing import Any, List, Union
import numpy as np


class BaseEmbedder(ABC):
    """嵌入服务基类"""
    
    def __init__(self, model_name: str, device: str = "cpu", **kwargs):
        """
        初始化嵌入器
        
        Args:
            model_name: 模型名称
            device: 设备 (cpu/cuda)
            **kwargs: 其他参数
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self.dimension = 0
        
    @abstractmethod
    def load_model(self) -> None:
        """加载模型"""
        pass
    
    @abstractmethod
    def embed_text(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        文本嵌入
        
        Args:
            texts: 单个文本或文本列表
            
        Returns:
            嵌入向量数组
        """
        pass
    
    @abstractmethod
    def embed_image(self, images: Union[str, List[str]]) -> np.ndarray:
        """
        图片嵌入
        
        Args:
            images: 图片路径或图片路径列表
            
        Returns:
            嵌入向量数组
        """
        pass
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        return self.dimension
    
    def normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """归一化向量"""
        norm = np.linalg.norm(vector, axis=-1, keepdims=True)
        return vector / (norm + 1e-9)
