# GitHub Trending Report

自动化技术趋势报告项目，使用Python开发，通过爬取GitHub Trending数据，结合AI技术生成专业的技术分析文章，并支持多渠道发布。

## 主要功能

1. **数据爬取模块**：
   - 从GitHub Trending获取热门项目数据
   - 支持按语言、时间范围筛选
   - 自动保存原始数据到本地

2. **文章生成模块**：
   - 使用LangChain和DeepSeek生成专业文章
   - 支持多种文章风格（技术分析、新闻简报、教程等）
   - 可自定义文章模板

3. **发布模块**：
   - 支持微信公众号发布
   - 支持Confluence知识库同步
   - 可扩展其他发布渠道

## 技术栈
- Python 3.10+
- LangChain
- DeepSeek API
- Requests
- BeautifulSoup

## 项目结构

```
github_trending_report/
├── README.md
├── requirements.txt
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── prompts.py
├── src/
│   ├── crawler/
│   │   ├── __init__.py
│   │   └── github_trending.py
│   ├── generator/
│   │   ├── __init__.py
│   │   └── article_generator.py
│   └── publisher/
│       ├── __init__.py
│       ├── wechat.py
│       └── confluence.py
└── main.py
```

## 安装

1. 克隆项目
```bash
git clone https://github.com/yourusername/github_trending_report.git
cd github_trending_report
```

2. 创建虚拟环境并安装依赖
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

3. 配置环境变量
复制`.env.example`为`.env`并填写必要的API密钥和配置

## 使用

### 基本使用
```bash
python main.py
```

### 可选参数
```bash
python main.py --language python --since weekly --output_format markdown
```

### 配置说明
编辑`config/settings.py`文件可修改以下配置：
- GitHub Trending爬取参数
- 文章生成参数
- 发布渠道配置

## 贡献
欢迎提交Pull Request或报告Issue。

## 许可证
MIT