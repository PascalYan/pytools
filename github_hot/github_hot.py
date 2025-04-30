import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMedia
import logging
import traceback
import json
from abc import ABC, abstractmethod

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

class ArticlePublisher(ABC):
    """文章发布基类"""
    @abstractmethod
    def publish(self, title, content):
        """发布文章"""
        pass

class WeChatMPPublisher(ArticlePublisher):
    """微信公众号发布器"""
    def __init__(self):
        self.app_id = os.getenv('WECHAT_APP_ID')
        self.app_secret = os.getenv('WECHAT_APP_SECRET')
        self.direct_publish = os.getenv('WECHAT_DIRECT_PUBLISH', 'false').lower() == 'true'
        
        if not all([self.app_id, self.app_secret]):
            logger.error("微信公众号配置未设置！请在.env文件中设置WECHAT_APP_ID和WECHAT_APP_SECRET")
            raise ValueError("微信公众号配置未设置")
            
        self.client = WeChatClient(self.app_id, self.app_secret)
        logger.info(f"微信公众号发布器初始化完成，{'直接发布' if self.direct_publish else '保存为草稿'}")
    
    def publish(self, title, content):
        """发布文章到微信公众号"""
        logger.info("开始发布文章到微信公众号...")
        try:
            # 下载GitHub logo作为封面图片
            cover_url = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            logger.debug(f"开始下载封面图片: {cover_url}")
            response = requests.get(cover_url)
            if response.status_code != 200:
                raise Exception("下载封面图片失败")
            
            # 保存临时图片文件
            with open('temp_cover.jpg', 'wb') as f:
                f.write(response.content)
            
            # 上传封面图片为永久素材
            logger.debug("开始上传封面图片")
            with open('temp_cover.jpg', 'rb') as f:
                thumb = self.client.material.add('image', f)
            logger.debug(f"封面图片上传成功: {thumb}")
            
            # 删除临时文件
            os.remove('temp_cover.jpg')
            
            # 构建文章数据
            articles = [{
                'title': title,
                'content': content,
                'thumb_media_id': thumb['media_id'],
                'need_open_comment': 0,
                'only_fans_can_comment': 0,
                'show_cover_pic': 1,
                'digest': content.split('\n')[0][:120],  # 只取第一行作为摘要
                'content_source_url': 'https://github.com/trending'  # 添加原文链接
            }]
            logger.debug(f"文章数据: {json.dumps(articles, ensure_ascii=False)}")
            
            if self.direct_publish:
                # 直接发布
                logger.debug("开始直接发布文章")
                result = self.client.material.add_articles(articles)
                logger.debug(f"直接发布结果: {result}")
                logger.info("文章已直接发布")
            else:
                # 保存为草稿
                url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self.client.access_token}"
                data = {
                    "articles": articles
                }
                logger.debug(f"开始保存草稿，URL: {url}")
                logger.debug(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
                
                # 使用 json.dumps 确保中文正确编码
                json_str = json.dumps(data, ensure_ascii=False).encode('utf-8')
                headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                    'Accept-Charset': 'utf-8'
                }
                response = requests.post(url, data=json_str, headers=headers)
                result = response.json()
                logger.debug(f"保存草稿响应: {result}")
                
                # 检查是否包含 media_id，如果有则表示成功
                if 'media_id' in result:
                    logger.info(f"文章已保存为草稿，media_id: {result.get('media_id')}")
                else:
                    error_msg = result.get('errmsg', '未知错误')
                    logger.error(f"保存草稿失败: {error_msg}")
                    raise Exception(f"保存草稿失败: {error_msg}")
            
            return result.get('media_id')
            
        except Exception as e:
            logger.error(f"发布文章到微信公众号失败: {str(e)}")
            raise

class WeChatWebhookPublisher(ArticlePublisher):
    """企业微信群机器人发布器"""
    def __init__(self):
        self.webhook_url = os.getenv('WECHAT_ARTICLE_WEBHOOK')
        self.url_source = os.getenv('WECHAT_ARTICLE_URL_SOURCE', 'csdn')
        
        if not self.webhook_url:
            logger.error("企业微信群机器人webhook地址未设置！请在.env文件中设置WECHAT_ARTICLE_WEBHOOK")
            raise ValueError("企业微信群机器人webhook地址未设置")
            
        logger.info(f"企业微信群机器人发布器初始化完成，URL来源：{self.url_source}")
    
    def publish(self, title, content, article_urls=None):
        """发送文章到企业微信群"""
        logger.info("开始发送文章到企业微信群...")
        try:
            # 选择URL来源
            url = None
            if article_urls:
                # 根据配置选择URL来源
                if self.url_source == 'csdn' and 'csdn' in article_urls:
                    url = article_urls['csdn']
                elif self.url_source == 'juejin' and 'juejin' in article_urls:
                    url = article_urls['juejin']
                elif self.url_source == 'devto' and 'devto' in article_urls:
                    url = article_urls['devto']
                elif self.url_source == 'confluence' and 'confluence' in article_urls:
                    url = article_urls['confluence']
                elif self.url_source == 'yuque' and 'yuque' in article_urls:
                    url = article_urls['yuque']
                elif self.url_source == 'notion' and 'notion' in article_urls:
                    url = article_urls['notion']
                elif 'github' in article_urls:
                    url = article_urls['github']
            
            if not url:
                logger.error("未找到可用的文章URL")
                raise ValueError("未找到可用的文章URL")
            
            # 构建图文消息
            data = {
                "msgtype": "news",
                "news": {
                    "articles": [{
                        "title": title,
                        "description": content[:200] + "..." if len(content) > 200 else content,
                        "url": url,
                        "picurl": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
                    }]
                }
            }
            
            logger.info("正在发送文章内容...")
            response = requests.post(self.webhook_url, json=data)
            response_json = response.json()
            
            if response_json['errcode'] != 0:
                logger.error(f"发送文章内容失败: {response.text}")
                raise Exception(f"发送文章内容失败: {response_json['errcode']}")
            
            logger.info("文章内容发送成功")
            return None  # 企业微信不返回URL
            
        except Exception as e:
            logger.error(f"发送文章内容时发生错误: {str(e)}")
            raise

class YuquePublisher(ArticlePublisher):
    """语雀发布器"""
    def __init__(self):
        self.token = os.getenv('YUQUE_TOKEN')
        self.namespace = os.getenv('YUQUE_NAMESPACE')
        self.slug = os.getenv('YUQUE_SLUG')
        
        if not all([self.token, self.namespace, self.slug]):
            logger.error("语雀配置未设置！请在.env文件中设置YUQUE_TOKEN、YUQUE_NAMESPACE和YUQUE_SLUG")
            raise ValueError("语雀配置未设置")
            
        self.headers = {
            'X-Auth-Token': self.token,
            'Content-Type': 'application/json'
        }
        logger.info("语雀发布器初始化完成")
    
    def publish(self, title, content):
        """发布文章到语雀"""
        logger.info("开始发布文章到语雀...")
        try:
            # 构建文章数据
            data = {
                "title": title,
                "body": content,
                "format": "markdown",
                "slug": self.slug
            }
            
            # 发布文章
            url = f"https://www.yuque.com/api/v2/repos/{self.namespace}/docs"
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code not in [200, 201]:
                logger.error(f"发布文章到语雀失败: {response.text}")
                raise Exception(f"发布文章到语雀失败: {response.status_code}")
            
            article_url = response.json()['data']['url']
            logger.info(f"文章发布到语雀成功，URL: {article_url}")
            return article_url
            
        except Exception as e:
            logger.error(f"发布文章到语雀时发生错误: {str(e)}")
            raise

class NotionPublisher(ArticlePublisher):
    """Notion发布器"""
    def __init__(self):
        self.token = os.getenv('NOTION_TOKEN')
        self.database_id = os.getenv('NOTION_DATABASE_ID')
        
        if not all([self.token, self.database_id]):
            logger.error("Notion配置未设置！请在.env文件中设置NOTION_TOKEN和NOTION_DATABASE_ID")
            raise ValueError("Notion配置未设置")
            
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }
        logger.info("Notion发布器初始化完成")
    
    def publish(self, title, content):
        """发布文章到Notion"""
        logger.info("开始发布文章到Notion...")
        try:
            # 构建文章数据
            data = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    }
                },
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": content
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
            
            # 发布文章
            url = "https://api.notion.com/v1/pages"
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code not in [200, 201]:
                logger.error(f"发布文章到Notion失败: {response.text}")
                raise Exception(f"发布文章到Notion失败: {response.status_code}")
            
            article_url = response.json()['url']
            logger.info(f"文章发布到Notion成功，URL: {article_url}")
            return article_url
            
        except Exception as e:
            logger.error(f"发布文章到Notion时发生错误: {str(e)}")
            raise

class CSDNPublisher(ArticlePublisher):
    """CSDN发布器"""
    def __init__(self):
        self.username = os.getenv('CSDN_USERNAME')
        self.password = os.getenv('CSDN_PASSWORD')
        self.cookie = os.getenv('CSDN_COOKIE')
        
        if not all([self.username, self.password, self.cookie]):
            logger.error("CSDN配置未设置！请在.env文件中设置CSDN_USERNAME、CSDN_PASSWORD和CSDN_COOKIE")
            raise ValueError("CSDN配置未设置")
            
        self.headers = {
            'Cookie': self.cookie,
            'Content-Type': 'application/json'
        }
        logger.info("CSDN发布器初始化完成")
    
    def publish(self, title, content):
        """发布文章到CSDN"""
        logger.info("开始发布文章到CSDN...")
        try:
            # 构建文章数据
            data = {
                "title": title,
                "content": content,
                "markdowncontent": content,
                "categories": "Python",
                "tags": "GitHub,Python,热门项目",
                "type": "original"
            }
            
            # 发布文章
            url = "https://mp.csdn.net/mp_blog/manage/article"
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code != 200:
                logger.error(f"发布文章到CSDN失败: {response.text}")
                raise Exception(f"发布文章到CSDN失败: {response.status_code}")
            
            article_url = response.json()['data']['url']
            logger.info(f"文章发布到CSDN成功，URL: {article_url}")
            return article_url
            
        except Exception as e:
            logger.error(f"发布文章到CSDN时发生错误: {str(e)}")
            raise

class JuejinPublisher(ArticlePublisher):
    """掘金发布器"""
    def __init__(self):
        self.user_id = os.getenv('JUEJIN_USER_ID')
        self.cookie = os.getenv('JUEJIN_COOKIE')
        
        if not all([self.user_id, self.cookie]):
            logger.error("掘金配置未设置！请在.env文件中设置JUEJIN_USER_ID和JUEJIN_COOKIE")
            raise ValueError("掘金配置未设置")
            
        self.headers = {
            'Cookie': self.cookie,
            'Content-Type': 'application/json'
        }
        logger.info("掘金发布器初始化完成")
    
    def publish(self, title, content):
        """发布文章到掘金"""
        logger.info("开始发布文章到掘金...")
        try:
            # 构建文章数据
            data = {
                "title": title,
                "content": content,
                "category_id": "6809637769959178254",  # Python分类
                "tag_ids": ["6809640407484334093"],  # GitHub标签
                "link_url": "",
                "cover_image": "",
                "is_gfw": 0
            }
            
            # 发布文章
            url = "https://api.juejin.cn/content_api/v1/article/publish"
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code != 200:
                logger.error(f"发布文章到掘金失败: {response.text}")
                raise Exception(f"发布文章到掘金失败: {response.status_code}")
            
            article_url = f"https://juejin.cn/post/{response.json()['data']['article_id']}"
            logger.info(f"文章发布到掘金成功，URL: {article_url}")
            return article_url
            
        except Exception as e:
            logger.error(f"发布文章到掘金时发生错误: {str(e)}")
            raise

class DevToPublisher(ArticlePublisher):
    """Dev.to发布器"""
    def __init__(self):
        self.api_key = os.getenv('DEVTO_API_KEY')
        
        if not self.api_key:
            logger.error("Dev.to配置未设置！请在.env文件中设置DEVTO_API_KEY")
            raise ValueError("Dev.to配置未设置")
            
        self.headers = {
            'api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        logger.info("Dev.to发布器初始化完成")
    
    def publish(self, title, content):
        """发布文章到Dev.to"""
        logger.info("开始发布文章到Dev.to...")
        try:
            # 构建文章数据
            data = {
                "article": {
                    "title": title,
                    "body_markdown": content,
                    "published": True,
                    "tags": ["python", "github", "trending"]
                }
            }
            
            # 发布文章
            url = "https://dev.to/api/articles"
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code not in [200, 201]:
                logger.error(f"发布文章到Dev.to失败: {response.text}")
                raise Exception(f"发布文章到Dev.to失败: {response.status_code}")
            
            article_url = response.json()['url']
            logger.info(f"文章发布到Dev.to成功，URL: {article_url}")
            return article_url
            
        except Exception as e:
            logger.error(f"发布文章到Dev.to时发生错误: {str(e)}")
            raise

class LocalFilePublisher(ArticlePublisher):
    """本地文件发布器"""
    def __init__(self):
        self.output_dir = os.getenv('LOCAL_OUTPUT_DIR')
        self.filename_template = os.getenv('LOCAL_FILENAME_TEMPLATE', '{date}_{title}.md')
        
        if not self.output_dir:
            logger.error("本地文件输出目录未设置！请在.env文件中设置LOCAL_OUTPUT_DIR")
            raise ValueError("本地文件输出目录未设置")
            
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        logger.info(f"本地文件发布器初始化完成，输出目录：{self.output_dir}，文件名模板：{self.filename_template}")
    
    def publish(self, title, content):
        """发布文章到本地文件
        
        Args:
            title: 文章标题
            content: 文章内容
            
        Returns:
            str: 文件的绝对路径
        """
        logger.info("开始保存文章到本地文件...")
        try:
            # 准备文件名变量
            date_str = datetime.now().strftime('%Y-%m-%d')
            time_str = datetime.now().strftime('%H-%M-%S')
            
            # 生成文件名
            # 支持的变量：
            # {date}: 当前日期 (YYYY-MM-DD)
            # {time}: 当前时间 (HH-MM-SS)
            # {title}: 文章标题
            filename = self.filename_template.format(
                date=date_str,
                time=time_str,
                title=title
            )
            
            filepath = os.path.join(self.output_dir, filename)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            abs_path = os.path.abspath(filepath)
            logger.info(f"文章已保存到：{abs_path}")
            return abs_path
            
        except Exception as e:
            logger.error(f"保存文章到本地文件时发生错误: {str(e)}")
            raise

class GitHubHotCrawler:
    """GitHub热门仓库爬虫"""
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.language = os.getenv('GITHUB_LANGUAGE', '')  # 空字符串表示所有语言
        self.since = os.getenv('GITHUB_SINCE', 'weekly')
        self.limit = int(os.getenv('GITHUB_LIMIT', '10'))
        
        # 验证时间范围
        if self.since not in ['daily', 'weekly', 'monthly']:
            logger.warning(f"无效的时间范围配置: {self.since}，使用默认的周报")
            self.since = 'weekly'
        
        if not self.github_token:
            logger.error("GitHub Token未设置！请在.env文件中设置GITHUB_TOKEN")
            raise ValueError("GitHub Token未设置")
            
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        logger.info(f"GitHub爬虫初始化完成，语言：{self.language or '所有语言'}，时间范围：{self.since}，数量限制：{self.limit}")
    
    def get_date_range(self):
        """获取日期范围
        
        Returns:
            tuple: (开始日期, 结束日期) 格式为 YYYY-MM-DD
        """
        end_date = datetime.now()
        if self.since == 'daily':
            days = 1
        elif self.since == 'weekly':
            days = 7
        else:  # monthly
            days = 30
        
        start_date = end_date - timedelta(days=days)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    def get_trending_repos(self):
        """从GitHub Trending页面获取热门仓库"""
        logger.info(f"开始获取{self.language or '所有语言'}的{self.since}热门仓库...")
        
        # 构建Trending页面URL
        url = self.get_trending_url()
        
        # 发送请求获取页面内容
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            logger.error(f"获取GitHub Trending页面失败: {response.status_code}")
            raise Exception(f"获取GitHub Trending页面失败: {response.status_code}")
        
        # 解析页面内容
        soup = BeautifulSoup(response.text, 'html.parser')
        repos = []
        
        # 查找所有仓库条目
        repo_items = soup.select('article.Box-row')
        for item in repo_items[:self.limit]:
            try:
                # 获取仓库名称和URL
                repo_link = item.select_one('h2 a')
                repo_name = repo_link['href'].strip('/')
                repo_url = f"https://github.com/{repo_name}"
                
                # 获取仓库描述
                description = item.select_one('p')
                description = description.text.strip() if description else ''
                
                # 获取语言
                language = item.select_one('span[itemprop="programmingLanguage"]')
                language = language.text.strip() if language else self.language or 'Unknown'
                
                # 获取星标数
                stars = item.select_one('a[href$="/stargazers"]')
                stars = int(stars.text.strip().replace(',', '')) if stars else 0
                
                # 获取Fork数
                forks = item.select_one('a[href$="/forks"]')
                forks = int(forks.text.strip().replace(',', '')) if forks else 0
                
                repo_info = {
                    'name': repo_name,
                    'description': description,
                    'stars': stars,
                    'forks': forks,
                    'url': repo_url,
                    'language': language
                }
                repos.append(repo_info)
                logger.info(f"已获取仓库: {repo_info['name']}")
                
            except Exception as e:
                logger.error(f"解析仓库信息时出错: {str(e)}")
                continue
        
        logger.info(f"成功获取{len(repos)}个热门仓库")
        return repos
    
    def get_trending_url(self):
        """获取GitHub Trending页面的URL"""
        url = "https://github.com/trending"
        if self.language:
            url += f"/{self.language}"
        url += f"?since={self.since}"
        return url
    
    def get_report_type_text(self):
        """获取报告类型文本"""
        return '日报' if self.since == 'daily' else '周报' if self.since == 'weekly' else '月报'
    
    def get_time_range_text(self):
        """获取时间范围文本"""
        if self.since == 'daily':
            return '过去24小时内'
        elif self.since == 'weekly':
            return '过去7天内'
        else:  # monthly
            return '过去30天内'
            
    def get_language_text(self):
        """获取语言文本"""
        if not self.language or self.language.startswith('#'):  # 处理空字符串或注释
            return "GitHub热门项目"
        return f"GitHub {self.language} 项目"

class ArticleGenerator:
    """文章生成器"""
    def __init__(self):
        self.template = """
<h1>{title}</h1>

<p>本{report_type}为大家带来 GitHub 上最受欢迎的 {language} 项目，这些项目在{time_range}获得了最多的 stars。</p>

{content}

<h2>项目详情</h2>

{details}

<hr/>
<p><em>数据统计时间：{time_range}</em></p>
"""
        logger.info("文章生成器初始化完成")
    
    def generate_article(self, repos, language='Python', crawler=None, title=None):
        """生成文章内容
        
        Args:
            repos: 仓库列表
            language: 编程语言
            crawler: GitHubHotCrawler实例
            title: 文章标题，如果提供则在文章开头显示
        """
        logger.info("开始生成文章...")
        
        # 获取时间范围
        if crawler:
            time_range = crawler.get_time_range_text()
        else:
            time_range = '过去7天内'  # 默认为周报
        
        # 生成项目列表
        content = "<ol>"
        details = ""
        
        for i, repo in enumerate(repos, 1):
            content += f'<li><a href="{repo["url"]}">{repo["name"]}</a> - {repo["description"]}</li>'
            details += f"""
<h3>{i}. {repo['name']}</h3>

<ul>
<li>描述：{repo['description']}</li>
<li>星标数：{repo['stars']}</li>
<li>Fork数：{repo['forks']}</li>
<li>主要语言：{repo['language']}</li>
<li>项目地址：<a href="{repo['url']}">{repo['url']}</a></li>
</ul>
"""
        
        content += "</ol>"
        
        article = self.template.format(
            title=title or "",
            language=language,
            report_type=crawler.get_report_type_text() if crawler else '周报',
            time_range=time_range,
            content=content,
            details=details
        )
        logger.info("文章生成完成")
        return article

class ConfluencePublisher(ArticlePublisher):
    def __init__(self):
        self.base_url = os.getenv('CONFLUENCE_BASE_URL')
        self.username = os.getenv('CONFLUENCE_USERNAME')
        self.api_token = os.getenv('CONFLUENCE_API_TOKEN')
        self.space_key = os.getenv('CONFLUENCE_SPACE_KEY')
        self.parent_page_id = os.getenv('CONFLUENCE_PARENT_PAGE_ID')
        
        if not all([self.base_url, self.username, self.api_token, self.space_key, self.parent_page_id]):
            logger.error("Confluence配置未设置！请在.env文件中设置相关配置")
            raise ValueError("Confluence配置未设置")
            
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        logger.info("Confluence发布器初始化完成")
    
    def publish(self, title, content):
        """发布文章到Confluence"""
        logger.info("开始发布文章到Confluence...")
        try:
            # 构建文章数据
            data = {
                "type": "page",
                "title": title,
                "space": {"key": self.space_key},
                "ancestors": [{"id": self.parent_page_id}],
                "body": {
                    "storage": {
                        "value": content,
                        "representation": "storage"
                    }
                }
            }
            
            # 发布文章
            url = f"{self.base_url}/rest/api/content"
            response = requests.post(url, headers=self.headers, json=data)
            logger.debug(f"confluence 发布文章，请求url：{url}，返回结果：{response}");
            response_json = response.json()
            
            if response.status_code not in [200, 201]:
                logger.error(f"发布文章到Confluence失败: {response.text}")
                raise Exception(f"发布文章到Confluence失败: {response.status_code}")
            
            # 获取文章URL
            article_url = f"{self.base_url}/pages/viewpage.action?pageId={response_json['id']}"
            logger.info(f"文章发布成功，URL: {article_url}")
            return article_url
            
        except Exception as e:
            logger.error(f"发布文章到Confluence时发生错误: {str(e)}")
            raise

class WeChatNotifier:
    def __init__(self):
        self.alert_webhook = os.getenv('WECHAT_ALERT_WEBHOOK')
        self.article_webhook = os.getenv('WECHAT_ARTICLE_WEBHOOK')
        
        if not self.alert_webhook:
            logger.error("企业微信群机器人告警webhook地址未设置！请在.env文件中设置WECHAT_ALERT_WEBHOOK")
            raise ValueError("企业微信群机器人告警webhook地址未设置")
            
        if not self.article_webhook:
            logger.error("企业微信群机器人文章推送webhook地址未设置！请在.env文件中设置WECHAT_ARTICLE_WEBHOOK")
            raise ValueError("企业微信群机器人文章推送webhook地址未设置")
            
        logger.info("企业微信群机器人通知器初始化完成")
    
    def send_alert(self, error_msg):
        """发送错误报警"""
        logger.info("开始发送错误告警...")
        try:
            # 格式化错误信息
            if isinstance(error_msg, Exception):
                error_type = type(error_msg).__name__
                error_info = str(error_msg)
                stack_trace = traceback.format_exc()
            else:
                # 如果是字符串，尝试解析错误信息
                error_lines = error_msg.split('\n')
                error_type = error_lines[0] if error_lines else "未知错误"
                error_info = error_lines[1] if len(error_lines) > 1 else error_msg
                stack_trace = '\n'.join(error_lines[2:]) if len(error_lines) > 2 else ''
            
            # 构建告警消息
            content = [
                "### GitHub热门项目抓取程序出错",
                f"> 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"> 错误类型：{error_type}",
                f"> 错误信息：{error_info}"
            ]
            
            # 如果有堆栈跟踪，添加到消息中
            if stack_trace:
                content.append(f"> 错误堆栈：\n{stack_trace}\n")
            
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": "\n".join(content)
                }
            }
            
            logger.info("正在发送告警消息...")
            response = requests.post(self.alert_webhook, json=data)
            response_json = response.json()
            
            if response_json['errcode'] != 0:
                logger.error(f"发送企业微信消息失败: {response.text}")
            else:
                logger.info("告警消息发送成功")
                
        except Exception as e:
            logger.error(f"发送告警消息时发生错误: {str(e)}")
            raise
    

def get_publishers():
    """获取启用的发布器"""
    publishers = []
    
    if os.getenv('ENABLE_LOCAL_FILE', 'false').lower() == 'true':
        publishers.append(LocalFilePublisher())
    
    if os.getenv('ENABLE_WECHAT_MP', 'false').lower() == 'true':
        publishers.append(WeChatMPPublisher())
    
    if os.getenv('ENABLE_WECHAT_WEBHOOK', 'false').lower() == 'true':
        publishers.append(WeChatWebhookPublisher())
    
    if os.getenv('ENABLE_CONFLUENCE', 'false').lower() == 'true':
        publishers.append(ConfluencePublisher())
    
    if os.getenv('ENABLE_YUQUE', 'false').lower() == 'true':
        publishers.append(YuquePublisher())
    
    if os.getenv('ENABLE_NOTION', 'false').lower() == 'true':
        publishers.append(NotionPublisher())
    
    if os.getenv('ENABLE_CSDN', 'false').lower() == 'true':
        publishers.append(CSDNPublisher())
    
    if os.getenv('ENABLE_JUEJIN', 'false').lower() == 'true':
        publishers.append(JuejinPublisher())
    
    if os.getenv('ENABLE_DEVTO', 'false').lower() == 'true':
        publishers.append(DevToPublisher())
    
    return publishers

def main():
    """主函数"""
    try:
        logger.info("程序开始执行...")
        
        # 初始化各个组件
        crawler = GitHubHotCrawler()
        generator = ArticleGenerator()
        notifier = WeChatNotifier()
        
        # 获取启用的发布器
        publishers = get_publishers()
        if not publishers:
            logger.warning("没有启用任何发布渠道！请在.env文件中配置发布渠道")
            return
        
        # 获取热门仓库
        repos = crawler.get_trending_repos()
        
        # 获取GitHub Trending URL
        trending_url = crawler.get_trending_url()
        
        # 生成文章标题
        language_text = crawler.get_language_text()
        start_date, end_date = crawler.get_date_range()
        title = f"{language_text} {crawler.get_report_type_text()}"
        
        # 发布文章
        article_urls = {'github': trending_url}  # 默认使用GitHub Trending URL
        webhook_publisher = None
        
        # 先发布到其他平台（带标题）
        article_with_title = generator.generate_article(
            repos,
            language=language_text,
            crawler=crawler,
            title=title
        )
        
        for publisher in publishers:
            if isinstance(publisher, WeChatWebhookPublisher):
                webhook_publisher = publisher
                continue
                
            try:
                url = publisher.publish(title, article_with_title)
                if url:
                    # 根据发布器类型存储URL
                    if isinstance(publisher, CSDNPublisher):
                        article_urls['csdn'] = url
                    elif isinstance(publisher, JuejinPublisher):
                        article_urls['juejin'] = url
                    elif isinstance(publisher, DevToPublisher):
                        article_urls['devto'] = url
                    elif isinstance(publisher, ConfluencePublisher):
                        article_urls['confluence'] = url
                    elif isinstance(publisher, YuquePublisher):
                        article_urls['yuque'] = url
                    elif isinstance(publisher, NotionPublisher):
                        article_urls['notion'] = url
            except Exception as e:
                logger.error(f"发布到{publisher.__class__.__name__}失败: {str(e)}")
                notifier.send_alert(e)
        
        # 最后发送到企业微信群（不带标题）
        if webhook_publisher:
            try:
                article_without_title = generator.generate_article(
                    repos,
                    language=language_text,
                    crawler=crawler
                )
                webhook_publisher.publish(title, article_without_title, article_urls)
            except Exception as e:
                logger.error(f"发送到企业微信群失败: {str(e)}")
                notifier.send_alert(e)
        
        logger.info("程序执行完成！")
        
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        notifier.send_alert(e)
        raise

if __name__ == '__main__':
    main() 