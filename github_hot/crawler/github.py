import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import base64
import logging

class GitHubHotCrawler:
    """GitHub热门仓库爬虫"""
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        language = os.getenv('GITHUB_LANGUAGE', '')
        if language and '#' in language:
            language = language.split('#')[0].strip()
        self.language = language
        self.since = os.getenv('GITHUB_SINCE', 'weekly')
        self.limit = int(os.getenv('GITHUB_LIMIT', '10'))
        if self.since not in ['daily', 'weekly', 'monthly']:
            logging.warning(f"无效的时间范围配置: {self.since}，使用默认的周报")
            self.since = 'weekly'
        if not self.github_token:
            logging.error("GitHub Token未设置！请在.env文件中设置GITHUB_TOKEN")
            raise ValueError("GitHub Token未设置")
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        logging.info(f"GitHub爬虫初始化完成，语言：{self.language or '所有语言'}，时间范围：{self.since}，数量限制：{self.limit}")

    def get_date_range(self):
        end_date = datetime.now()
        if self.since == 'daily':
            days = 1
        elif self.since == 'weekly':
            days = 7
        else:
            days = 30
        start_date = end_date - timedelta(days=days)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

    def get_repo_details(self, owner, repo):
        try:
            repo_url = f"https://api.github.com/repos/{owner}/{repo}"
            try:
                response = requests.get(repo_url, headers=self.headers, timeout=10)
            except requests.exceptions.RequestException as e:
                logging.error(f"请求仓库 {owner}/{repo} 基本信息时发生网络错误: {str(e)}")
                return {}
            if response is None or response.status_code != 200:
                logging.warning(f"获取仓库 {owner}/{repo} 信息失败: {response.status_code if response else 'None response'}")
                return {}
            try:
                repo_info = response.json()
            except Exception as e:
                logging.warning(f"解析仓库 {owner}/{repo} 信息失败: {str(e)}")
                return {}
            if not isinstance(repo_info, dict):
                logging.warning(f"获取仓库 {owner}/{repo} 信息格式错误")
                return {}
            readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
            try:
                readme_response = requests.get(readme_url, headers=self.headers, timeout=10)
            except requests.exceptions.RequestException as e:
                logging.error(f"请求仓库 {owner}/{repo} README 时发生网络错误: {str(e)}")
                readme_response = None
            readme_content = ""
            if readme_response is not None and readme_response.status_code == 200:
                try:
                    readme_data = readme_response.json()
                    if isinstance(readme_data, dict) and 'content' in readme_data:
                        try:
                            readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
                            readme_content = readme_content[:500] + "..." if len(readme_content) > 500 else readme_content
                        except Exception as e:
                            logging.warning(f"解码 README 内容失败: {str(e)}")
                except Exception as e:
                    logging.warning(f"解析 README 数据失败: {str(e)}")
            contributors_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
            try:
                contributors_response = requests.get(contributors_url, headers=self.headers, timeout=10)
            except requests.exceptions.RequestException as e:
                logging.error(f"请求仓库 {owner}/{repo} 贡献者信息时发生网络错误: {str(e)}")
                contributors_response = None
            contributors = []
            if contributors_response is not None and contributors_response.status_code == 200:
                try:
                    contributors_data = contributors_response.json()
                    if isinstance(contributors_data, list):
                        for contributor in contributors_data[:5]:
                            if isinstance(contributor, dict) and 'login' in contributor:
                                contributors.append(contributor['login'])
                except Exception as e:
                    logging.warning(f"解析贡献者数据失败: {str(e)}")
            updated_at_str = ""
            if isinstance(repo_info, dict) and 'updated_at' in repo_info and repo_info['updated_at']:
                try:
                    updated_at = datetime.strptime(repo_info['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
                    updated_at_str = updated_at.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    logging.warning(f"解析更新时间失败: {str(e)}")
            description = repo_info.get('description', '') if isinstance(repo_info, dict) else ''
            license_name = repo_info.get('license', {}).get('name', '') if isinstance(repo_info, dict) else ''
            topics = repo_info.get('topics', []) if isinstance(repo_info, dict) else []
            homepage = repo_info.get('homepage', '') if isinstance(repo_info, dict) else ''
            open_issues = repo_info.get('open_issues', 0) if isinstance(repo_info, dict) else 0
            watchers = repo_info.get('watchers', 0) if isinstance(repo_info, dict) else 0
            return {
                'description': description,
                'readme': readme_content,
                'contributors': contributors,
                'updated_at': updated_at_str,
                'license': license_name,
                'topics': topics,
                'homepage': homepage,
                'open_issues': open_issues,
                'watchers': watchers
            }
        except Exception as e:
            logging.error(f"获取仓库 {owner}/{repo} 详细信息时出错: {str(e)}")
            return {}

    def get_trending_repos(self):
        logging.info(f"开始获取{self.language or '所有语言'}的{self.since}热门仓库...")
        url = self.get_trending_url()
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                logging.error(f"获取GitHub Trending页面失败: {response.status_code}")
                raise Exception(f"获取GitHub Trending页面失败: {response.status_code}")
            soup = BeautifulSoup(response.text, 'html.parser')
            repos = []
            repo_items = soup.select('article.Box-row')
            if not repo_items:
                logging.warning("未找到任何仓库条目，可能是页面结构发生变化")
                return []
            for item in repo_items[:self.limit]:
                try:
                    repo_link = item.select_one('h2 a')
                    if not repo_link or 'href' not in repo_link.attrs:
                        logging.warning("未找到有效的仓库链接")
                        continue
                    repo_name = repo_link['href'].strip('/')
                    if '/' not in repo_name:
                        logging.warning(f"无效的仓库名称格式: {repo_name}")
                        continue
                    owner, repo = repo_name.split('/')
                    repo_url = f"https://github.com/{repo_name}"
                    description = item.select_one('p')
                    description = description.text.strip() if description else ''
                    language = item.select_one('span[itemprop="programmingLanguage"]')
                    language = language.text.strip() if language else self.language or 'Unknown'
                    stars = item.select_one('a[href$="/stargazers"]')
                    try:
                        stars = int(stars.text.strip().replace(',', '')) if stars else 0
                    except (ValueError, AttributeError):
                        stars = 0
                        logging.warning(f"解析星标数失败: {repo_name}")
                    forks = item.select_one('a[href$="/forks"]')
                    try:
                        forks = int(forks.text.strip().replace(',', '')) if forks else 0
                    except (ValueError, AttributeError):
                        forks = 0
                        logging.warning(f"解析Fork数失败: {repo_name}")
                    details = self.get_repo_details(owner, repo)
                    repo_info = {
                        'name': repo_name,
                        'description': description or details.get('description', ''),
                        'stars': stars,
                        'forks': forks,
                        'url': repo_url,
                        'language': language,
                        'details': details
                    }
                    repos.append(repo_info)
                    logging.info(f"已获取仓库: {repo_info['name']}")
                except Exception as e:
                    logging.error(f"解析仓库信息时出错: {str(e)}")
                    continue
            logging.info(f"成功获取{len(repos)}个热门仓库")
            return repos
        except requests.exceptions.RequestException as e:
            logging.error(f"请求GitHub Trending页面时发生网络错误: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"获取热门仓库时发生错误: {str(e)}")
            raise

    def get_trending_url(self):
        url = "https://github.com/trending"
        if self.language:
            url += f"/{self.language}"
        url += f"?since={self.since}"
        return url

    def get_report_type_text(self):
        return '日报' if self.since == 'daily' else '周报' if self.since == 'weekly' else '月报'

    def get_time_range_text(self):
        if self.since == 'daily':
            return '过去24小时内'
        elif self.since == 'weekly':
            return '过去7天内'
        else:
            return '过去30天内'

    def get_language_text(self):
        if not self.language or self.language.startswith('#'):
            return "GitHub热门项目"
        return f"GitHub {self.language} 项目"

    # TODO: 实现 GitHubHotCrawler 的所有方法和逻辑
    pass 