from atlassian import Confluence
from typing import Dict
import logging
from config.settings import CONFLUENCE_URL, CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN
from config.settings import CONFLUENCE_SPACE_KEY, CONFLUENCE_PARENT_PAGE_ID

class ConfluencePublisher:
    """
    Confluence文章发布器
    """
    
    def __init__(self):
        self.client = Confluence(
            url=CONFLUENCE_URL,
            username=CONFLUENCE_USERNAME,
            token=CONFLUENCE_API_TOKEN
        )
    
    def publish_article(self, article_data: Dict, space_key: str = CONFLUENCE_SPACE_KEY, parent_page_id: str = CONFLUENCE_PARENT_PAGE_ID) -> str:
        """
        发布文章到Confluence
        
        :param article_data: 文章数据，包含标题、内容等
        :param space_key: Confluence空间key
        :param parent_page_id: 父页面ID(可选)
        :return: 文章发布后的URL
        """
        try:
            # 为文章内容添加Markdown宏支持
            markdown_body = f'<ac:structured-macro ac:name="markdown"><ac:plain-text-body><![CDATA[{article_data.get("content", "")}]]></ac:plain-text-body></ac:structured-macro>';
            
            result = self.client.create_page(
                space=space_key,
                title=article_data.get("title", "GitHub技术趋势报告"),
                body=markdown_body,
                parent_id=parent_page_id
            )
            
            page_url = f"{self.client.url}/pages/viewpage.action?pageId={result['id']}"
            logging.info(f"Confluence文章发布成功，页面ID: {result['id']}, 文章URL: {page_url}")
            return page_url
            
        except Exception as e:
            logging.error(f"Confluence文章发布失败: {e}")
            return "#"