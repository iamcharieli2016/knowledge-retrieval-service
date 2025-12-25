"""
嵌入服务工厂
"""
from typing import Dict, Any

from .base import BaseEmbedder
from .huggingface_embedder import HuggingFaceEmbedder


class EmbedderFactory:
    """嵌入器工厂类"""
    
    _embedders: Dict[str, type] = {
        "huggingface": HuggingFaceEmbedder,
    }
    
    @classmethod
    def register_embedder(cls, name: str, embedder_class: type) -> None:
        """
        注册新的嵌入器
        
        Args:
            name: 嵌入器名称
            embedder_class: 嵌入器类
        """
        cls._embedders[name] = embedder_class
    
    @classmethod
    def create_embedder(cls, provider: str, model_name: str, 
                       device: str = "cpu", **kwargs) -> BaseEmbedder:
        """
        创建嵌入器实例
        
        Args:
            provider: 提供商名称
            model_name: 模型名称
            device: 设备
            **kwargs: 其他参数
            
        Returns:
            嵌入器实例
        """
        provider = provider.lower()
        
        if provider not in cls._embedders:
            raise ValueError(f"Unsupported embedder provider: {provider}")
        
        embedder_class = cls._embedders[provider]
        return embedder_class(model_name=model_name, device=device, **kwargs)
    
    @classmethod
    def get_available_embedders(cls) -> Dict[str, str]:
        """获取可用的嵌入器列表"""
        return {
            name: embedder_class.__doc__ or "No description"
            for name, embedder_class in cls._embedders.items()
        }
