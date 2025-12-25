"""
文件处理器基类
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np


class BaseProcessor(ABC):
    """文件处理器基类"""
    
    def __init__(self, **config):
        """
        初始化处理器
        
        Args:
            **config: 配置参数
        """
        self.config = config
    
    @abstractmethod
    def process(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        处理文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            处理结果字典，包含提取的内容和元数据
        """
        pass
    
    @abstractmethod
    def extract_content(self, file_path: Union[str, Path]) -> Any:
        """
        提取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取的内容
        """
        pass
    
    def validate_file(self, file_path: Union[str, Path]) -> bool:
        """
        验证文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否有效
        """
        path = Path(file_path)
        return path.exists() and path.is_file()
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return {
            "filename": path.name,
            "extension": path.suffix,
            "size": path.stat().st_size,
            "modified_time": path.stat().st_mtime
        }
