import requests
import concurrent.futures
from github import Github
import xlsxwriter
from copy import deepcopy
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置 GitHub Token 和默认参数
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# 动态搜索关键词，例如 "chatbot language:Python"
DEFAULT_SEARCH_QUERY = "map client"  
# 动态搜索结果数量
DEFAULT_SEARCH_RESULTS = 5  
# 排序方式，可选值："stars"、"forks"、"last_updated"
DEFAULT_SORT_KEY = "stars"  
 # 指定仓库列表
DEFAULT_SPECIFY_REPO_NAMES = [ 
    "nanbingxyz/5ire",
    "NitroRCr/AIaW",
    "amidabuddha/console-chat-gpt",
    "continuedev/continue",
    "block/goose",
    "danny-avila/LibreChat",
    "3choff/mcp-chatbot",
    "sooperset/mcp-client-slackbot",
    "chainlit/chainlit",
    "CherryHQ/cherry-studio",
    "seekrays/seekchat",
    "VikashLoomba/copilot-mcp",
    "supercorp-ai/superinterface",
    "ChatGPTNextWeb/NextChat",
    "evilsocket/nerve",
    "zed-industries/zed",
    "luohy15/y-cli",
    "Enconvo/Enconvo",
    "BigSweetPotatoStudio/HyperChat",
    "ggozad/oterm",
    "Abiorh001/mcp_omni_connect",
    "daodao97/chatmcp",
    "cline/cline",
    "getcursor/cursor",
    "thinkinaixyz/deepchat",
    "cognitivecomputations/dolphin-mcp",
    "mario-andreschak/FLUJO",
    "nick1udwig/kibitz",
    "CopilotKit/open-mcp-client"
]
# 配置输出文件名
DEFAULT_OUTPUT_FILE = "repo_rank.xlsx"

###### 以上配置完，可以直接运行代码 ######


if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN 未设置，请配置有效的 GitHub Token。")

g = Github(GITHUB_TOKEN)

# 获取仓库信息
def fetch_repo_info(repo_name):
    try:
        repo = g.get_repo(repo_name)
        return {
            "name": repo.full_name,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "last_updated": repo.updated_at,
            "owner": repo.owner.login,
            "doc_link": extract_doc_link(repo),
            "license": repo.get_license().license.name if repo.get_license() else "未找到开源协议信息",
            "description": repo.description,
            "latest_release": repo.get_latest_release().tag_name if repo.get_latest_release() else None,
            "error": None
        }
    except Exception as e:
        return handle_repo_error(repo_name, str(e))

# 处理仓库错误
def handle_repo_error(repo_name, error_message):
    if "404" in error_message:
        error_message = "仓库不存在或不可访问 (404)"
    print(f"获取 {repo_name} 的信息时出错: {error_message}")
    return {
        "name": repo_name,
        "stars": 0,
        "forks": 0,
        "last_updated": None,
        "owner": None,
        "doc_link": None,
        "license": "未找到开源协议信息",
        "description": None,
        "latest_release": None,
        "error": error_message
    }

# 提取文档链接
def extract_doc_link(repo):
    try:
        content = repo.get_readme().decoded_content.decode('utf-8')
        for line in content.splitlines():
            if 'http' in line and ('doc' in line.lower() or 'documentation' in line.lower()):
                start = line.find('http')
                end = line.find(' ', start)
                return line[start:end] if end != -1 else line[start:]
    except Exception:
        pass
    return None

# 搜索 GitHub 仓库
def search_github_repositories(query, per_page=10):
    url = "https://api.github.com/search/repositories"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": per_page}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return [fetch_repo_info(item.get("full_name")) for item in response.json().get("items", [])]
    except Exception as e:
        print(f"GitHub 搜索 API 调用失败: {e}")
        return []
    
    # 获取指定仓库信息
def fetch_specified_repos(repo_names):
    print("获取指定仓库信息...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return list(executor.map(fetch_repo_info, repo_names))

# 保存为 Excel
def save_to_excel(repo_info_list, output_file):
    workbook = xlsxwriter.Workbook(output_file)
    worksheet = workbook.add_worksheet("Repo Info")

    headers = ["排名", "仓库名称", "Star 数 (k)", "Fork 数", "最后更新时间", "作者/公司", "官方文档链接", "开源协议", "仓库描述", "最近发布版本", "错误信息"]
    header_format = workbook.add_format({
        'bold': True, 'font_color': 'white', 'bg_color': '#FF6F61', 'border': 1,
        'align': 'center', 'valign': 'vcenter', 'font_size': 14, 'font_name': '微软雅黑'
    })
    cell_format = workbook.add_format({
        'text_wrap': True, 'border': 1, 'align': 'left', 'valign': 'top',
        'font_size': 12, 'font_name': '微软雅黑', 'bg_color': '#FFF4E6', 'bold': True
    })

    worksheet.set_column(0, len(headers) - 1, 20)
    for col_idx, header in enumerate(headers):
        worksheet.write(0, col_idx, header, header_format)

    # 在保存为 Excel 的逻辑中，追加调用 translate_to_chinese 翻译描述为中文
    for row_idx, repo_info in enumerate(repo_info_list, start=1):
        translated_description = translate_to_chinese(repo_info['description']) if repo_info['description'] else "N/A"
        row = [
            row_idx,
            repo_info['name'],
            f"{repo_info['stars'] / 1000:.1f}k",
            repo_info['forks'],
            str(repo_info['last_updated']),
            repo_info['owner'],
            repo_info['doc_link'] or "N/A",
            repo_info['license'],
            f"{repo_info['description']}\n(翻译: {translated_description})" if repo_info['description'] else "N/A",
            repo_info['latest_release'] or "N/A",
            repo_info.get('error', "无")
        ]
        for col_idx, cell_value in enumerate(row):
            worksheet.write(row_idx, col_idx, cell_value, cell_format)

    workbook.close()
    print(f"结果已保存到 {output_file}")


# 翻译为中文
def translate_to_chinese(text):
    if not text:
        return "翻译不可用"
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {"q": text, "langpair": "en|zh-CN"}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("responseData", {}).get("translatedText", "翻译不可用")
    except Exception as e:
        print(f"翻译 API 调用失败: {e}")
    return "翻译不可用"


# 主流程
if __name__ == "__main__":
    print("开始调研 GitHub 仓库...")

    # 获取指定仓库信息
    specified_repos = fetch_specified_repos(DEFAULT_SPECIFY_REPO_NAMES) if DEFAULT_SPECIFY_REPO_NAMES else []

    # 动态搜索开源项目
    search_results = search_github_repositories(DEFAULT_SEARCH_QUERY, per_page=DEFAULT_SEARCH_RESULTS)

    # 合并结果并去重
    print("合并结果并去重...")
    all_repos = list({repo['name']: deepcopy(repo) for repo in specified_repos + search_results if repo.get('name')}.values())

    # 确保 sorted_repos 定义正确
    sorted_repos = sorted(all_repos, key=lambda x: x[DEFAULT_SORT_KEY], reverse=True) if all_repos else []

    # 保存为 Excel
    if sorted_repos:
        print("保存结果到 Excel 文件...")
        save_to_excel(sorted_repos, DEFAULT_OUTPUT_FILE)
        print(f"调研完成，结果已保存到 {DEFAULT_OUTPUT_FILE}。")
    else:
        print("没有可用的仓库信息，未生成 Excel 文件。")