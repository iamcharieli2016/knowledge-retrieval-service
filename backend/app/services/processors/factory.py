"""
文件处理器工厂
"""
from typing import Dict
from pathlib import Path

from .base import BaseProcessor
from .image_processor import ImageProcessor
from .document_processor import DocumentProcessor
from .audio_processor import AudioProcessor


class ProcessorFactory:
    """文件处理器工厂类"""
    
    # 文件扩展名到处理器类型的映射
    _extension_to_type = {
        ".jpg": "image",
        ".jpeg": "image",
        ".png": "image",
        ".gif": "image",
        ".bmp": "image",
        ".webp": "image",
        ".pdf": "document",
        ".docx": "document",
        ".doc": "document",
        ".txt": "document",
        ".md": "document",
        ".mp3": "audio",
        ".wav": "audio",
        ".m4a": "audio",
        ".flac": "audio",
        ".ogg": "audio",
        ".aac": "audio",
    }
    
    # 处理器类型到处理器类的映射
    _processors: Dict[str, type] = {
        "image": ImageProcessor,
        "document": DocumentProcessor,
        "audio": AudioProcessor,
    }
    
    @classmethod
    def register_processor(cls, file_type: str, processor_class: type) -> None:
        """
        注册新的处理器
        
        Args:
            file_type: 文件类型
            processor_class: 处理器类
        """
        cls._processors[file_type] = processor_class
    
    @classmethod
    def create_processor(cls, file_path: str, **config) -> BaseProcessor:
        """
        根据文件路径创建处理器
        
        Args:
            file_path: 文件路径
            **config: 配置参数
            
        Returns:
            处理器实例
        """
        extension = Path(file_path).suffix.lower()
        
        if extension not in cls._extension_to_type:
            raise ValueError(f"Unsupported file extension: {extension}")
        
        file_type = cls._extension_to_type[extension]
        
        if file_type not in cls._processors:
            raise ValueError(f"No processor found for file type: {file_type}")
        
        processor_class = cls._processors[file_type]
        return processor_class(**config)
    
    @classmethod
    def get_file_type(cls, file_path: str) -> str:
        """
        获取文件类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件类型
        """
        extension = Path(file_path).suffix.lower()
        return cls._extension_to_type.get(extension, "unknown")
    
    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """
        检查文件是否支持
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否支持
        """
        extension = Path(file_path).suffix.lower()
        return extension in cls._extension_to_type
