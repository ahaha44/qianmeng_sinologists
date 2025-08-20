# GraphRAG 使用指南（小白友好版）

## 🌟 什么是 GraphRAG？

GraphRAG 是微软开发的一个强大工具，它能把大量文本资料转换成知识图谱，让 AI 更好地理解和回答复杂问题。想象一下，它就像是把一堆散乱的笔记整理成一张清晰的思维导图。

## 📝 准备工作

### 1. 获取 API 密钥

你需要两个 API 密钥：

#### DeepSeek API（主要模型）
1. 访问 [DeepSeek 官网](https://platform.deepseek.com/)
2. 注册/登录账号
3. 进入 [API Keys 页面](https://platform.deepseek.com/api_keys)
4. 点击"创建 API Key"
5. 复制生成的密钥（注意：只显示一次，请妥善保存）

#### OpenAI API（嵌入模型）
1. 访问 [OpenAI 平台](https://platform.openai.com/)
2. 注册/登录账号
3. 进入 [API Keys 页面](https://platform.openai.com/api-keys)
4. 点击"Create new secret key"
5. 复制生成的密钥

### 2. 安装 Python 和 GraphRAG

#### Windows 用户：
1. 从 [Python 官网](https://www.python.org/downloads/) 下载 Python（选择 3.10 或更高版本）
2. 安装时勾选"Add Python to PATH"
3. 打开命令提示符（Win+R，输入 cmd）
4. 输入以下命令安装 GraphRAG：
```bash
pip install graphrag
```

#### Mac 用户：
1. 打开终端（在 Launchpad 中找到"终端"）
2. 安装 Homebrew（如果没有）：
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
3. 安装 Python：
```bash
brew install python3
```
4. 安装 GraphRAG：
```bash
pip3 install graphrag
```

## 🚀 快速开始

### 第一步：配置 API 密钥

1. 在项目根目录找到 `.env.example` 文件
2. 复制并重命名为 `.env`
3. 用记事本或任何文本编辑器打开 `.env`
4. 替换其中的密钥：
```env
GRAPHRAG_API_KEY=你的DeepSeek密钥
GRAPHRAG_EMBEDDING_API_KEY=你的OpenAI密钥
```
5. 保存文件

### 第二步：准备数据

1. 在项目根目录创建 `input` 文件夹
2. 把你要分析的文本文件（.txt 格式）放入 `input` 文件夹
   - 例如：汉学家的传记、研究论文等
   - 文件名建议用英文或拼音，避免中文乱码

### 第三步：运行 GraphRAG

1. 打开终端/命令提示符
2. 进入项目目录：
```bash
cd /你的项目路径/qianmeng_sinologists
```

3. 初始化 GraphRAG（第一次使用需要）：
```bash
python -m graphrag.index --init
```

4. 构建知识图谱：
```bash
python -m graphrag.index --root .
```
这个过程可能需要几分钟到几小时，取决于数据量大小。

### 第四步：查询知识图谱

构建完成后，你可以查询知识图谱：

```bash
python -m graphrag.query --root . --method global "你的问题"
```

例如：
```bash
python -m graphrag.query --root . --method global "汉学家之间有什么联系？"
```

## 💡 使用技巧

### 查询方法说明

GraphRAG 提供两种查询方法：

1. **全局查询（global）**：适合宏观问题
   ```bash
   python -m graphrag.query --root . --method global "汉学研究的主要流派有哪些？"
   ```

2. **局部查询（local）**：适合具体细节
   ```bash
   python -m graphrag.query --root . --method local "费正清的主要研究成果是什么？"
   ```

### 数据准备建议

1. **文本格式**：使用纯文本（.txt）格式
2. **编码**：确保文件是 UTF-8 编码
3. **文件大小**：单个文件不要超过 10MB
4. **内容结构**：最好有清晰的段落划分

## 📊 查看结果

运行完成后，结果保存在 `output` 文件夹中：
- `artifacts/`：知识图谱数据
- `reports/`：处理报告
- 可以用 Excel 打开 `.parquet` 文件查看提取的实体和关系

## ❓ 常见问题

### Q1: API 调用失败怎么办？
**A**: 检查以下几点：
- API 密钥是否正确
- 账户是否有余额
- 网络连接是否正常
- 如果在中国大陆，可能需要配置代理

### Q2: 处理速度太慢？
**A**: 可以调整 `settings.yaml` 中的参数：
- 减少 `chunks.size`（如改为 800）
- 增加 `llm.concurrent_requests`（如改为 50）

### Q3: 费用如何？
**A**: 
- DeepSeek：约 ¥1/百万 tokens（非常便宜）
- OpenAI 嵌入：约 $0.02/百万 tokens
- 处理 100 页文档大约花费 ¥5-10

### Q4: 如何完全使用 DeepSeek（不用 OpenAI）？
**A**: 修改 `settings.yaml` 中的嵌入配置：
```yaml
embeddings:
  llm:
    api_key: ${GRAPHRAG_API_KEY}  # 使用同一个 DeepSeek 密钥
    type: openai_embedding
    model: deepseek-chat  # 改为 DeepSeek 模型
    api_base: https://api.deepseek.com/v1  # DeepSeek API
```

## 🆘 需要帮助？

如果遇到问题：
1. 查看错误信息，通常会有明确提示
2. 检查 `output/*/reports/` 中的日志文件
3. 在项目的 GitHub Issues 中搜索类似问题
4. 询问 AI 助手（如 Claude、ChatGPT）

## 📚 进阶学习

- [GraphRAG 官方文档](https://microsoft.github.io/graphrag/)
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs)
- [知识图谱基础概念](https://en.wikipedia.org/wiki/Knowledge_graph)

---

💡 **小贴士**：第一次使用建议先用少量数据（1-2个小文件）测试，确保配置正确后再处理大量数据。

祝你使用愉快！如有疑问，欢迎随时询问。