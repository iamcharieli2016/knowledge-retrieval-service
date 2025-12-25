"""
知识检索核心服务
"""
import uuid
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..core.config import Settings
from ..models.schemas import FileType, ProcessingStatus
from .embeddings.factory import EmbedderFactory
from .storage.factory import VectorDBFactory
from .processors.factory import ProcessorFactory
from .retrieval import HybridRetriever, MultiPathRetriever


class VectorRetrieverAdapter:
    """向量检索适配器 - 将 KnowledgeRetrievalService 适配为 HybridRetriever 期望的接口"""
    
    def __init__(self, service):
        self.service = service
        self.doc_id_to_index = {}  # file_id -> index 映射
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        搜索接口适配
        返回: List[Tuple[doc_index, score]]
        """
        # 生成查询向量
        q_vector = self.service.embedder.embed_text(query)
        if len(q_vector.shape) > 1:
            q_vector = q_vector.flatten()
        
        # 向量检索
        results = self.service.vector_db.search(
            query_vector=q_vector,
            top_k=top_k,
            filter=None
        )
        
        # 转换为 (doc_index, score) 格式
        indexed_results = []
        for vector_id, similarity, metadata in results:
            file_id = metadata.get('file_id')
            # 为每个文档分配一个索引
            if file_id not in self.doc_id_to_index:
                self.doc_id_to_index[file_id] = len(self.doc_id_to_index)
            doc_index = self.doc_id_to_index[file_id]
            indexed_results.append((doc_index, float(similarity)))
        
        return indexed_results


class KnowledgeRetrievalService:
    """知识检索服务"""
    
    def __init__(self, settings: Settings):
        """
        初始化服务
        
        Args:
            settings: 配置对象
        """
        self.settings = settings
        self.embedder = None
        self.vector_db = None
        self.file_metadata: Dict[str, Dict[str, Any]] = {}
        
        # 混合检索相关
        self.hybrid_retriever = None
        self.multi_path_retriever = None
        self._hybrid_indexed = False
        
        # 初始化组件
        self._initialize_embedder()
        self._initialize_vector_db()
        self._initialize_hybrid_retriever()
    
    def _initialize_embedder(self) -> None:
        """初始化嵌入器"""
        try:
            self.embedder = EmbedderFactory.create_embedder(
                provider=self.settings.embedding.provider,
                model_name=self.settings.embedding.model_name,
                device=self.settings.embedding.device
            )
            print(f"Embedder initialized: {self.settings.embedding.model_name}")
        except Exception as e:
            print(f"Error initializing embedder: {e}")
            raise
    
    def _initialize_vector_db(self) -> None:
        """初始化向量数据库"""
        try:
            provider = self.settings.vector_db.provider
            config = getattr(self.settings.vector_db, provider, {})
            
            if config is None:
                config = {}
            
            self.vector_db = VectorDBFactory.create_database(
                provider=provider,
                **config
            )
            print(f"Vector database initialized: {provider}")
        except Exception as e:
            print(f"Error initializing vector database: {e}")
            raise
    
    def _initialize_hybrid_retriever(self) -> None:
        """初始化混合检索器"""
        try:
            # 检查是否启用混合检索
            enable_hybrid = getattr(self.settings.retrieval, 'enable_hybrid', False)
            if enable_hybrid:
                alpha = getattr(self.settings.retrieval, 'hybrid_alpha', 0.5)
                # 创建向量检索适配器
                vector_adapter = VectorRetrieverAdapter(self)
                self.hybrid_retriever = HybridRetriever(
                    vector_retriever=vector_adapter,
                    alpha=alpha
                )
                print(f"Hybrid retriever initialized (alpha={alpha})")
                
                # 检查是否启用多路召回
                enable_multi_path = getattr(self.settings.retrieval, 'enable_multi_path', False)
                if enable_multi_path:
                    self.multi_path_retriever = MultiPathRetriever(self.hybrid_retriever)
                    print("Multi-path retriever initialized")
        except Exception as e:
            print(f"Error initializing hybrid retriever: {e}")
            import traceback
            traceback.print_exc()
            # 混合检索失败不影响基础功能
            self.hybrid_retriever = None
            self.multi_path_retriever = None
    
    async def upload_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        上传并处理文件
        
        Args:
            file_path: 文件路径
            filename: 文件名
            
        Returns:
            处理结果
        """
        start_time = time.time()
        
        # 生成文件 ID
        file_id = str(uuid.uuid4())
        
        try:
            # 获取文件类型
            file_type = ProcessorFactory.get_file_type(file_path)
            
            if file_type == "unknown":
                raise ValueError(f"Unsupported file type: {filename}")
            
            # 创建处理器
            processor_config = getattr(self.settings.file_processing, file_type, {})
            if processor_config is None:
                processor_config = {}
                
            processor = ProcessorFactory.create_processor(
                file_path=file_path,
                **processor_config
            )
            
            # 处理文件
            result = processor.process(file_path)
            
            # 生成嵌入
            embeddings = await self._generate_embeddings(result, file_type)
            
            # 存储到向量数据库
            metadata = {
                "file_id": file_id,
                "filename": filename,
                "file_type": file_type,
                "file_path": file_path,
                **result.get("metadata", {})
            }
            
            vector_ids = self.vector_db.insert(
                vectors=embeddings,
                metadatas=[metadata] * len(embeddings),
                ids=[f"{file_id}_{i}" for i in range(len(embeddings))]
            )
            
            # 保存元数据
            processing_time = time.time() - start_time
            
            self.file_metadata[file_id] = {
                "file_id": file_id,
                "filename": filename,
                "file_type": file_type,
                "file_path": file_path,
                "vector_ids": vector_ids,
                "processing_time": processing_time,
                "status": ProcessingStatus.COMPLETED,
                "metadata": metadata
            }
            
            # 标记混合索引需要更新
            self._hybrid_indexed = False
            
            return {
                "file_id": file_id,
                "filename": filename,
                "file_type": file_type,
                "status": ProcessingStatus.COMPLETED,
                "processing_time": processing_time,
                "vector_count": len(embeddings)
            }
            
        except Exception as e:
            # 标记为失败
            self.file_metadata[file_id] = {
                "file_id": file_id,
                "filename": filename,
                "status": ProcessingStatus.FAILED,
                "error": str(e)
            }
            raise
    
    async def _generate_embeddings(self, processed_data: Dict[str, Any], 
                                   file_type: str) -> np.ndarray:
        """
        生成嵌入向量
        
        Args:
            processed_data: 处理后的数据
            file_type: 文件类型
            
        Returns:
            嵌入向量数组
        """
        if file_type == "image":
            # 图片嵌入
            file_path = processed_data["file_path"]
            image_embedding = self.embedder.embed_image(file_path)
            
            # 确保是二维数组
            if len(image_embedding.shape) == 1:
                image_embedding = image_embedding.reshape(1, -1)
            
            # 如果有 OCR 提取的文字，也生成文字向量
            text_content = processed_data.get("text_content", "")
            if text_content and text_content.strip():
                print(f"Generating text embedding for OCR text: {text_content[:50]}...")
                text_embedding = self.embedder.embed_text([text_content])
                
                # 合并图像向量和文字向量
                embeddings = np.vstack([image_embedding, text_embedding])
                print(f"Combined embeddings: image + text = {embeddings.shape}")
            else:
                embeddings = image_embedding
                
        elif file_type == "document":
            # 文档嵌入（使用文本块）
            chunks = processed_data.get("chunks", [processed_data["content"]])
            
            if not chunks:
                chunks = [processed_data["content"]]
            
            embeddings = self.embedder.embed_text(chunks)
            
        elif file_type == "audio":
            # 音频嵌入（使用转写文本）
            text_content = processed_data.get("text_content", "")
            
            if not text_content or not text_content.strip():
                # 如果转写为空，使用文件名
                text_content = processed_data.get("metadata", {}).get("file_name", "audio file")
            
            print(f"Generating audio embedding for transcribed text: {text_content[:100]}...")
            embeddings = self.embedder.embed_text([text_content])
            
        else:
            raise ValueError(f"Unsupported file type for embedding: {file_type}")
        
        return embeddings
    
    async def search(self, query: Optional[str] = None, 
                    file_id: Optional[str] = None,
                    query_vector: Optional[np.ndarray] = None,
                    top_k: int = 10,
                    threshold: float = 0.0,
                    filter: Optional[Dict[str, Any]] = None,
                    use_hybrid: bool = True) -> List[Dict[str, Any]]:
        """
        搜索相似内容
        
        Args:
            query: 文本查询
            file_id: 文件ID作为查询
            query_vector: 查询向量
            top_k: 返回结果数量
            threshold: 相似度阈值
            filter: 过滤条件
            use_hybrid: 是否使用混合检索
            
        Returns:
            搜索结果列表
        """
        start_time = time.time()
        
        # 尝试使用混合检索（仅当有文本查询时）
        if use_hybrid and query and self.multi_path_retriever:
            return await self._hybrid_search(query, top_k, threshold, start_time)
        elif use_hybrid and query and self.hybrid_retriever:
            return await self._simple_hybrid_search(query, top_k, threshold, start_time)
        
        # 回退到原始向量检索
        # 生成查询向量
        if query_vector is not None:
            q_vector = query_vector
        elif query is not None:
            q_vector = self.embedder.embed_text(query)
        elif file_id is not None:
            # 从向量数据库获取文件向量
            file_info = self.file_metadata.get(file_id)
            if not file_info:
                raise ValueError(f"File not found: {file_id}")
            
            vector_id = file_info["vector_ids"][0]
            result = self.vector_db.get_by_id(vector_id)
            
            if result is None:
                raise ValueError(f"Vector not found for file: {file_id}")
            
            q_vector, _ = result
        else:
            raise ValueError("Either query, file_id, or query_vector must be provided")
        
        # 确保查询向量是一维的
        if len(q_vector.shape) > 1:
            q_vector = q_vector.flatten()
        
        # 搜索
        results = self.vector_db.search(
            query_vector=q_vector,
            top_k=top_k,
            filter=filter
        )
        
        # 格式化结果
        formatted_results = []
        for vector_id, similarity, metadata in results:
            if similarity >= threshold:
                formatted_results.append({
                    "file_id": metadata.get("file_id"),
                    "filename": metadata.get("filename"),
                    "file_type": metadata.get("file_type"),
                    "similarity": float(similarity),
                    "metadata": metadata
                })
        
        query_time = time.time() - start_time
        
        return {
            "results": formatted_results,
            "total": len(formatted_results),
            "query_time": query_time
        }
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        更新配置
        
        Args:
            updates: 配置更新
        """
        # 更新嵌入模型
        if "embedding_model" in updates or "embedding_provider" in updates:
            provider = updates.get("embedding_provider", self.settings.embedding.provider)
            model_name = updates.get("embedding_model", self.settings.embedding.model_name)
            
            self.embedder = EmbedderFactory.create_embedder(
                provider=provider,
                model_name=model_name,
                device=self.settings.embedding.device
            )
            
            # 更新配置
            if "embedding_provider" in updates:
                self.settings.embedding.provider = provider
            if "embedding_model" in updates:
                self.settings.embedding.model_name = model_name
        
        # 更新向量数据库
        if "vector_db_provider" in updates:
            provider = updates["vector_db_provider"]
            config = getattr(self.settings.vector_db, provider, {})
            
            if config is None:
                config = {}
            
            self.vector_db = VectorDBFactory.create_database(
                provider=provider,
                **config
            )
            
            self.settings.vector_db.provider = provider
        
        # 更新检索配置
        if "default_top_k" in updates:
            self.settings.retrieval.default_top_k = updates["default_top_k"]
        
        if "similarity_threshold" in updates:
            self.settings.retrieval.similarity_threshold = updates["similarity_threshold"]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_files = len(self.file_metadata)
        
        files_by_type = {}
        for file_info in self.file_metadata.values():
            file_type = file_info.get("file_type", "unknown")
            files_by_type[file_type] = files_by_type.get(file_type, 0) + 1
        
        # 获取向量总数（使用file_metadata代替，避免ChromaDB count()挂起）
        # 每个文件可能有多个向量，这里简单估算
        total_vectors = sum(file_info.get("vector_count", 1) for file_info in self.file_metadata.values())
        
        return {
            "total_files": total_files,
            "files_by_type": files_by_type,
            "total_vectors": total_vectors,
            "storage_used": 0  # 可以添加实际存储计算
        }
    
    def delete_file(self, file_id: str) -> bool:
        """删除文件"""
        if file_id not in self.file_metadata:
            return False
        
        file_info = self.file_metadata[file_id]
        vector_ids = file_info.get("vector_ids", [])
        
        # 从向量数据库删除
        if vector_ids:
            self.vector_db.delete(vector_ids)
        
        # 删除元数据
        del self.file_metadata[file_id]
        
        return True
    
    async def _prepare_documents_for_hybrid(self) -> List[Dict[str, Any]]:
        """准备文档数据用于混合检索"""
        documents = []
        for fid, file_info in self.file_metadata.items():
            metadata = file_info.get('metadata', {})
            
            # 提取文本内容
            text_content = metadata.get('content', '')
            ocr_text = metadata.get('ocr_text', '')
            
            # 合并所有文本用于搜索
            combined_text = f"{text_content} {ocr_text} {file_info.get('filename', '')}".strip()
            
            doc = {
                'file_id': fid,
                'filename': file_info.get('filename', ''),
                'file_type': file_info.get('file_type', ''),
                'text': combined_text,  # 使用合并后的文本
                'ocr_text': ocr_text
            }
            documents.append(doc)
        return documents
    
    async def _hybrid_search(self, query: str, top_k: int, threshold: float, start_time: float) -> Dict[str, Any]:
        """多路召回混合检索"""
        try:
            # 准备文档数据并建立索引（首次或文档更新时）
            if not self._hybrid_indexed:
                documents = await self._prepare_documents_for_hybrid()
                if documents:
                    self.hybrid_retriever.index(documents)
                    self._hybrid_indexed = True
                    print(f"Hybrid index built with {len(documents)} documents")
            
            # 多路召回检索
            results = self.multi_path_retriever.search(
                query, 
                top_k=top_k,
                expand_query=True
            )
            
            # 格式化结果
            formatted_results = []
            for result in results:
                hybrid_score = result.get('hybrid_score', 0)
                if hybrid_score >= threshold:
                    formatted_results.append({
                        'file_id': result['file_id'],
                        'filename': result['filename'],
                        'file_type': result['file_type'],
                        'similarity': float(hybrid_score),
                        'metadata': result,
                        'method': 'multi_path_hybrid'
                    })
            
            query_time = time.time() - start_time
            
            return {
                'results': formatted_results,
                'total': len(formatted_results),
                'query_time': query_time,
                'method': 'multi_path_hybrid'
            }
        except Exception as e:
            print(f"Hybrid search error: {e}, falling back to vector search")
            # 出错时回退到向量检索
            return await self._vector_search(query, top_k, threshold, start_time)
    
    async def _simple_hybrid_search(self, query: str, top_k: int, threshold: float, start_time: float) -> Dict[str, Any]:
        """简单混合检索（无查询扩展）"""
        try:
            # 准备文档数据并建立索引
            if not self._hybrid_indexed:
                documents = await self._prepare_documents_for_hybrid()
                if documents:
                    self.hybrid_retriever.index(documents)
                    self._hybrid_indexed = True
                    print(f"Hybrid index built with {len(documents)} documents")
            
            # 混合检索
            results = self.hybrid_retriever.search(query, top_k=top_k, use_rrf=True)
            
            # 格式化结果
            formatted_results = []
            for result in results:
                hybrid_score = result.get('hybrid_score', 0)
                if hybrid_score >= threshold:
                    formatted_results.append({
                        'file_id': result['file_id'],
                        'filename': result['filename'],
                        'file_type': result['file_type'],
                        'similarity': float(hybrid_score),
                        'metadata': result,
                        'method': 'hybrid'
                    })
            
            query_time = time.time() - start_time
            
            return {
                'results': formatted_results,
                'total': len(formatted_results),
                'query_time': query_time,
                'method': 'hybrid'
            }
        except Exception as e:
            print(f"Hybrid search error: {e}, falling back to vector search")
            return await self._vector_search(query, top_k, threshold, start_time)
    
    async def _vector_search(self, query: str, top_k: int, threshold: float, start_time: float) -> Dict[str, Any]:
        """纯向量检索（回退方案）"""
        q_vector = self.embedder.embed_text(query)
        
        if len(q_vector.shape) > 1:
            q_vector = q_vector.flatten()
        
        results = self.vector_db.search(
            query_vector=q_vector,
            top_k=top_k,
            filter=None
        )
        
        formatted_results = []
        for vector_id, similarity, metadata in results:
            if similarity >= threshold:
                formatted_results.append({
                    'file_id': metadata.get('file_id'),
                    'filename': metadata.get('filename'),
                    'file_type': metadata.get('file_type'),
                    'similarity': float(similarity),
                    'metadata': metadata,
                    'method': 'vector'
                })
        
        query_time = time.time() - start_time
        
        return {
            'results': formatted_results,
            'total': len(formatted_results),
            'query_time': query_time,
            'method': 'vector'
        }
