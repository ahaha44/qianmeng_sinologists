#!/usr/bin/env python3
"""
GraphRAG 集成方案
使用Microsoft GraphRAG或LlamaIndex的知识图谱RAG实现
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GraphRAG相关依赖检查
try:
    # Microsoft GraphRAG
    from graphrag import GraphRAG
    from graphrag.index import create_index
    from graphrag.query import GraphRAGQuery
    GRAPHRAG_AVAILABLE = True
except ImportError:
    GRAPHRAG_AVAILABLE = False
    logger.warning("Microsoft GraphRAG未安装")

try:
    # LlamaIndex作为备选方案
    from llama_index import (
        Document,
        VectorStoreIndex,
        StorageContext,
        KnowledgeGraphIndex,
        ServiceContext
    )
    from llama_index.graph_stores import SimpleGraphStore
    from llama_index.llms import OpenAI
    from llama_index.embeddings import OpenAIEmbedding
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    LLAMAINDEX_AVAILABLE = False
    logger.warning("LlamaIndex未安装")

try:
    # LangChain GraphRAG支持
    from langchain.graphs import NetworkxEntityGraph
    from langchain.indexes import GraphIndexCreator
    from langchain.llms import OpenAI as LangChainOpenAI
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.document_loaders import JSONLoader
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain未安装")

# NetworkX用于图操作
try:
    import networkx as nx
    from pyvis.network import Network
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    logger.warning("NetworkX/PyVis未安装")


class ScholarGraphRAG:
    """
    汉学家知识图谱RAG系统
    支持多种GraphRAG实现
    """
    
    def __init__(self, backend: str = "auto", api_key: Optional[str] = None):
        """
        初始化GraphRAG系统
        
        Args:
            backend: 使用的后端 ("microsoft", "llamaindex", "langchain", "auto")
            api_key: OpenAI API密钥（如果需要）
        """
        self.backend = self._select_backend(backend)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.graph = None
        self.index = None
        
        # 初始化选定的后端
        self._init_backend()
    
    def _select_backend(self, backend: str) -> str:
        """选择可用的后端"""
        if backend == "auto":
            if GRAPHRAG_AVAILABLE:
                return "microsoft"
            elif LLAMAINDEX_AVAILABLE:
                return "llamaindex"
            elif LANGCHAIN_AVAILABLE:
                return "langchain"
            else:
                return "networkx"  # 基础实现
        return backend
    
    def _init_backend(self):
        """初始化选定的后端"""
        logger.info(f"初始化GraphRAG后端: {self.backend}")
        
        if self.backend == "microsoft" and GRAPHRAG_AVAILABLE:
            self._init_microsoft_graphrag()
        elif self.backend == "llamaindex" and LLAMAINDEX_AVAILABLE:
            self._init_llamaindex()
        elif self.backend == "langchain" and LANGCHAIN_AVAILABLE:
            self._init_langchain()
        else:
            self._init_networkx()
    
    def _init_microsoft_graphrag(self):
        """初始化Microsoft GraphRAG"""
        # Microsoft GraphRAG配置
        config = {
            "llm": {
                "type": "openai",
                "api_key": self.api_key,
                "model": "gpt-4"
            },
            "embeddings": {
                "type": "openai",
                "api_key": self.api_key
            }
        }
        self.graphrag = GraphRAG(config)
    
    def _init_llamaindex(self):
        """初始化LlamaIndex知识图谱"""
        if not self.api_key:
            logger.warning("需要OpenAI API密钥")
            return
        
        # 配置LLM和嵌入模型
        llm = OpenAI(temperature=0, model="gpt-4", api_key=self.api_key)
        embed_model = OpenAIEmbedding(api_key=self.api_key)
        
        # 创建服务上下文
        self.service_context = ServiceContext.from_defaults(
            llm=llm,
            embed_model=embed_model
        )
        
        # 创建图存储
        self.graph_store = SimpleGraphStore()
        self.storage_context = StorageContext.from_defaults(
            graph_store=self.graph_store
        )
    
    def _init_langchain(self):
        """初始化LangChain图索引"""
        if not self.api_key:
            logger.warning("需要OpenAI API密钥")
            return
        
        self.llm = LangChainOpenAI(
            temperature=0,
            openai_api_key=self.api_key
        )
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.api_key
        )
        
        # 创建实体图
        self.entity_graph = NetworkxEntityGraph()
        
        # 文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def _init_networkx(self):
        """初始化基础NetworkX图"""
        if not NETWORKX_AVAILABLE:
            logger.error("请安装networkx: pip install networkx pyvis")
            return
        
        self.graph = nx.DiGraph()
        logger.info("使用NetworkX基础图实现")
    
    async def load_scholars_data(self, data_path: str):
        """
        加载汉学家数据到图谱
        
        Args:
            data_path: 数据文件路径（JSON格式）
        """
        with open(data_path, 'r', encoding='utf-8') as f:
            scholars_data = json.load(f)
        
        if self.backend == "microsoft":
            await self._load_microsoft(scholars_data)
        elif self.backend == "llamaindex":
            self._load_llamaindex(scholars_data)
        elif self.backend == "langchain":
            self._load_langchain(scholars_data)
        else:
            self._load_networkx(scholars_data)
    
    async def _load_microsoft(self, data: List[Dict]):
        """加载数据到Microsoft GraphRAG"""
        # 创建文档
        documents = []
        for scholar in data:
            doc_text = self._scholar_to_text(scholar)
            documents.append({
                "id": scholar.get("id", scholar["name"]),
                "text": doc_text,
                "metadata": scholar
            })
        
        # 创建索引
        self.index = await create_index(
            documents=documents,
            config=self.graphrag.config
        )
        logger.info(f"Microsoft GraphRAG索引创建完成，包含{len(documents)}个文档")
    
    def _load_llamaindex(self, data: List[Dict]):
        """加载数据到LlamaIndex"""
        # 创建文档
        documents = []
        for scholar in data:
            doc = Document(
                text=self._scholar_to_text(scholar),
                metadata=scholar
            )
            documents.append(doc)
        
        # 创建知识图谱索引
        self.index = KnowledgeGraphIndex.from_documents(
            documents,
            service_context=self.service_context,
            storage_context=self.storage_context,
            show_progress=True
        )
        logger.info(f"LlamaIndex知识图谱创建完成，包含{len(documents)}个文档")
    
    def _load_langchain(self, data: List[Dict]):
        """加载数据到LangChain"""
        # 构建文本文档
        texts = []
        metadatas = []
        
        for scholar in data:
            text = self._scholar_to_text(scholar)
            texts.append(text)
            metadatas.append(scholar)
        
        # 分割文本
        split_texts = self.text_splitter.create_documents(
            texts=texts,
            metadatas=metadatas
        )
        
        # 创建图索引
        graph_creator = GraphIndexCreator(
            llm=self.llm,
            embeddings=self.embeddings
        )
        
        self.index = graph_creator.from_documents(split_texts)
        logger.info(f"LangChain图索引创建完成，包含{len(data)}个学者")
    
    def _load_networkx(self, data: List[Dict]):
        """加载数据到NetworkX图"""
        for scholar in data:
            # 添加学者节点
            self.graph.add_node(
                scholar["name"],
                **scholar
            )
            
            # 添加关系边
            if scholar.get("mentors"):
                for mentor in scholar["mentors"]:
                    self.graph.add_edge(
                        mentor, 
                        scholar["name"],
                        relationship="mentor"
                    )
            
            if scholar.get("collaborators"):
                for collaborator in scholar["collaborators"]:
                    self.graph.add_edge(
                        scholar["name"],
                        collaborator,
                        relationship="collaboration"
                    )
            
            if scholar.get("institutions"):
                for institution in scholar["institutions"]:
                    self.graph.add_node(
                        institution,
                        type="institution"
                    )
                    self.graph.add_edge(
                        scholar["name"],
                        institution,
                        relationship="affiliation"
                    )
        
        logger.info(f"NetworkX图创建完成: {self.graph.number_of_nodes()}个节点, {self.graph.number_of_edges()}条边")
    
    def _scholar_to_text(self, scholar: Dict) -> str:
        """将学者数据转换为文本描述"""
        text_parts = [
            f"{scholar['name']}是一位汉学家。"
        ]
        
        if scholar.get("name_zh"):
            text_parts.append(f"中文名：{scholar['name_zh']}。")
        
        if scholar.get("birth_year") and scholar.get("death_year"):
            text_parts.append(f"生卒年：{scholar['birth_year']}-{scholar['death_year']}。")
        elif scholar.get("birth_year"):
            text_parts.append(f"出生年：{scholar['birth_year']}。")
        
        if scholar.get("nationality"):
            text_parts.append(f"国籍：{scholar['nationality']}。")
        
        if scholar.get("research_fields"):
            fields = "、".join(scholar["research_fields"])
            text_parts.append(f"研究领域：{fields}。")
        
        if scholar.get("institutions"):
            institutions = "、".join(scholar["institutions"][:3])
            text_parts.append(f"任职机构：{institutions}。")
        
        if scholar.get("major_works"):
            works = "、".join(scholar["major_works"][:3])
            text_parts.append(f"主要著作：{works}。")
        
        if scholar.get("abstract"):
            text_parts.append(scholar["abstract"][:200])
        
        return " ".join(text_parts)
    
    async def query(self, question: str, context_size: int = 5) -> Dict[str, Any]:
        """
        查询知识图谱
        
        Args:
            question: 自然语言问题
            context_size: 返回的上下文大小
            
        Returns:
            查询结果
        """
        if self.backend == "microsoft":
            return await self._query_microsoft(question, context_size)
        elif self.backend == "llamaindex":
            return self._query_llamaindex(question, context_size)
        elif self.backend == "langchain":
            return self._query_langchain(question, context_size)
        else:
            return self._query_networkx(question, context_size)
    
    async def _query_microsoft(self, question: str, context_size: int) -> Dict:
        """Microsoft GraphRAG查询"""
        query = GraphRAGQuery(
            index=self.index,
            llm=self.graphrag.llm
        )
        
        result = await query.aquery(
            question,
            k=context_size
        )
        
        return {
            "answer": result.response,
            "context": result.context,
            "entities": result.entities,
            "relationships": result.relationships
        }
    
    def _query_llamaindex(self, question: str, context_size: int) -> Dict:
        """LlamaIndex查询"""
        query_engine = self.index.as_query_engine(
            response_mode="tree_summarize",
            verbose=True,
            similarity_top_k=context_size
        )
        
        response = query_engine.query(question)
        
        # 提取图谱信息
        graph_info = self.graph_store.get_triplets(question)
        
        return {
            "answer": str(response),
            "source_nodes": [
                {
                    "text": node.node.text,
                    "metadata": node.node.metadata
                }
                for node in response.source_nodes
            ],
            "graph_triplets": graph_info
        }
    
    def _query_langchain(self, question: str, context_size: int) -> Dict:
        """LangChain查询"""
        # 使用图索引查询
        result = self.index.query(
            question,
            k=context_size
        )
        
        return {
            "answer": result["result"],
            "source_documents": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in result.get("source_documents", [])
            ]
        }
    
    def _query_networkx(self, question: str, context_size: int) -> Dict:
        """NetworkX基础查询（基于关键词）"""
        # 简单的关键词匹配
        keywords = question.lower().split()
        relevant_nodes = []
        
        for node, data in self.graph.nodes(data=True):
            node_text = str(data).lower()
            if any(keyword in node_text for keyword in keywords):
                relevant_nodes.append({
                    "name": node,
                    "data": data,
                    "connections": list(self.graph.neighbors(node))
                })
        
        # 限制返回数量
        relevant_nodes = relevant_nodes[:context_size]
        
        return {
            "answer": f"找到{len(relevant_nodes)}个相关学者",
            "results": relevant_nodes,
            "graph_stats": {
                "total_nodes": self.graph.number_of_nodes(),
                "total_edges": self.graph.number_of_edges()
            }
        }
    
    def visualize_graph(self, output_path: str = "docs/graph_visualization.html"):
        """
        可视化知识图谱
        
        Args:
            output_path: 输出HTML文件路径
        """
        if not NETWORKX_AVAILABLE:
            logger.error("需要安装pyvis: pip install pyvis")
            return
        
        # 创建可视化网络
        net = Network(
            height="750px",
            width="100%",
            bgcolor="#222222",
            font_color="white",
            notebook=False
        )
        
        if self.backend == "networkx" and self.graph:
            # 直接从NetworkX图创建
            net.from_nx(self.graph)
        else:
            # 从其他后端提取图数据
            # 这里需要根据具体后端实现
            logger.warning(f"{self.backend}后端的可视化尚未实现")
            return
        
        # 配置物理引擎
        net.set_options("""
        {
            "physics": {
                "enabled": true,
                "barnesHut": {
                    "gravitationalConstant": -8000,
                    "centralGravity": 0.3,
                    "springLength": 100
                }
            },
            "interaction": {
                "hover": true,
                "tooltipDelay": 100
            }
        }
        """)
        
        # 保存HTML
        net.save_graph(output_path)
        logger.info(f"图谱可视化已保存到: {output_path}")
    
    def get_scholar_subgraph(self, scholar_name: str, depth: int = 2) -> Dict:
        """
        获取特定学者的子图
        
        Args:
            scholar_name: 学者姓名
            depth: 子图深度
            
        Returns:
            子图数据
        """
        if self.backend != "networkx" or not self.graph:
            logger.warning("此功能仅支持NetworkX后端")
            return {}
        
        # 使用BFS获取子图
        subgraph_nodes = set()
        queue = [(scholar_name, 0)]
        
        while queue:
            node, current_depth = queue.pop(0)
            if current_depth > depth:
                continue
            
            if node in self.graph:
                subgraph_nodes.add(node)
                
                if current_depth < depth:
                    # 添加邻居节点
                    for neighbor in self.graph.neighbors(node):
                        queue.append((neighbor, current_depth + 1))
        
        # 创建子图
        subgraph = self.graph.subgraph(subgraph_nodes)
        
        return {
            "nodes": list(subgraph.nodes(data=True)),
            "edges": list(subgraph.edges(data=True)),
            "stats": {
                "node_count": subgraph.number_of_nodes(),
                "edge_count": subgraph.number_of_edges()
            }
        }


# 简单的CLI接口
async def main():
    """主函数"""
    print("=" * 60)
    print("GraphRAG 汉学家知识图谱系统")
    print("=" * 60)
    
    # 检查可用的后端
    print("\n可用的GraphRAG后端:")
    if GRAPHRAG_AVAILABLE:
        print("✓ Microsoft GraphRAG")
    if LLAMAINDEX_AVAILABLE:
        print("✓ LlamaIndex")
    if LANGCHAIN_AVAILABLE:
        print("✓ LangChain")
    if NETWORKX_AVAILABLE:
        print("✓ NetworkX (基础)")
    
    # 创建GraphRAG实例
    graphrag = ScholarGraphRAG(backend="auto")
    
    # 检查是否有数据文件
    data_file = "docs/scholars_enriched.json"
    if not os.path.exists(data_file):
        print(f"\n数据文件不存在: {data_file}")
        print("请先运行 extract_scholar_data.py 生成数据")
        
        # 创建示例数据
        example_data = [
            {
                "name": "Joseph Needham",
                "name_zh": "李约瑟",
                "birth_year": 1900,
                "death_year": 1995,
                "nationality": "British",
                "research_fields": ["科技史", "生物化学"],
                "institutions": ["Cambridge University"],
                "major_works": ["Science and Civilisation in China"],
                "abstract": "英国著名科学史家，研究中国科技史的先驱。"
            },
            {
                "name": "John King Fairbank",
                "name_zh": "费正清",
                "birth_year": 1907,
                "death_year": 1991,
                "nationality": "American",
                "research_fields": ["中国近代史", "中美关系"],
                "institutions": ["Harvard University"],
                "mentors": ["Charles Sidney Gardner"],
                "abstract": "美国汉学家，哈佛大学东亚研究中心创始人。"
            }
        ]
        
        # 保存示例数据
        with open("docs/example_graphrag_data.json", 'w', encoding='utf-8') as f:
            json.dump(example_data, f, ensure_ascii=False, indent=2)
        
        data_file = "docs/example_graphrag_data.json"
        print(f"已创建示例数据: {data_file}")
    
    # 加载数据
    print(f"\n加载数据: {data_file}")
    await graphrag.load_scholars_data(data_file)
    
    # 可视化图谱
    if NETWORKX_AVAILABLE:
        graphrag.visualize_graph()
        print("图谱可视化已生成: docs/graph_visualization.html")
    
    # 示例查询
    print("\n" + "=" * 60)
    print("示例查询")
    print("=" * 60)
    
    questions = [
        "Joseph Needham的主要研究领域是什么？",
        "哪些学者研究中国科技史？",
        "费正清和哈佛大学的关系？"
    ]
    
    for question in questions:
        print(f"\n问题: {question}")
        result = await graphrag.query(question)
        print(f"回答: {result.get('answer', '无结果')}")
        
        if 'results' in result:
            print(f"相关节点: {len(result['results'])}个")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())