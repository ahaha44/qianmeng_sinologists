#!/bin/bash

# 汉学研究项目 GitHub Pages 部署脚本

echo "🚀 开始部署汉学研究网站到 GitHub Pages..."

# 确保在正确的分支上
git checkout gh-pages

# 复制最新的index.html（如果存在）
if [ -f "../index.html" ]; then
    cp ../index.html .
    echo "✅ 已更新 index.html"
fi

# 添加所有更改
git add .

# 提交更改
git commit -m "更新网站内容 $(date)"

# 推送到GitHub
git push origin gh-pages

echo "✅ 部署完成！"
echo "🌐 您的网站地址：https://ahaha44.github.io/qianmeng_sinologists"
echo "📝 如果网站没有立即更新，请等待几分钟让GitHub Pages重新构建"
