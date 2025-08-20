#!/usr/bin/env python3
"""
生成示例知识图谱数据
不依赖transformer，使用简单的规则提取关键信息
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any

def extract_name_from_filename(filename: str) -> str:
    """从文件名提取人名"""
    name = Path(filename).stem
    # 替换下划线为空格
    name = name.replace('_', ' ')
    # 移除括号内容
    name = re.sub(r'\s*\([^)]*\)', '', name)
    return name.strip()

def extract_basic_info(html_content: str) -> Dict[str, Any]:
    """从HTML中提取基本信息"""
    info = {
        'birth_year': None,
        'death_year': None,
        'nationality': None,
        'field': None
    }
    
    # 提取年份 (出生/去世年)
    years = re.findall(r'\b(1[5-9]\d{2}|20[0-2]\d)\b', html_content)
    if years:
        years = sorted([int(y) for y in years])
        if len(years) >= 1:
            info['birth_year'] = years[0]
        if len(years) >= 2:
            info['death_year'] = years[-1] if years[-1] > years[0] else None
    
    # 提取国籍关键词
    nationalities = {
        'American': '美国',
        'British': '英国', 
        'French': '法国',
        'German': '德国',
        'Russian': '俄罗斯',
        'Japanese': '日本',
        'Italian': '意大利',
        'Dutch': '荷兰',
        'Canadian': '加拿大',
        'Australian': '澳大利亚'
    }
    
    for eng, chi in nationalities.items():
        if eng.lower() in html_content.lower():
            info['nationality'] = chi
            break
    
    # 提取研究领域
    fields = {
        'history': '历史',
        'philosophy': '哲学',
        'linguistics': '语言学',
        'literature': '文学',
        'archaeology': '考古学',
        'religion': '宗教',
        'art': '艺术',
        'anthropology': '人类学'
    }
    
    for eng, chi in fields.items():
        if eng in html_content.lower():
            info['field'] = chi
            break
    
    return info

def generate_sample_knowledge_graph():
    """生成示例知识图谱"""
    
    people_dir = Path('docs/people')
    
    if not people_dir.exists():
        print(f"目录不存在: {people_dir}")
        return None
    
    # 获取前30个HTML文件作为示例
    html_files = list(people_dir.glob('*.html'))[:30]
    
    nodes = []
    edges = []
    
    print(f"处理 {len(html_files)} 个文件...")
    
    for html_file in html_files:
        try:
            # 读取HTML内容
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 提取名字
            name = extract_name_from_filename(html_file.name)
            
            # 提取基本信息
            info = extract_basic_info(content)
            
            # 创建节点
            node = {
                'id': name,
                'name': name,
                'type': 'scholar',
                'birth_year': info['birth_year'],
                'death_year': info['death_year'],
                'nationality': info['nationality'],
                'field': info['field'],
                'file': f'people/{html_file.name}'
            }
            
            nodes.append(node)
            
        except Exception as e:
            print(f"处理 {html_file.name} 时出错: {e}")
            continue
    
    # 创建一些示例关系
    # 基于时间重叠创建可能的合作关系
    for i, node1 in enumerate(nodes):
        for node2 in nodes[i+1:]:
            if node1['birth_year'] and node2['birth_year']:
                # 如果两人生活时期有重叠
                overlap = False
                if node1['death_year'] and node2['death_year']:
                    overlap = not (node1['death_year'] < node2['birth_year'] or 
                                 node2['death_year'] < node1['birth_year'])
                elif node1['death_year']:
                    overlap = node1['death_year'] > node2['birth_year']
                elif node2['death_year']:
                    overlap = node2['death_year'] > node1['birth_year']
                else:
                    # 都还在世，年龄差小于50年
                    overlap = abs(node1['birth_year'] - node2['birth_year']) < 50
                
                # 如果时期重叠且研究领域相同，创建潜在合作关系
                if overlap and node1['field'] == node2['field'] and node1['field']:
                    edges.append({
                        'source': node1['id'],
                        'target': node2['id'],
                        'type': 'potential_collaboration',
                        'field': node1['field']
                    })
    
    # 构建知识图谱数据
    knowledge_graph = {
        'nodes': nodes,
        'edges': edges[:20],  # 限制边的数量，避免过于复杂
        'metadata': {
            'total_scholars': len(nodes),
            'total_relationships': len(edges[:20]),
            'fields': list(set(n['field'] for n in nodes if n['field'])),
            'nationalities': list(set(n['nationality'] for n in nodes if n['nationality']))
        }
    }
    
    return knowledge_graph

def main():
    """主函数"""
    print("生成示例知识图谱数据...")
    
    graph = generate_sample_knowledge_graph()
    
    if graph:
        output_path = 'docs/knowledge_graph.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)
        
        print(f"知识图谱已保存到: {output_path}")
        print(f"- 学者节点: {graph['metadata']['total_scholars']}")
        print(f"- 关系边: {graph['metadata']['total_relationships']}")
        print(f"- 研究领域: {', '.join(graph['metadata']['fields'])}")
        print(f"- 国籍: {', '.join(graph['metadata']['nationalities'])}")
    else:
        print("生成失败")

if __name__ == "__main__":
    main()