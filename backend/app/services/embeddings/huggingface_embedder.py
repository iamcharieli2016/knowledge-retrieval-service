"""
HuggingFace 嵌入实现
"""
from typing import List, Union
import numpy as np
from PIL import Image

from .base import BaseEmbedder


class HuggingFaceEmbedder(BaseEmbedder):
    """HuggingFace 嵌入器实现"""
    
    def __init__(self, model_name: str, device: str = "cpu", **kwargs):
        super().__init__(model_name, device, **kwargs)
        self.load_model()
    
    def load_model(self) -> None:
        """加载模型"""
        try:
            # 判断模型类型
            if "clip" in self.model_name.lower():
                self._load_clip_model()
            else:
                self._load_sentence_transformer()
        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")
            raise
    
    def _load_sentence_transformer(self) -> None:
        """加载 Sentence Transformer 模型"""
        from sentence_transformers import SentenceTransformer
        
        self.model = SentenceTransformer(self.model_name)
        self.model.to(self.device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.model_type = "sentence_transformer"
    
    def _load_clip_model(self) -> None:
        """加载 CLIP 模型"""
        from transformers import CLIPProcessor, CLIPModel
        
        self.model = CLIPModel.from_pretrained(self.model_name)
        self.processor = CLIPProcessor.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.dimension = self.model.config.projection_dim
        self.model_type = "clip"
    
    def embed_text(self, texts: Union[str, List[str]]) -> np.ndarray:
        """文本嵌入"""
        if isinstance(texts, str):
            texts = [texts]
        
        if self.model_type == "clip":
            inputs = self.processor(
                text=texts,
                return_tensors="pt",
                padding=True,
                truncation=True
            ).to(self.device)
            
            with torch.no_grad():
                text_features = self.model.get_text_features(**inputs)
                embeddings = text_features.cpu().numpy()
        else:
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False
            )
        
        return self.normalize_vector(embeddings)
    
    def embed_image(self, images: Union[str, List[str]]) -> np.ndarray:
        """图片嵌入"""
        if isinstance(images, str):
            images = [images]
        
        if self.model_type != "clip":
            raise ValueError(f"Model {self.model_name} does not support image embedding")
        
        # 加载图片
        pil_images = []
        for img_path in images:
            try:
                img = Image.open(img_path).convert("RGB")
                pil_images.append(img)
            except Exception as e:
                print(f"Error loading image {img_path}: {e}")
                raise
        
        inputs = self.processor(
            images=pil_images,
            return_tensors="pt",
            padding=True
        ).to(self.device)
        
        import torch
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            embeddings = image_features.cpu().numpy()
        
        return self.normalize_vector(embeddings)
    
    def embed_batch(self, items: List[Union[str, Image.Image]], 
                   item_type: str = "text", batch_size: int = 32) -> np.ndarray:
        """批量嵌入"""
        all_embeddings = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            if item_type == "text":
                embeddings = self.embed_text(batch)
            elif item_type == "image":
                embeddings = self.embed_image(batch)
            else:
                raise ValueError(f"Unsupported item type: {item_type}")
            
            all_embeddings.append(embeddings)
        
        return np.vstack(all_embeddings)


import torch  # Import at the top level for the module
