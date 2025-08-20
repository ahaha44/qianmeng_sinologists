#!/usr/bin/env python3
"""
Transformer模型NER实现
使用HuggingFace的预训练模型进行命名实体识别
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import re

# 基础依赖（如果没有安装会提示）
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("警告: transformers未安装。请运行: pip install transformers torch")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("警告: BeautifulSoup未安装。请运行: pip install beautifulsoup4")


@dataclass
class ScholarEntity:
    """学者实体数据结构"""
    name: str
    name_zh: str = None
    birth_year: int = None
    death_year: int = None
    nationality: str = None
    institutions: List[str] = None
    research_fields: List[str] = None
    mentors: List[str] = None
    students: List[str] = None
    collaborators: List[str] = None
    major_works: List[str] = None
    awards: List[str] = None


class TransformerNER:
    """基于Transformer的命名实体识别器"""
    
    def __init__(self, model_name: str = None):
        """
        初始化NER模型
        
        Args:
            model_name: HuggingFace模型名称
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("请先安装transformers: pip install transformers torch")
        
        # 推荐的模型（按优先级）
        self.recommended_models = {
            'chinese': [
                'ckiplab/bert-base-chinese-ner',  # 中文NER
                'hfl/chinese-bert-wwm-ext',        # 中文BERT
                'bert-base-chinese'                 # 基础中文BERT
            ],
            'english': [
                'dslim/bert-base-NER',             # 英文NER专用
                'dbmdz/bert-large-cased-finetuned-conll03-english',  # CoNLL-03
                'Jean-Baptiste/camembert-ner'      # 多语言
            ],
            'multilingual': [
                'xlm-roberta-large-finetuned-conll03-english',  # 多语言NER
                'Davlan/bert-base-multilingual-cased-ner-hrl'   # 多语言NER
            ]
        }
        
        # 选择模型
        if model_name:
            self.model_name = model_name
        else:
            # 默认使用多语言模型（支持中英文）
            self.model_name = 'Davlan/bert-base-multilingual-cased-ner-hrl'
            print(f"使用默认模型: {self.model_name}")
        
        # 初始化pipeline
        self._init_pipeline()
    
    def _init_pipeline(self):
        """初始化NER pipeline"""
        try:
            print(f"加载模型: {self.model_name}")
            self.nlp = pipeline(
                "ner",
                model=self.model_name,
                aggregation_strategy="simple"
            )
            print("模型加载成功！")
        except Exception as e:
            print(f"模型加载失败: {e}")
            print("尝试使用备用模型...")
            # 使用简单的英文NER模型作为备用
            self.nlp = pipeline("ner", aggregation_strategy="simple")
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        从文本中提取命名实体
        
        Args:
            text: 输入文本
            
        Returns:
            分类的实体字典
        """
        if not text:
            return {}
        
        # 执行NER
        entities = self.nlp(text)
        
        # 分类整理实体
        categorized = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'misc': []
        }
        
        for entity in entities:
            entity_text = entity['word'].strip()
            entity_label = entity['entity_group']
            
            # 根据标签分类
            if entity_label in ['PER', 'PERSON', 'I-PER', 'B-PER']:
                categorized['persons'].append(entity_text)
            elif entity_label in ['ORG', 'ORGANIZATION', 'I-ORG', 'B-ORG']:
                categorized['organizations'].append(entity_text)
            elif entity_label in ['LOC', 'LOCATION', 'GPE', 'I-LOC', 'B-LOC']:
                categorized['locations'].append(entity_text)
            elif entity_label in ['DATE', 'TIME']:
                categorized['dates'].append(entity_text)
            else:
                categorized['misc'].append(entity_text)
        
        # 去重
        for key in categorized:
            categorized[key] = list(set(categorized[key]))
        
        return categorized
    
    def extract_relationships(self, text: str) -> List[Dict[str, str]]:
        """
        提取文本中的关系
        
        Args:
            text: 输入文本
            
        Returns:
            关系列表
        """
        relationships = []
        
        # 关系模式（使用正则表达式）
        patterns = {
            'mentor': [
                r'(?P<student>[\w\s]+) studied under (?P<mentor>[\w\s]+)',
                r'(?P<mentor>[\w\s]+) was the teacher of (?P<student>[\w\s]+)',
                r'(?P<student>[\w\s]+) was a student of (?P<mentor>[\w\s]+)',
                r'(?P<student>[\w\s]+)师从(?P<mentor>[\w\s]+)',
            ],
            'collaboration': [
                r'(?P<person1>[\w\s]+) collaborated with (?P<person2>[\w\s]+)',
                r'(?P<person1>[\w\s]+) worked with (?P<person2>[\w\s]+)',
                r'(?P<person1>[\w\s]+)与(?P<person2>[\w\s]+)合作',
            ],
            'affiliation': [
                r'(?P<person>[\w\s]+) (?:worked at|was at|taught at) (?P<institution>[\w\s]+University|[\w\s]+Institute)',
                r'(?P<person>[\w\s]+)任教于(?P<institution>[\w\s]+大学|[\w\s]+学院)',
            ]
        }
        
        for rel_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    relationships.append({
                        'type': rel_type,
                        **match.groupdict()
                    })
        
        return relationships
    
    def extract_chinese_names(self, text: str) -> List[str]:
        """
        提取中文名字
        
        Args:
            text: 输入文本
            
        Returns:
            中文名字列表
        """
        # 中文名字模式（2-4个汉字）
        chinese_name_pattern = r'[\u4e00-\u9fa5]{2,4}(?:·[\u4e00-\u9fa5]{2,4})?'
        names = re.findall(chinese_name_pattern, text)
        
        # 过滤掉可能不是名字的词
        filtered_names = []
        exclude_words = ['研究', '大学', '教授', '博士', '院士', '先生', '女士']
        
        for name in names:
            if not any(word in name for word in exclude_words):
                filtered_names.append(name)
        
        return list(set(filtered_names))
    
    def extract_years(self, text: str) -> List[int]:
        """
        提取年份
        
        Args:
            text: 输入文本
            
        Returns:
            年份列表
        """
        # 匹配4位数年份（1000-2999）
        year_pattern = r'\b[12]\d{3}\b'
        years = re.findall(year_pattern, text)
        return sorted(list(set(int(y) for y in years)))
    
    def process_scholar_html(self, html_path: str) -> ScholarEntity:
        """
        处理汉学家HTML文件
        
        Args:
            html_path: HTML文件路径
            
        Returns:
            ScholarEntity对象
        """
        if not BS4_AVAILABLE:
            raise ImportError("请先安装BeautifulSoup: pip install beautifulsoup4")
        
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # 提取文本内容
        # 移除script和style标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        
        # 限制文本长度（Transformer模型有长度限制）
        max_length = 5000
        if len(text) > max_length:
            text = text[:max_length]
        
        # 提取实体
        entities = self.extract_entities(text)
        relationships = self.extract_relationships(text)
        chinese_names = self.extract_chinese_names(text)
        years = self.extract_years(text)
        
        # 提取标题作为名字
        title = soup.find('title')
        name = title.text.replace(' - Wikipedia', '').strip() if title else Path(html_path).stem
        
        # 构建ScholarEntity
        scholar = ScholarEntity(
            name=name,
            name_zh=chinese_names[0] if chinese_names else None,
            birth_year=min(years) if years else None,
            death_year=max(years) if years and len(years) > 1 else None,
            institutions=entities.get('organizations', [])[:5],
            research_fields=self._infer_research_fields(text),
            mentors=[r.get('mentor') for r in relationships if r['type'] == 'mentor'],
            collaborators=[r.get('person2') for r in relationships if r['type'] == 'collaboration'],
            major_works=self._extract_works(soup),
            awards=self._extract_awards(text)
        )
        
        return scholar
    
    def _infer_research_fields(self, text: str) -> List[str]:
        """推断研究领域"""
        fields = []
        field_keywords = {
            '历史': ['history', 'historical', '历史', '史学'],
            '哲学': ['philosophy', 'philosophical', '哲学', '思想'],
            '语言学': ['linguistics', 'language', '语言', '文字'],
            '文学': ['literature', 'literary', '文学', '诗词'],
            '宗教': ['religion', 'religious', 'buddhism', '宗教', '佛教', '道教'],
            '艺术': ['art', 'artistic', '艺术', '书法', '绘画'],
            '考古': ['archaeology', 'archaeological', '考古'],
            '人类学': ['anthropology', 'anthropological', '人类学'],
            '社会学': ['sociology', 'social', '社会学'],
            '政治': ['politics', 'political', '政治']
        }
        
        text_lower = text.lower()
        for field, keywords in field_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                fields.append(field)
        
        return fields[:5]  # 最多5个领域
    
    def _extract_works(self, soup: BeautifulSoup) -> List[str]:
        """提取主要著作"""
        works = []
        
        # 查找包含书名的斜体标签
        for italic in soup.find_all('i'):
            text = italic.get_text().strip()
            if len(text) > 5 and len(text) < 200:
                works.append(text)
        
        return list(set(works))[:10]  # 最多10本
    
    def _extract_awards(self, text: str) -> List[str]:
        """提取获奖信息"""
        awards = []
        award_keywords = ['prize', 'award', 'medal', 'honor', 'honour', '奖', '勋章']
        
        sentences = text.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in award_keywords):
                # 简化句子
                sentence = re.sub(r'\[\d+\]', '', sentence).strip()
                if len(sentence) < 200:
                    awards.append(sentence)
        
        return awards[:5]  # 最多5个奖项


class ScholarKnowledgeGraphBuilder:
    """汉学家知识图谱构建器"""
    
    def __init__(self):
        self.ner = TransformerNER()
        self.scholars = []
        self.relationships = []
    
    def process_directory(self, directory: str) -> None:
        """
        处理整个目录的HTML文件
        
        Args:
            directory: 包含HTML文件的目录
        """
        html_files = list(Path(directory).glob("*.html"))
        print(f"找到 {len(html_files)} 个HTML文件")
        
        for idx, html_file in enumerate(html_files[:10], 1):  # 先处理10个作为示例
            try:
                print(f"处理 [{idx}/10]: {html_file.name}")
                scholar = self.ner.process_scholar_html(str(html_file))
                self.scholars.append(asdict(scholar))
            except Exception as e:
                print(f"  错误: {e}")
                continue
    
    def build_graph(self) -> Dict[str, Any]:
        """
        构建知识图谱
        
        Returns:
            图谱数据
        """
        # 构建节点
        nodes = []
        for scholar in self.scholars:
            nodes.append({
                'id': scholar['name'],
                'type': 'scholar',
                'data': scholar
            })
        
        # 构建边（关系）
        edges = []
        for scholar in self.scholars:
            # 导师关系
            if scholar.get('mentors'):
                for mentor in scholar['mentors']:
                    edges.append({
                        'source': mentor,
                        'target': scholar['name'],
                        'type': 'mentor'
                    })
            
            # 合作关系
            if scholar.get('collaborators'):
                for collaborator in scholar['collaborators']:
                    edges.append({
                        'source': scholar['name'],
                        'target': collaborator,
                        'type': 'collaboration'
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_scholars': len(self.scholars),
                'total_relationships': len(edges)
            }
        }
    
    def save_graph(self, output_path: str = "docs/knowledge_graph.json"):
        """保存知识图谱"""
        graph = self.build_graph()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)
        print(f"知识图谱已保存到: {output_path}")


def main():
    """主函数"""
    print("=" * 60)
    print("Transformer NER 汉学家数据提取")
    print("=" * 60)
    
    if not TRANSFORMERS_AVAILABLE:
        print("\n请先安装依赖：")
        print("pip install transformers torch beautifulsoup4")
        return
    
    # 创建知识图谱构建器
    builder = ScholarKnowledgeGraphBuilder()
    
    # 处理HTML文件
    people_dir = "docs/people"
    if os.path.exists(people_dir):
        builder.process_directory(people_dir)
        builder.save_graph()
    else:
        print(f"目录不存在: {people_dir}")
        print("创建示例数据...")
        
        # 创建示例
        example = ScholarEntity(
            name="Joseph Needham",
            name_zh="李约瑟",
            birth_year=1900,
            death_year=1995,
            nationality="British",
            institutions=["Cambridge University"],
            research_fields=["科技史", "生物化学"],
            major_works=["Science and Civilisation in China"]
        )
        
        with open("docs/example_scholar.json", 'w', encoding='utf-8') as f:
            json.dump(asdict(example), f, ensure_ascii=False, indent=2)
        print("示例数据已保存到: docs/example_scholar.json")


if __name__ == "__main__":
    main()