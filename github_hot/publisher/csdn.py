from publisher import register_publisher
from publisher.base import ArticlePublisher
import os
import requests
import logging

@register_publisher('csdn')
class CSDNPublisher(ArticlePublisher):
    """CSDN发布器"""
    def __init__(self) -> None:
        self.username = os.getenv('CSDN_USERNAME')
        self.password = os.getenv('CSDN_PASSWORD')
        self.cookie = os.getenv('CSDN_COOKIE')
        if not all([self.username, self.password, self.cookie]):
            logging.error("CSDN配置未设置！请在.env文件中设置CSDN_USERNAME、CSDN_PASSWORD和CSDN_COOKIE")
            raise ValueError("CSDN配置未设置")
        self.headers = {
            'Cookie': self.cookie,
            'Content-Type': 'application/json'
        }
        logging.info("CSDN发布器初始化完成")

    def publish(self, title: str, content: str) -> str:
        """发布文章到CSDN
        Args:
            title: 文章标题
            content: 文章内容
        Returns:
            str: 文章URL
        """
        logging.info("开始发布文章到CSDN...")
        try:
            data = {
                "title": title,
                "content": content,
                "markdowncontent": content,
                "categories": "Python",
                "tags": "GitHub,Python,热门项目",
                "type": "original"
            }
            url = "https://mp.csdn.net/mp_blog/manage/article"
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code != 200:
                logging.error(f"发布文章到CSDN失败: {response.text}")
                raise Exception(f"发布文章到CSDN失败: {response.status_code}")
            article_url = response.json()['data']['url']
            logging.info(f"文章发布到CSDN成功，URL: {article_url}")
            return article_url
        except Exception as e:
            logging.error(f"发布文章到CSDN时发生错误: {str(e)}")
            raise 