# GitHub Repo Ranker

GitHub Repo Ranker 是一个用于调研和分析 GitHub 开源项目的工具。它可以根据指定的仓库列表或动态搜索条件，获取仓库的详细信息，并将结果导出为美观的 Excel 文件，方便进一步分析。

## 功能特点
- 支持通过关键词动态搜索 GitHub 仓库
- 支持指定仓库列表进行批量分析
- 导出详细的仓库信息到 Excel 文件
- 包含仓库的 stars、forks、issues 等关键指标
- 美观的 Excel 输出格式

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/github_repo_ranker.git
cd github_repo_ranker
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 配置参数
在.env文件中配置以下参数(将配置示例文件[.env.example](.env.example)复制或改名为.env)：
- **GitHub Token**：配置 `GITHUB_TOKEN`，用于访问 GitHub API
  - 获取地址：https://github.com/settings/tokens

在 `github_repo_ranker.py` 中配置以下参数：
- **搜索关键词**：修改 `DEFAULT_SEARCH_QUERY`，设置动态搜索的关键词
- **指定仓库列表**：在 `DEFAULT_SPECIFY_REPO_NAMES` 中添加需要调研的仓库名称
- **输出文件名**：通过 `DEFAULT_OUTPUT_FILE` 配置生成的 Excel 文件名

### 2. 运行工具
```bash
python github_repo_ranker.py
```

### 3. 查看结果
结果将导出为 Excel 文件，默认文件名为 `repo_rank.xlsx`，可以在配置中修改。

## 注意事项
- 确保配置了有效的 GitHub Token
- 如果需要访问更多 GitHub API 数据，请确保 Token 具有相应的权限
- 建议合理控制请求频率，避免触发 GitHub API 限制

## 贡献
欢迎提交 Issue 和 Pull Request 来改进此项目！

## 许可证
MIT License