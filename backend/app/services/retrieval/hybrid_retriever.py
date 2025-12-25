"""
混合检索器 - 结合稠密向量和稀疏向量
"""
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from collections import defaultdict
import re


class BM25:
    """BM25 稀疏检索算法"""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents = []
        self.doc_lengths = []
        self.avg_doc_length = 0
        self.doc_freqs = {}
        self.idf = {}
        self.doc_count = 0
    
    def tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 中文字符分割 + 英文单词分割
        tokens = []
        
        # 提取中文字符
        chinese = re.findall(r'[\u4e00-\u9fff]+', text)
        for word in chinese:
            tokens.extend(list(word))  # 中文按字分
        
        # 提取英文单词
        english = re.findall(r'[a-zA-Z]+', text.lower())
        tokens.extend(english)
        
        return tokens
    
    def index(self, documents: List[Dict[str, Any]]):
        """建立索引"""
        self.documents = documents
        self.doc_count = len(documents)
        
        # 统计文档长度和词频
        for doc in documents:
            text = doc.get('text', '') + ' ' + doc.get('ocr_text', '')
            tokens = self.tokenize(text)
            self.doc_lengths.append(len(tokens))
            
            # 统计文档频率
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1
        
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        
        # 计算 IDF
        for token, freq in self.doc_freqs.items():
            self.idf[token] = np.log((self.doc_count - freq + 0.5) / (freq + 0.5) + 1.0)
    
    def score_document(self, query_tokens: List[str], doc_tokens: List[str], doc_length: int) -> float:
        """计算单个文档的 BM25 分数"""
        score = 0.0
        token_freqs = defaultdict(int)
        
        for token in doc_tokens:
            token_freqs[token] += 1
        
        for token in query_tokens:
            if token not in token_freqs:
                continue
            
            tf = token_freqs[token]
            idf = self.idf.get(token, 0)
            
            # BM25 公式
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length)
            
            score += idf * numerator / denominator
        
        return score
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """搜索文档"""
        query_tokens = self.tokenize(query)
        
        scores = []
        for i, doc in enumerate(self.documents):
            text = doc.get('text', '') + ' ' + doc.get('ocr_text', '')
            doc_tokens = self.tokenize(text)
            score = self.score_document(query_tokens, doc_tokens, self.doc_lengths[i])
            scores.append((i, score))
        
        # 排序并返回 top-k
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]


class HybridRetriever:
    """混合检索器 - 结合向量检索和 BM25"""
    
    def __init__(self, vector_retriever, alpha: float = 0.5):
        """
        Args:
            vector_retriever: 向量检索器（CLIP）
            alpha: 稠密向量权重 (1-alpha 为 BM25 权重)
        """
        self.vector_retriever = vector_retriever
        self.bm25 = BM25()
        self.alpha = alpha
        self.documents = []
    
    def index(self, documents: List[Dict[str, Any]]):
        """建立混合索引"""
        self.documents = documents
        
        # 为 BM25 建立索引
        self.bm25.index(documents)
        print(f"Indexed {len(documents)} documents for hybrid search")
    
    def search(
        self, 
        query: str, 
        top_k: int = 10,
        use_rrf: bool = False  # 默认使用加权融合
    ) -> List[Dict[str, Any]]:
        """
        混合检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            use_rrf: 是否使用 RRF (Reciprocal Rank Fusion)，默认False使用加权融合
            
        Returns:
            检索结果列表
        """
        # 1. 向量检索
        vector_results = self.vector_retriever.search(query, top_k=50)
        
        # 2. BM25 检索
        bm25_results = self.bm25.search(query, top_k=50)
        
        # 3. 结果融合 - 使用加权融合保留BM25高分
        if use_rrf:
            final_scores = self._reciprocal_rank_fusion(vector_results, bm25_results)
        else:
            final_scores = self._weighted_fusion(vector_results, bm25_results)
        
        # 4. 排序并返回 top-k
        sorted_results = sorted(final_scores.items(), key=lambda x: -x[1])[:top_k]
        
        # 5. 格式化结果
        results = []
        for doc_id, score in sorted_results:
            doc = self.documents[doc_id].copy()
            doc['hybrid_score'] = float(score)
            results.append(doc)
        
        return results
    
    def _weighted_fusion(
        self, 
        vector_results: List[Tuple[int, float]], 
        bm25_results: List[Tuple[int, float]]
    ) -> Dict[int, float]:
        """
        加权融合（无归一化版本）
        
        保留BM25的原始高分，使相关文档能显著高于不相关文档
        alpha较小时BM25权重更高，更适合关键词匹配场景
        """
        scores = defaultdict(float)
        
        # 向量分数（已经在0-1范围）
        for doc_id, score in vector_results:
            scores[doc_id] += self.alpha * score
        
        # BM25分数（保留原始分数，通常0-5范围）
        for doc_id, score in bm25_results:
            scores[doc_id] += (1 - self.alpha) * score
        
        return scores
    
    def _reciprocal_rank_fusion(
        self, 
        vector_results: List[Tuple[int, float]], 
        bm25_results: List[Tuple[int, float]],
        k: int = 60
    ) -> Dict[int, float]:
        """
        Reciprocal Rank Fusion (RRF)
        
        RRF(d) = Σ 1 / (k + rank_i(d))
        
        其中 k 是常数（通常为60），rank_i(d) 是文档 d 在第 i 个排序列表中的排名
        """
        scores = defaultdict(float)
        
        # 向量检索结果
        for rank, (doc_id, _) in enumerate(vector_results, start=1):
            scores[doc_id] += 1.0 / (k + rank)
        
        # BM25 结果
        for rank, (doc_id, _) in enumerate(bm25_results, start=1):
            scores[doc_id] += 1.0 / (k + rank)
        
        return scores


class QueryExpander:
    """查询扩展器"""
    
    def __init__(self):
        # 同义词词典（可以扩展）
        self.synonyms = {
            '小红书': ['RED', '小红书APP', '小红书平台', '种草平台'],
            '营销': ['推广', '宣传', '运营'],
            '教程': ['指南', '攻略', '教学'],
            '方法': ['技巧', '方式', '策略'],
            # 人名映射（中英文）
            '李宏毅': ['Hung-yi Lee', 'Lee Hung-yi', 'Hongyi Li', 'Li Hongyi'],
            '吴恩达': ['Andrew Ng', 'Ng Andrew'],
            '李飞飞': ['Fei-Fei Li', 'Li Fei-Fei'],
        }
    
    def expand(self, query: str) -> List[str]:
        """扩展查询"""
        expanded = [query]
        
        # 添加同义词
        for word, syns in self.synonyms.items():
            if word in query:
                for syn in syns:
                    expanded.append(query.replace(word, syn))
        
        return expanded
    
    def add_synonym(self, word: str, synonyms: List[str]):
        """添加同义词"""
        self.synonyms[word] = synonyms


class MultiPathRetriever:
    """多路召回检索器"""
    
    def __init__(self, hybrid_retriever: HybridRetriever):
        self.hybrid_retriever = hybrid_retriever
        self.query_expander = QueryExpander()
    
    def search(
        self, 
        query: str, 
        top_k: int = 10,
        expand_query: bool = True
    ) -> List[Dict[str, Any]]:
        """
        多路召回搜索
        
        Args:
            query: 原始查询
            top_k: 最终返回数量
            expand_query: 是否进行查询扩展
        """
        all_results = {}
        
        # 路径1: 原始查询
        results1 = self.hybrid_retriever.search(query, top_k=top_k * 2)
        for r in results1:
            doc_id = r['file_id']
            all_results[doc_id] = {
                'result': r,
                'max_score': r.get('hybrid_score', 0),
                'score_count': 1
            }
        
        # 路径2: 查询扩展
        if expand_query:
            expanded_queries = self.query_expander.expand(query)
            for exp_query in expanded_queries[1:]:  # 跳过原始查询
                results2 = self.hybrid_retriever.search(exp_query, top_k=top_k)
                for r in results2:
                    doc_id = r['file_id']
                    current_score = r.get('hybrid_score', 0)
                    
                    if doc_id not in all_results:
                        # 新文档
                        all_results[doc_id] = {
                            'result': r,
                            'max_score': current_score,
                            'score_count': 1
                        }
                    else:
                        # 已存在文档，更新为更高分数
                        old_score = all_results[doc_id]['max_score']
                        if current_score > old_score:
                            # 调试日志：分数提升
                            print(f"[DEBUG] Score boost for {r.get('filename', doc_id)}: {old_score:.4f} → {current_score:.4f} (query: {exp_query})")
                            all_results[doc_id]['max_score'] = current_score
                            all_results[doc_id]['result'] = r  # 使用高分查询的结果
                        all_results[doc_id]['score_count'] += 1
        
        # 去重并返回 top-k，使用最高分数排序
        unique_results = []
        for doc_id, data in all_results.items():
            result = data['result'].copy()
            result['hybrid_score'] = data['max_score']  # 使用最高分数
            result['match_count'] = data['score_count']  # 记录匹配次数
            unique_results.append(result)
        
        unique_results.sort(key=lambda x: -x.get('hybrid_score', 0))
        
        return unique_results[:top_k]


# 使用示例
if __name__ == "__main__":
    # 模拟数据
    documents = [
        {
            'file_id': '1',
            'filename': '小红书营销.pdf',
            'text': '小红书是一个生活方式平台',
            'ocr_text': '小红书营销攻略',
            'vector': np.random.rand(512)
        },
        {
            'file_id': '2',
            'filename': 'marketing.pdf',
            'text': '社交媒体推广方法',
            'ocr_text': '营销技巧分享',
            'vector': np.random.rand(512)
        }
    ]
    
    # 模拟向量检索器
    class MockVectorRetriever:
        def __init__(self, docs):
            self.docs = docs
        
        def search(self, query, top_k=10):
            # 简单返回所有文档
            return [(i, 0.8) for i in range(len(self.docs))]
    
    # 创建混合检索器
    vector_retriever = MockVectorRetriever(documents)
    hybrid = HybridRetriever(vector_retriever, alpha=0.5)
    hybrid.index(documents)
    
    # 搜索
    results = hybrid.search("小红书营销", top_k=5)
    
    print("混合检索结果:")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['filename']} - Score: {r['hybrid_score']:.3f}")
