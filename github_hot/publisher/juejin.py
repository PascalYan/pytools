from publisher import register_publisher
from publisher.base import ArticlePublisher
import os
import requests
import logging

@register_publisher('juejin')
class JuejinPublisher(ArticlePublisher):
    """掘金发布器"""
    def __init__(self) -> None:
        self.user_id = os.getenv('JUEJIN_USER_ID')
        self.cookie = os.getenv('JUEJIN_COOKIE')
        if not all([self.user_id, self.cookie]):
            logging.error("掘金配置未设置！请在.env文件中设置JUEJIN_USER_ID和JUEJIN_COOKIE")
            raise ValueError("掘金配置未设置")
        self.headers = {
            'Cookie': self.cookie,
            'Content-Type': 'application/json'
        }
        logging.info("掘金发布器初始化完成")

    def publish(self, title: str, content: str) -> str:
        """发布文章到掘金
        Args:
            title: 文章标题
            content: 文章内容
        Returns:
            str: 文章URL
        """
        logging.info("开始发布文章到掘金...")
        try:
            data = {
                "title": title,
                "content": content,
                "category_id": "6809637769959178254",
                "tag_ids": ["6809640407484334093"],
                "link_url": "",
                "cover_image": "",
                "is_gfw": 0
            }
            url = "https://api.juejin.cn/content_api/v1/article/publish"
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code != 200:
                logging.error(f"发布文章到掘金失败: {response.text}")
                raise Exception(f"发布文章到掘金失败: {response.status_code}")
            article_url = f"https://juejin.cn/post/{response.json()['data']['article_id']}"
            logging.info(f"文章发布到掘金成功，URL: {article_url}")
            return article_url
        except Exception as e:
            logging.error(f"发布文章到掘金时发生错误: {str(e)}")
            raise 