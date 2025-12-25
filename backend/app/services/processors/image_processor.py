"""
图片处理器
"""
from pathlib import Path
from typing import Any, Dict, Union
from PIL import Image
import numpy as np

from .base import BaseProcessor

try:
    import easyocr
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("Warning: easyocr not installed. OCR functionality will be disabled.")


class ImageProcessor(BaseProcessor):
    """图片处理器"""
    
    def __init__(self, **config):
        super().__init__(**config)
        self.max_dimension = config.get("max_dimension", 1024)
        self.thumbnail_size = config.get("thumbnail_size", 256)
        self.enable_ocr = config.get("enable_ocr", True)
        self.ocr_reader = None
        
        # 初始化 OCR
        if self.enable_ocr and HAS_OCR:
            try:
                # 支持中英文
                self.ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
                print("OCR initialized: Chinese + English support")
            except Exception as e:
                print(f"OCR initialization failed: {e}")
                self.ocr_reader = None
    
    def process(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """处理图片文件"""
        if not self.validate_file(file_path):
            raise ValueError(f"Invalid file: {file_path}")
        
        # 获取文件信息
        file_info = self.get_file_info(file_path)
        
        # 加载图片
        image = self.extract_content(file_path)
        
        # 获取图片元数据
        metadata = {
            **file_info,
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "format": image.format
        }
        
        # 调整图片大小（如果需要）
        if max(image.width, image.height) > self.max_dimension:
            image = self._resize_image(image, self.max_dimension)
            metadata["resized"] = True
        
        # OCR 提取文字
        extracted_text = ""
        if self.ocr_reader is not None:
            try:
                # 转换为 numpy array 供 OCR 使用
                image_array = np.array(image)
                results = self.ocr_reader.readtext(image_array)
                
                # 提取所有文字
                texts = [result[1] for result in results]
                extracted_text = " ".join(texts)
                
                metadata["ocr_text"] = extracted_text
                metadata["ocr_detected"] = len(texts) > 0
                
                if extracted_text:
                    print(f"OCR extracted text: {extracted_text[:100]}...")
            except Exception as e:
                print(f"OCR failed: {e}")
                metadata["ocr_error"] = str(e)
        
        return {
            "content": image,
            "text_content": extracted_text,  # 新增：提取的文字
            "metadata": metadata,
            "file_path": str(file_path)
        }
    
    def extract_content(self, file_path: Union[str, Path]) -> Image.Image:
        """提取图片内容"""
        try:
            image = Image.open(file_path)
            # 转换为 RGB 模式
            if image.mode != "RGB":
                image = image.convert("RGB")
            return image
        except Exception as e:
            raise ValueError(f"Error loading image {file_path}: {e}")
    
    def _resize_image(self, image: Image.Image, max_dimension: int) -> Image.Image:
        """调整图片大小"""
        width, height = image.size
        
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def create_thumbnail(self, image: Image.Image, size: int = None) -> Image.Image:
        """创建缩略图"""
        if size is None:
            size = self.thumbnail_size
        
        thumbnail = image.copy()
        thumbnail.thumbnail((size, size), Image.Resampling.LANCZOS)
        return thumbnail
    
    def to_array(self, image: Image.Image) -> np.ndarray:
        """转换图片为数组"""
        return np.array(image)
