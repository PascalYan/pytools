from publisher import register_publisher
from publisher.base import ArticlePublisher
import os
import requests
import logging

@register_publisher('devto')
class DevToPublisher(ArticlePublisher):
    """Dev.to发布器"""
    def __init__(self) -> None:
        self.api_key = os.getenv('DEVTO_API_KEY')
        if not self.api_key:
            logging.error("Dev.to配置未设置！请在.env文件中设置DEVTO_API_KEY")
            raise ValueError("Dev.to配置未设置")
        self.headers = {
            'api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        logging.info("Dev.to发布器初始化完成")

    def publish(self, title: str, content: str) -> str:
        """发布文章到Dev.to
        Args:
            title: 文章标题
            content: 文章内容
        Returns:
            str: 文章URL
        """
        logging.info("开始发布文章到Dev.to...")
        try:
            data = {
                "article": {
                    "title": title,
                    "body_markdown": content,
                    "published": True,
                    "tags": ["python", "github", "trending"]
                }
            }
            url = "https://dev.to/api/articles"
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code not in [200, 201]:
                logging.error(f"发布文章到Dev.to失败: {response.text}")
                raise Exception(f"发布文章到Dev.to失败: {response.status_code}")
            article_url = response.json()['url']
            logging.info(f"文章发布到Dev.to成功，URL: {article_url}")
            return article_url
        except Exception as e:
            logging.error(f"发布文章到Dev.to时发生错误: {str(e)}")
            raise 