#!/bin/bash

# 汉学研究 GraphRAG 服务器启动脚本

echo "🚀 启动汉学研究 GraphRAG 服务器..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements.txt

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "⚠️  警告: 未找到 .env 文件，请确保已配置API密钥"
    echo "📝 请复制 .env.example 为 .env 并填入您的API密钥"
fi

# 检查GraphRAG是否安装
echo "🔍 检查 GraphRAG 安装..."
python3 -c "import graphrag" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 安装 GraphRAG..."
    pip install git+https://github.com/microsoft/graphrag.git
fi

# 创建必要的目录
mkdir -p output cache

echo "✅ 环境准备完成！"
echo "🌐 启动 Flask 服务器..."
echo "📱 访问地址: http://localhost:5000"
echo "🔧 API 地址: http://localhost:5000/api"
echo ""
echo "按 Ctrl+C 停止服务器"

# 启动Flask服务器
python3 app.py
