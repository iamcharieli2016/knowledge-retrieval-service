"""
音频处理器 - 使用Whisper进行语音转文字
"""
import os
from typing import Dict, Any, Union
from pathlib import Path

from .base import BaseProcessor

# Whisper支持检测
try:
    import whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False
    print("Warning: whisper not installed. Audio processing will be disabled.")
    print("Install with: pip install openai-whisper")


class AudioProcessor(BaseProcessor):
    """音频处理器"""
    
    def __init__(self, model_size: str = "base", language: str = "zh"):
        """
        初始化音频处理器
        
        Args:
            model_size: Whisper模型大小 (tiny, base, small, medium, large)
                - tiny: 最快，精度低 (~1GB内存)
                - base: 平衡，推荐 (~1GB内存)
                - small: 较好精度 (~2GB内存)
                - medium/large: 最高精度，慢 (>5GB内存)
            language: 语言代码 (zh=中文, en=英文)
        """
        if not HAS_WHISPER:
            raise RuntimeError(
                "Whisper not installed. Please install: pip install openai-whisper"
            )
        
        self.model_size = model_size
        self.language = language
        self.model = None
        
        print(f"Audio processor initialized with model: {model_size}, language: {language}")
    
    def _load_model(self):
        """延迟加载模型（首次使用时）"""
        if self.model is None:
            print(f"Loading Whisper model '{self.model_size}'... (first time may download ~150MB)")
            self.model = whisper.load_model(self.model_size)
            print(f"Whisper model '{self.model_size}' loaded successfully")
    
    def extract_content(self, file_path: Union[str, Path]) -> str:
        """
        提取音频内容（转写为文本）
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            转写的文本内容
        """
        self._load_model()
        
        file_path = str(file_path)
        
        try:
            result = self.model.transcribe(
                file_path,
                language=self.language,
                fp16=False,
                verbose=False
            )
            
            return result["text"].strip()
            
        except Exception as e:
            print(f"Error extracting audio content: {e}")
            return ""
    
    def process(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        处理音频文件
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            处理结果字典，包含：
            - content: None (音频本身不需要返回)
            - text_content: 转写的文本
            - language: 检测到的语言
            - duration: 音频时长（秒）
            - metadata: 其他元数据
        """
        self._load_model()
        
        file_path = str(file_path)
        
        try:
            # 使用Whisper转写音频
            print(f"Transcribing audio: {Path(file_path).name}...")
            
            result = self.model.transcribe(
                file_path,
                language=self.language,  # 指定语言可以提高速度和准确度
                fp16=False,  # CPU模式使用FP32
                verbose=False  # 不打印进度
            )
            
            # 提取转写文本
            text_content = result["text"].strip()
            detected_language = result.get("language", self.language)
            
            # 计算时长
            segments = result.get("segments", [])
            duration = segments[-1]["end"] if segments else 0
            
            print(f"Audio transcribed successfully: {len(text_content)} characters, {duration:.1f}s")
            
            return {
                "content": None,  # 音频不需要返回原始内容
                "text_content": text_content,
                "language": detected_language,
                "duration": duration,
                "metadata": {
                    "file_name": Path(file_path).name,
                    "file_size": os.path.getsize(file_path),
                    "segments_count": len(segments),
                    "model_size": self.model_size
                }
            }
            
        except Exception as e:
            print(f"Error processing audio: {e}")
            raise RuntimeError(f"Failed to process audio file: {e}")
    
    def validate(self, file_path: Union[str, Path]) -> bool:
        """
        验证音频文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为有效音频文件
        """
        extension = Path(file_path).suffix.lower()
        
        # 支持的音频格式
        supported_formats = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"]
        
        if extension not in supported_formats:
            return False
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False
        
        # 检查文件大小（限制100MB）
        file_size = os.path.getsize(file_path)
        max_size = 100 * 1024 * 1024  # 100MB
        
        if file_size > max_size:
            print(f"Warning: Audio file too large: {file_size / 1024 / 1024:.1f}MB (max: 100MB)")
            return False
        
        return True


# 简化版：只转写不做额外处理
class SimpleAudioProcessor(AudioProcessor):
    """简化的音频处理器 - 使用tiny模型"""
    
    def __init__(self):
        super().__init__(model_size="base", language="zh")
