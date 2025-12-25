"""
文档处理器
"""
from pathlib import Path
from typing import Any, Dict, List, Union
import PyPDF2
import docx

from .base import BaseProcessor


class DocumentProcessor(BaseProcessor):
    """文档处理器"""
    
    def __init__(self, **config):
        super().__init__(**config)
        self.chunk_size = config.get("chunk_size", 512)
        self.chunk_overlap = config.get("chunk_overlap", 50)
    
    def process(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """处理文档文件"""
        if not self.validate_file(file_path):
            raise ValueError(f"Invalid file: {file_path}")
        
        # 获取文件信息
        file_info = self.get_file_info(file_path)
        
        # 提取文本内容
        text = self.extract_content(file_path)
        
        # 分块
        chunks = self._chunk_text(text)
        
        metadata = {
            **file_info,
            "total_chunks": len(chunks),
            "total_length": len(text)
        }
        
        return {
            "content": text,
            "chunks": chunks,
            "metadata": metadata,
            "file_path": str(file_path)
        }
    
    def extract_content(self, file_path: Union[str, Path]) -> str:
        """提取文档内容"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == ".pdf":
            return self._extract_pdf(path)
        elif extension in [".docx", ".doc"]:
            return self._extract_docx(path)
        elif extension in [".txt", ".md"]:
            return self._extract_text(path)
        else:
            raise ValueError(f"Unsupported document type: {extension}")
    
    def _extract_pdf(self, file_path: Path) -> str:
        """提取 PDF 文本"""
        try:
            text = ""
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error extracting PDF {file_path}: {e}")
    
    def _extract_docx(self, file_path: Path) -> str:
        """提取 Word 文档文本"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error extracting DOCX {file_path}: {e}")
    
    def _extract_text(self, file_path: Path) -> str:
        """提取纯文本文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except Exception as e:
            raise ValueError(f"Error extracting text {file_path}: {e}")
    
    def _chunk_text(self, text: str) -> List[str]:
        """将文本分块"""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # 如果不是最后一块，尝试在句子边界处分割
            if end < text_length:
                # 寻找最近的句子结束符
                for delimiter in [". ", "。", "! ", "！", "? ", "？", "\n"]:
                    last_delimiter = text.rfind(delimiter, start, end)
                    if last_delimiter != -1:
                        end = last_delimiter + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # 移动到下一块，考虑重叠
            start = end - self.chunk_overlap if end < text_length else text_length
        
        return chunks
