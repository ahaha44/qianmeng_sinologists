# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

qianmeng_sinologists 是一个汉学家资料库项目，提供汉学研究者的网页索引和信息展示。项目使用静态网站架构，包含汉学家个人页面、搜索功能和信息展示界面。

## 项目架构

### 目录结构
```
qianmeng_sinologists/
├── docs/                    # 网站主目录
│   ├── index.html          # 主页（汉学研究介绍页）
│   ├── people.html         # 汉学家列表页
│   ├── manifest.json       # 汉学家数据索引文件
│   ├── people/             # 汉学家个人页面（300+ HTML文件）
│   └── assets/             # 静态资源
│       ├── style.css       # 样式文件
│       ├── app.js          # 应用脚本
│       └── images/         # 图片资源
└── scripts/                # 构建脚本
    ├── build_manifest.py   # 生成manifest.json的脚本
    └── fix_wiki_paths.py   # 修复Wikipedia路径的脚本
```

### 技术栈
- **前端**: 纯HTML + Tailwind CSS + 原生JavaScript
- **数据处理**: Python脚本（BeautifulSoup用于HTML解析）
- **样式框架**: Tailwind CSS（通过CDN引入）
- **无需构建工具**: 静态网站，直接在浏览器中运行

## 常用命令

### 生成汉学家索引文件
```bash
python scripts/build_manifest.py docs/people docs/manifest.json
```

### 本地预览网站
```bash
# 使用Python内置服务器
cd docs && python -m http.server 8000

# 或使用Node.js的http-server（如果已安装）
npx http-server docs -p 8000
```

### 修复Wikipedia链接路径
```bash
python scripts/fix_wiki_paths.py
```

## 核心功能实现

### 汉学家搜索系统
- **数据源**: `docs/manifest.json` 包含所有汉学家的姓名和文件映射
- **搜索实现**: 前端JavaScript实时过滤，支持按字母筛选和模糊搜索
- **页面入口**: 
  - `docs/index.html#people` - 主页嵌入式搜索
  - `docs/people.html` - 完整搜索页面

### 数据更新流程
1. 将新的汉学家HTML文件添加到 `docs/people/` 目录
2. 运行 `build_manifest.py` 重新生成索引
3. 无需其他构建步骤，刷新页面即可看到更新

## 开发原则

1. **静态优先**: 保持纯静态架构，避免引入服务端依赖
2. **性能考虑**: 使用懒加载和分页限制（每次最多显示30条记录）
3. **代码简洁**: 使用原生JavaScript，避免框架依赖
4. **响应式设计**: 使用Tailwind的响应式类确保移动端体验
5. **渐进增强**: 核心功能不依赖JavaScript（汉学家页面可直接访问）

## 注意事项

- 修改汉学家数据后必须重新运行 `build_manifest.py`
- 所有汉学家页面文件名应遵循Wikipedia格式（空格用下划线替代）
- 保持 `manifest.json` 的JSON格式正确，避免破坏搜索功能
- 图片资源放在 `docs/assets/images/` 目录下
- 代码注释使用中文，便于理解和维护