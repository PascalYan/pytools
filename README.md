# pytools

## 简介
pytools 是一个集合了多种实用工具的项目，旨在为开发者提供便捷的工具集。目前包含以下工具：

### 1. GitHub Repo Ranker
GitHub Repo Ranker 是一个用于调研和分析 GitHub 开源项目的工具。它可以根据指定的仓库列表或动态搜索条件，获取仓库的详细信息，并将结果导出为美观的 Excel 文件，方便进一步分析。

## 工具列表
- `github_repo_ranker/`：GitHub Repo Ranker 工具。

## 使用方法

### 1. 安装依赖
每个工具有独立的依赖管理，请进入对应工具的文件夹并安装依赖。例如：
```bash
cd github_repo_ranker
pip install -r requirements.txt
```

### 2. 配置参数
在工具文件夹中找到主脚本文件（如 `github_repo_ranker.py`），根据需要修改配置参数。

- **GitHub Token**：在代码中配置 `GITHUB_TOKEN`，以便访问 GitHub API，获取地址：https://github.com/settings/tokens。
    - **搜索关键词**：修改 `DEFAULT_SEARCH_QUERY`，设置动态搜索的关键词。
- **指定仓库列表**：在 `DEFAULT_SPECIFY_REPO_NAMES` 中添加需要调研的仓库名称。
- **输出文件名**：通过 `DEFAULT_OUTPUT_FILE` 配置生成的 Excel 文件名。

### 3. 运行工具
进入工具文件夹后运行主脚本。例如：
```bash
cd github_repo_ranker
python github_repo_ranker.py
```

### 4. 查看结果
结果将导出为 Excel 文件，默认文件名为 `repo_rank.xlsx`，可以在工具配置中修改。

## 注意事项
- 每个工具的依赖独立管理，需分别安装。
- 确保配置了有效的参数和环境。
- 如果需要访问更多 GitHub API 数据，请确保配置了有效的 GitHub Token。

## 贡献
欢迎提交 Issue 和 Pull Request 来改进此项目！

## 许可证
MIT License