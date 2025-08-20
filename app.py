#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汉学研究 GraphRAG API 服务
提供基于GraphRAG的智能查询功能
"""

import os
import json
import subprocess
import tempfile
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
GRAPHRAG_ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(GRAPHRAG_ROOT, "cache")
OUTPUT_DIR = os.path.join(GRAPHRAG_ROOT, "output")

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def query():
    """处理GraphRAG查询"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        method = data.get('method', 'global')  # global 或 local
        
        if not question:
            return jsonify({'error': '请提供查询问题'}), 400
        
        logger.info(f"收到查询: {question} (方法: {method})")
        
        # 检查是否已经构建了知识图谱
        if not os.path.exists(OUTPUT_DIR):
            return jsonify({
                'error': '知识图谱尚未构建，请先运行构建命令',
                'suggestion': '请在服务器上运行: python -m graphrag.index --root .'
            }), 503
        
        # 执行GraphRAG查询
        result = execute_graphrag_query(question, method)
        
        return jsonify({
            'success': True,
            'question': question,
            'method': method,
            'answer': result
        })
        
    except Exception as e:
        logger.error(f"查询出错: {str(e)}")
        return jsonify({'error': f'查询失败: {str(e)}'}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """检查服务状态"""
    try:
        # 检查GraphRAG是否可用
        graphrag_available = check_graphrag_availability()
        
        # 检查知识图谱是否已构建
        knowledge_graph_built = os.path.exists(OUTPUT_DIR)
        
        return jsonify({
            'service': 'running',
            'graphrag_available': graphrag_available,
            'knowledge_graph_built': knowledge_graph_built,
            'input_files_count': count_input_files()
        })
        
    except Exception as e:
        logger.error(f"状态检查出错: {str(e)}")
        return jsonify({'error': f'状态检查失败: {str(e)}'}), 500

@app.route('/api/build', methods=['POST'])
def build_knowledge_graph():
    """构建知识图谱"""
    try:
        logger.info("开始构建知识图谱...")
        
        # 执行构建命令
        result = execute_graphrag_build()
        
        return jsonify({
            'success': True,
            'message': '知识图谱构建完成',
            'details': result
        })
        
    except Exception as e:
        logger.error(f"构建知识图谱出错: {str(e)}")
        return jsonify({'error': f'构建失败: {str(e)}'}), 500

def execute_graphrag_query(question, method):
    """执行GraphRAG查询"""
    try:
        # 创建临时文件存储查询
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(question)
            temp_file = f.name
        
        # 构建命令
        cmd = [
            'python', '-m', 'graphrag.query',
            '--root', GRAPHRAG_ROOT,
            '--method', method,
            '--query', question
        ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=GRAPHRAG_ROOT,
            timeout=300  # 5分钟超时
        )
        
        # 清理临时文件
        os.unlink(temp_file)
        
        if result.returncode != 0:
            raise Exception(f"GraphRAG查询失败: {result.stderr}")
        
        return result.stdout.strip()
        
    except subprocess.TimeoutExpired:
        raise Exception("查询超时，请稍后重试")
    except Exception as e:
        raise Exception(f"执行查询时出错: {str(e)}")

def execute_graphrag_build():
    """执行GraphRAG构建"""
    try:
        cmd = ['python', '-m', 'graphrag.index', '--root', GRAPHRAG_ROOT]
        
        logger.info(f"执行构建命令: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=GRAPHRAG_ROOT,
            timeout=3600  # 1小时超时
        )
        
        if result.returncode != 0:
            raise Exception(f"构建失败: {result.stderr}")
        
        return result.stdout.strip()
        
    except subprocess.TimeoutExpired:
        raise Exception("构建超时")
    except Exception as e:
        raise Exception(f"构建时出错: {str(e)}")

def check_graphrag_availability():
    """检查GraphRAG是否可用"""
    try:
        result = subprocess.run(
            ['python', '-m', 'graphrag', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

def count_input_files():
    """统计输入文件数量"""
    input_dir = os.path.join(GRAPHRAG_ROOT, "input")
    if not os.path.exists(input_dir):
        return 0
    
    count = 0
    for file in os.listdir(input_dir):
        if file.endswith('.txt'):
            count += 1
    return count

if __name__ == '__main__':
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    print("🚀 启动汉学研究 GraphRAG API 服务...")
    print(f"📁 项目根目录: {GRAPHRAG_ROOT}")
    print(f"📊 输入文件数量: {count_input_files()}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
