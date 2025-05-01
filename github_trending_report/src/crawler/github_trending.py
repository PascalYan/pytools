import json
import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from pathlib import Path

from config.settings import GITHUB_TRENDING_URL, DATA_DIR

logger = logging.getLogger(__name__)


def fetch_trending_repos(language: str = "", since: str = "daily", spoken_language: str = "") -> List[Dict]:
    """
    从GitHub Trending获取热门仓库
    
    :param language: 编程语言过滤，如"python"，空字符串表示所有语言
    :param since: 时间范围，可选"daily", "weekly", "monthly"
    :param spoken_language: 界面语言过滤，如"zh"表示中文
    :return: 热门仓库列表，每个仓库包含名称、描述、星数等信息
    """
    # 生成文件名并检查本地缓存
    filepath = get_trending_data_filepath(language, since, spoken_language)
    
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                logger.info(f"趋势已经爬取过，从本地缓存加载数据: {filepath}")
                return cached_data
        except Exception as e:
            logger.error(f"加载缓存数据失败: {e}")
    
    # 没有缓存则从GitHub获取
    url = f"{GITHUB_TRENDING_URL}"
    if language:
        url += f"/{language}"
    
    params = {"since": since}
    if spoken_language:
        params["spoken_language_code"] = spoken_language
    
    try:
        logger.info(f"正在从GitHub获取趋势数据: {url}，参数: {params}") 
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        logger.debug(f"GitHub趋势API响应状态码: {response.status_code}")
        
        # 验证响应内容
        if not response.text:
            raise ValueError("GitHub趋势API返回空响应")
            
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', {'class': 'Box-row'})
        
        if not articles:
            logger.warning("GitHub趋势页面解析失败，未找到项目数据")
            return []
        
        trending_repos = []
        for article in articles:
            title = article.find('h2').text.strip().replace('\n', '').replace(' ', '')
            description = article.find('p', {'class': 'col-9'}).text.strip() if article.find('p', {'class': 'col-9'}) else ""
            
            # 提取总 Stars 数
            star_element = article.find('a', href=lambda href: href and '/stargazers' in href)
            total_stars = star_element.text.strip().replace(',', '') if star_element else '--'

            # 提取新增 Stars 数
            stars_change_element = article.find('span', class_='d-inline-block float-sm-right')
            stars_change = stars_change_element.text.strip().split(' ')[0].replace(',', '') if stars_change_element else '--'
            repo_info = {
                'name': title,
                'description': description,
                'stars': total_stars,
                f'{since}_stars': stars_change,
                'language': language if language else "all",
                'url': f"https://github.com/{title}",
                'fetched_at': datetime.now().isoformat()
            }
            trending_repos.append(repo_info)
        
        # 保存获取的数据
        save_trending_data(trending_repos, filepath)
        
        return trending_repos
    
    except Exception as e:
        logger.error(f"获取GitHub Trending数据失败: {e}")
        return []


def get_trending_data_filepath(language: str = "", since: str = "daily", spoken_language: str = "") -> Path:
    """
    生成GitHub趋势数据文件名路径
    
    :param language: 编程语言
    :param since: 时间范围
    :param spoken_language: 界面语言
    :return: 完整文件路径
    """
    today = datetime.now().strftime("%Y-%m-%d")
    param_str = f"{language}_{since}"
    if spoken_language:
        param_str += f"_{spoken_language}"
    data_file = f"github_trending_{param_str}_{today}.json"
    return DATA_DIR / data_file


def save_trending_data(repos: List[Dict], filepath: str = None):
    """
    保存趋势数据到JSON文件
    
    :param repos: 仓库数据列表
    :param filename: 自定义文件名
    """
    
    try:
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(repos, f, ensure_ascii=False, indent=2)
        logger.info(f"趋势数据已保存到: {filepath}")
    except Exception as e:
        logger.error(f"保存趋势数据失败: {e}")