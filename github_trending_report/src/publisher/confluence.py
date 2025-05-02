from atlassian import Confluence
from typing import Dict
import logging
from config.settings import CONFLUENCE_URL, CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN

class ConfluencePublisher:
    """
    Confluence文章发布器
    """
    
    def __init__(self):
        self.client = Confluence(
            url=CONFLUENCE_URL,
            username=CONFLUENCE_USERNAME,
            password=CONFLUENCE_API_TOKEN
        )
    
    def publish_article(self, article_data: Dict, space_key: str, parent_page_id: str = None) -> bool:
        """
        发布文章到Confluence
        
        :param article_data: 文章数据，包含标题、内容等
        :param space_key: Confluence空间key
        :param parent_page_id: 父页面ID(可选)
        :return: 发布是否成功
        """
        try:
            result = self.client.create_page(
                space=space_key,
                title=article_data.get("title", "GitHub技术趋势报告"),
                body=article_data.get("content", ""),
                parent_id=parent_page_id
            )
            
            logging.info(f"Confluence文章发布成功，页面ID: {result['id']}")
            return True
            
        except Exception as e:
            logging.error(f"Confluence文章发布失败: {e}")
            return False