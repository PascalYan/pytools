from publisher import register_publisher
from publisher.base import ArticlePublisher
import os
import requests
import logging

@register_publisher('yuque')
class YuquePublisher(ArticlePublisher):
    """语雀发布器"""
    def __init__(self) -> None:
        self.token = os.getenv('YUQUE_TOKEN')
        self.namespace = os.getenv('YUQUE_NAMESPACE')
        self.slug = os.getenv('YUQUE_SLUG')
        if not all([self.token, self.namespace, self.slug]):
            logging.error("语雀配置未设置！请在.env文件中设置YUQUE_TOKEN、YUQUE_NAMESPACE和YUQUE_SLUG")
            raise ValueError("语雀配置未设置")
        self.headers = {
            'X-Auth-Token': self.token,
            'Content-Type': 'application/json'
        }
        logging.info("语雀发布器初始化完成")

    def publish(self, title: str, content: str) -> str:
        """发布文章到语雀
        Args:
            title: 文章标题
            content: 文章内容
        Returns:
            str: 文章URL
        """
        logging.info("开始发布文章到语雀...")
        try:
            data = {
                "title": title,
                "body": content,
                "format": "markdown",
                "slug": self.slug
            }
            url = f"https://www.yuque.com/api/v2/repos/{self.namespace}/docs"
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code not in [200, 201]:
                logging.error(f"发布文章到语雀失败: {response.text}")
                raise Exception(f"发布文章到语雀失败: {response.status_code}")
            article_url = response.json()['data']['url']
            logging.info(f"文章发布到语雀成功，URL: {article_url}")
            return article_url
        except Exception as e:
            logging.error(f"发布文章到语雀时发生错误: {str(e)}")
            raise 