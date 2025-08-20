# 汉学研究 GraphRAG 智能查询系统

## 🌟 项目简介

这是一个基于 Microsoft GraphRAG 技术的汉学研究智能查询系统，收录了数百位著名汉学家的详细资料。通过先进的知识图谱技术，系统能够深度理解汉学家之间的关系、研究成果和学术贡献。

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装：
- Python 3.9+
- Git

### 2. 克隆项目

```bash
git clone https://github.com/ahaha44/qianmeng_sinologists.git
cd qianmeng_sinologists
```

### 3. 配置API密钥

复制环境变量模板并填入您的API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的API密钥：

```env
# DeepSeek API (主要模型)
GRAPHRAG_API_KEY=your_deepseek_api_key_here

# OpenAI API (嵌入模型)
GRAPHRAG_EMBEDDING_API_KEY=your_openai_api_key_here
```

### 4. 启动服务器

使用提供的启动脚本：

```bash
./start_server.sh
```

或者手动启动：

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 GraphRAG
pip install git+https://github.com/microsoft/graphrag.git

# 启动服务器
python3 app.py
```

### 5. 访问系统

打开浏览器访问：http://localhost:5000

## 📊 系统功能

### 🤖 智能查询
- **全局查询**：宏观分析汉学研究趋势和学者关系
- **局部查询**：深入了解具体学者的研究成果
- **实时响应**：基于GraphRAG技术提供智能回答

### 📚 数据内容
- 282位著名汉学家详细资料
- 涵盖各个研究领域和时期
- 包含学术贡献、研究领域、重要著作等信息

### 🎯 示例问题
- "费正清的主要研究成果是什么？"
- "汉学家之间有什么联系？"
- "哪些汉学家研究中国古代文学？"
- "20世纪汉学研究的主要趋势是什么？"

## 🏗️ 系统架构

### 后端 (Flask API)
- `app.py` - 主服务器文件
- 提供 RESTful API 接口
- 集成 GraphRAG 查询功能
- 支持知识图谱构建

### 前端 (HTML + JavaScript)
- `templates/index.html` - 用户界面
- 响应式设计，支持移动端
- 实时查询结果显示
- 系统状态监控

### 数据处理
- `input/` - 汉学家数据文件
- `output/` - GraphRAG 输出结果
- `cache/` - 缓存文件

## 🔧 API 接口

### 查询接口
```http
POST /api/query
Content-Type: application/json

{
    "question": "您的问题",
    "method": "global"  // 或 "local"
}
```

### 状态检查
```http
GET /api/status
```

### 构建知识图谱
```http
POST /api/build
```

## 📁 项目结构

```
qianmeng_sinologists/
├── app.py                 # Flask 主服务器
├── settings.yaml          # GraphRAG 配置
├── requirements.txt       # Python 依赖
├── .env                   # 环境变量 (需要创建)
├── .env.example          # 环境变量模板
├── start_server.sh       # 启动脚本
├── deploy.sh             # 部署脚本
├── templates/
│   └── index.html        # 网页模板
├── input/                # 汉学家数据文件
│   ├── 费正清.txt
│   ├── 李约瑟.txt
│   └── ...
├── output/               # GraphRAG 输出
├── cache/                # 缓存文件
└── docs/                 # 文档
```

## 🎯 使用流程

### 首次使用
1. 配置API密钥
2. 启动服务器
3. 构建知识图谱（首次需要）
4. 开始查询

### 日常使用
1. 启动服务器
2. 访问网页界面
3. 输入问题并选择查询方法
4. 查看智能回答

## 🔍 查询方法说明

### 全局查询 (Global)
- 适合宏观问题
- 分析整体趋势和关系
- 处理时间较长
- 示例：汉学研究的主要流派有哪些？

### 局部查询 (Local)
- 适合具体细节
- 快速获取特定信息
- 处理时间较短
- 示例：费正清的主要研究成果是什么？

## 🛠️ 故障排除

### 常见问题

1. **API密钥错误**
   - 检查 `.env` 文件中的密钥是否正确
   - 确认账户有足够余额

2. **GraphRAG安装失败**
   ```bash
   pip install --upgrade pip
   pip install git+https://github.com/microsoft/graphrag.git
   ```

3. **知识图谱构建失败**
   - 检查输入文件格式
   - 确认API密钥有效
   - 查看错误日志

4. **查询超时**
   - 尝试使用局部查询方法
   - 简化问题描述
   - 检查网络连接

### 日志查看
```bash
# 查看Flask日志
tail -f app.log

# 查看GraphRAG输出
ls output/*/reports/
```

## 📈 性能优化

### 系统配置
- 调整 `settings.yaml` 中的参数
- 增加并发请求数
- 优化缓存设置

### 查询优化
- 使用更具体的问题
- 选择合适的查询方法
- 避免过于复杂的问题

## 🔒 安全注意事项

1. **API密钥保护**
   - 不要将 `.env` 文件提交到Git
   - 定期更换API密钥
   - 使用环境变量管理密钥

2. **网络安全**
   - 生产环境使用HTTPS
   - 配置防火墙规则
   - 限制API访问频率

## 📞 技术支持

如果遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查项目GitHub Issues
3. 查看GraphRAG官方文档
4. 联系技术支持

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 🙏 致谢

- Microsoft GraphRAG 团队
- DeepSeek AI 团队
- 所有为汉学研究做出贡献的学者

---

**祝您使用愉快！** 🎉
