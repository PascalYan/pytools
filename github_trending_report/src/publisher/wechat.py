from wechatpy import WeChatClient
from config.settings import WECHAT_APP_ID, WECHAT_APP_SECRET,WECHAT_PUBLISH_MODE, WECHAT_AUTHOR, WECHAT_THUMB_MEDIA_ID
from typing import Dict
import json
import os
import logging
import markdown

class WeChatPublisher:
    """
    微信公众号文章发布器
    """
    
    def __init__(self):
        self.client = WeChatClient(WECHAT_APP_ID, WECHAT_APP_SECRET)
    
    def markdown_to_html(self, markdown_content: str) -> str:
        """
        将Markdown内容转换为微信公众号支持的HTML格式
        
        :param markdown_content: Markdown格式的文章内容
        :return: 转换后的HTML内容
        """
        return markdown.markdown(markdown_content)
        
    def publish_article(self, article_data: Dict) -> bool:
        """
        发布文章到微信公众号
        
        :param article_data: 文章数据，包含标题、内容、封面图等
        :return: 发布是否成功
        """
        try:
            # 处理封面素材
            if WECHAT_THUMB_MEDIA_ID:
                result = {'media_id': WECHAT_THUMB_MEDIA_ID}
                logging.info(f"使用配置的封面素材ID: {result['media_id']}")
            else:
                # 上传封面素材
                cover_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "cover_image.png")
                if not os.path.exists(cover_path):
                    raise ValueError(f"封面图片路径不存在: {cover_path}")
                    
                try:
                    with open(cover_path, 'rb') as f:
                        result = self.client.material.add(
                            media_type='image',
                            media_file=f
                        )
                        logging.info(f"上传封面素材成功: {json.dumps(result)}")
                except Exception as e:
                    logging.error(f"上传封面素材失败: {str(e)}")
                    raise

            # 构造图文消息
            content = article_data.get("content", "")
            if content.startswith("#"):  # 简单检测是否为Markdown
                content = self.markdown_to_html(content)
                
            articles = [{
                "title": article_data.get("title", "GitHub技术趋势报告"),
                "content": content,
                "thumb_media_id": result['media_id'],
                "author": article_data.get("author", WECHAT_AUTHOR),
                "digest": article_data.get("digest", "最新GitHub技术趋势分析")
            }]
            
            # 创建草稿
            result = self.client.draft.add(articles=articles)
            
            # 如果是发布模式而非草稿，则发布草稿
            if WECHAT_PUBLISH_MODE != "draft":
                self.client.freepublish.submit(result['media_id'])
            
            logging.info(f"微信公众号文章发布成功: {json.dumps(result)}")
            return True
            
        except Exception as e:
            logging.error(f"微信公众号文章发布失败: {e}")
            return False