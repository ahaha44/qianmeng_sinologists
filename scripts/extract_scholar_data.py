#!/usr/bin/env python3
"""
汉学家数据提取脚本
从Wikipedia HTML文件中提取结构化信息
"""

import os
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from datetime import datetime


class ScholarDataExtractor:
    """汉学家数据提取器"""
    
    def __init__(self, people_dir: str = "docs/people"):
        self.people_dir = Path(people_dir)
        self.scholars_data = []
        
    def extract_all(self) -> List[Dict[str, Any]]:
        """提取所有汉学家数据"""
        html_files = list(self.people_dir.glob("*.html"))
        print(f"发现 {len(html_files)} 个HTML文件")
        
        for idx, html_file in enumerate(html_files, 1):
            try:
                print(f"处理 [{idx}/{len(html_files)}]: {html_file.name}")
                scholar_data = self.extract_scholar(html_file)
                if scholar_data:
                    self.scholars_data.append(scholar_data)
            except Exception as e:
                print(f"  错误: {e}")
                continue
                
        return self.scholars_data
    
    def extract_scholar(self, html_path: Path) -> Optional[Dict[str, Any]]:
        """从单个HTML文件提取汉学家信息"""
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # 基础信息
        data = {
            'id': html_path.stem,
            'file': html_path.name,
            'name': self._extract_name(soup),
            'name_zh': None,  # 中文名
            'birth_death': self._extract_birth_death(soup),
            'nationality': self._extract_nationality(soup),
            'fields': self._extract_fields(soup),
            'institutions': self._extract_institutions(soup),
            'education': self._extract_education(soup),
            'abstract': self._extract_abstract(soup),
            'infobox': self._extract_infobox(soup),
            'categories': self._extract_categories(soup),
            'external_links': self._extract_external_links(soup)
        }
        
        # 清理空值
        data = {k: v for k, v in data.items() if v}
        return data
    
    def _extract_name(self, soup: BeautifulSoup) -> str:
        """提取姓名"""
        # 优先从标题提取
        title = soup.find('title')
        if title:
            name = title.text.replace(' - Wikipedia', '').strip()
            return name
            
        # 从h1标题提取
        h1 = soup.find('h1', class_='firstHeading')
        if h1:
            return h1.text.strip()
            
        return ""
    
    def _extract_birth_death(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """提取生卒年份"""
        # 查找包含生卒年的常见模式
        patterns = [
            r'\b(\d{4})\s*[-–—]\s*(\d{4})\b',  # 1900-1995
            r'\b(?:born|b\.)\s*(\d{4})\b',      # born 1900
            r'\b(\d{4})\s*[-–—]\s*\)',          # 1900-)
        ]
        
        # 首先检查infobox
        infobox = soup.find('table', class_='infobox')
        if infobox:
            text = infobox.get_text()
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    if len(match.groups()) == 2:
                        return {
                            'birth': int(match.group(1)),
                            'death': int(match.group(2))
                        }
                    elif len(match.groups()) == 1:
                        return {'birth': int(match.group(1))}
        
        # 检查第一段
        first_p = soup.find('p', class_=None)
        if first_p:
            text = first_p.get_text()
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    if len(match.groups()) == 2:
                        return {
                            'birth': int(match.group(1)),
                            'death': int(match.group(2))
                        }
                    elif len(match.groups()) == 1:
                        return {'birth': int(match.group(1))}
        
        return None
    
    def _extract_nationality(self, soup: BeautifulSoup) -> Optional[str]:
        """提取国籍"""
        # 从分类中提取
        categories = self._extract_categories(soup)
        for cat in categories:
            # 常见国籍模式
            if 'British' in cat:
                return 'British'
            elif 'American' in cat:
                return 'American'
            elif 'French' in cat:
                return 'French'
            elif 'German' in cat:
                return 'German'
            elif 'Chinese' in cat:
                return 'Chinese'
            elif 'Japanese' in cat:
                return 'Japanese'
        
        return None
    
    def _extract_fields(self, soup: BeautifulSoup) -> List[str]:
        """提取研究领域"""
        fields = []
        
        # 从分类提取
        categories = self._extract_categories(soup)
        field_keywords = [
            'historian', 'linguist', 'philosopher', 'translator',
            'archaeologist', 'anthropologist', 'scholar', 'sinologist'
        ]
        
        for cat in categories:
            cat_lower = cat.lower()
            for keyword in field_keywords:
                if keyword in cat_lower:
                    fields.append(cat)
                    break
        
        return list(set(fields))[:10]  # 限制最多10个领域
    
    def _extract_institutions(self, soup: BeautifulSoup) -> List[str]:
        """提取所属机构"""
        institutions = []
        
        # 查找包含大学名称的链接
        university_keywords = [
            'University', 'College', 'Institute', 'Academy',
            'School', '大学', '学院'
        ]
        
        links = soup.find_all('a')
        for link in links:
            text = link.get_text().strip()
            for keyword in university_keywords:
                if keyword in text and len(text) < 100:
                    institutions.append(text)
                    break
        
        # 去重并限制数量
        return list(set(institutions))[:5]
    
    def _extract_education(self, soup: BeautifulSoup) -> List[str]:
        """提取教育背景"""
        education = []
        
        # 查找Education部分
        education_header = soup.find(['h2', 'h3'], string=re.compile(r'Education|Academic'))
        if education_header:
            # 获取下一个兄弟元素直到下一个标题
            next_sibling = education_header.find_next_sibling()
            while next_sibling and next_sibling.name not in ['h2', 'h3']:
                if next_sibling.name == 'p' or next_sibling.name == 'ul':
                    education.append(next_sibling.get_text().strip())
                next_sibling = next_sibling.find_next_sibling()
        
        return education[:3]  # 限制最多3条
    
    def _extract_abstract(self, soup: BeautifulSoup) -> str:
        """提取摘要（第一段）"""
        # 查找第一个非空段落
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            # 跳过太短的段落和坐标段落
            if len(text) > 100 and not text.startswith('Coordinates'):
                # 清理文本
                text = re.sub(r'\[\d+\]', '', text)  # 移除引用标记
                text = re.sub(r'\s+', ' ', text)     # 规范化空白
                return text[:500]  # 限制长度
        
        return ""
    
    def _extract_infobox(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """提取信息框数据"""
        infobox = soup.find('table', class_='infobox')
        if not infobox:
            return None
        
        data = {}
        rows = infobox.find_all('tr')
        
        for row in rows:
            # 查找标签和值
            label = row.find('th')
            value = row.find('td')
            
            if label and value:
                label_text = label.get_text().strip()
                value_text = value.get_text().strip()
                
                # 清理文本
                label_text = re.sub(r'\s+', ' ', label_text)
                value_text = re.sub(r'\s+', ' ', value_text)
                value_text = re.sub(r'\[\d+\]', '', value_text)
                
                if label_text and value_text:
                    data[label_text] = value_text[:200]  # 限制值的长度
        
        return data if data else None
    
    def _extract_categories(self, soup: BeautifulSoup) -> List[str]:
        """提取Wikipedia分类"""
        categories = []
        
        # 方法1: 从页面底部的分类链接提取
        cat_links = soup.find_all('a', href=re.compile(r'/wiki/Category:'))
        for link in cat_links:
            cat_name = link.get_text().strip()
            if cat_name and not cat_name.startswith('Category:'):
                categories.append(cat_name)
        
        # 方法2: 从隐藏的分类div提取
        cat_div = soup.find('div', id='mw-normal-catlinks')
        if cat_div:
            cat_list = cat_div.find('ul')
            if cat_list:
                for li in cat_list.find_all('li'):
                    categories.append(li.get_text().strip())
        
        return list(set(categories))
    
    def _extract_external_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """提取外部链接"""
        links = []
        
        # 查找External links部分
        ext_header = soup.find(['h2', 'h3'], string=re.compile(r'External links|References'))
        if ext_header:
            next_sibling = ext_header.find_next_sibling()
            while next_sibling and next_sibling.name not in ['h2', 'h3']:
                if next_sibling.name == 'ul':
                    for li in next_sibling.find_all('li'):
                        a = li.find('a', href=True)
                        if a and not a['href'].startswith('/wiki/'):
                            links.append({
                                'text': a.get_text().strip(),
                                'url': a['href']
                            })
                next_sibling = next_sibling.find_next_sibling()
        
        return links[:5]  # 限制最多5个链接
    
    def save_to_json(self, output_path: str = "docs/scholars_enriched.json"):
        """保存提取的数据到JSON文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.scholars_data, f, ensure_ascii=False, indent=2)
        print(f"\n数据已保存到 {output_path}")
        print(f"总共提取了 {len(self.scholars_data)} 位汉学家的数据")
    
    def generate_statistics(self) -> Dict[str, Any]:
        """生成统计信息"""
        stats = {
            'total_scholars': len(self.scholars_data),
            'with_birth_death': 0,
            'with_nationality': 0,
            'with_fields': 0,
            'with_institutions': 0,
            'with_infobox': 0,
            'nationalities': {},
            'birth_years': [],
            'research_fields': {}
        }
        
        for scholar in self.scholars_data:
            if 'birth_death' in scholar:
                stats['with_birth_death'] += 1
                if 'birth' in scholar['birth_death']:
                    stats['birth_years'].append(scholar['birth_death']['birth'])
            
            if 'nationality' in scholar:
                stats['with_nationality'] += 1
                nat = scholar['nationality']
                stats['nationalities'][nat] = stats['nationalities'].get(nat, 0) + 1
            
            if 'fields' in scholar and scholar['fields']:
                stats['with_fields'] += 1
                for field in scholar['fields']:
                    stats['research_fields'][field] = stats['research_fields'].get(field, 0) + 1
            
            if 'institutions' in scholar and scholar['institutions']:
                stats['with_institutions'] += 1
            
            if 'infobox' in scholar:
                stats['with_infobox'] += 1
        
        return stats


def main():
    """主函数"""
    print("=" * 60)
    print("汉学家数据提取工具")
    print("=" * 60)
    
    # 创建提取器
    extractor = ScholarDataExtractor()
    
    # 提取所有数据
    scholars = extractor.extract_all()
    
    # 保存数据
    extractor.save_to_json()
    
    # 生成统计
    stats = extractor.generate_statistics()
    
    print("\n" + "=" * 60)
    print("统计信息")
    print("=" * 60)
    print(f"总人数: {stats['total_scholars']}")
    print(f"包含生卒年: {stats['with_birth_death']}")
    print(f"包含国籍: {stats['with_nationality']}")
    print(f"包含研究领域: {stats['with_fields']}")
    print(f"包含机构信息: {stats['with_institutions']}")
    print(f"包含信息框: {stats['with_infobox']}")
    
    if stats['nationalities']:
        print("\n国籍分布:")
        for nat, count in sorted(stats['nationalities'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {nat}: {count}")
    
    if stats['birth_years']:
        print(f"\n出生年份范围: {min(stats['birth_years'])} - {max(stats['birth_years'])}")
    
    if stats['research_fields']:
        print("\n热门研究领域:")
        for field, count in sorted(stats['research_fields'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {field}: {count}")


if __name__ == "__main__":
    main()