from publisher import register_publisher
from publisher.base import ArticlePublisher
import os
import requests
import logging
import json
from wechatpy import WeChatClient

@register_publisher('wechat_mp')
class WeChatMPPublisher(ArticlePublisher):
    """微信公众号发布器"""
    def __init__(self) -> None:
        self.app_id = os.getenv('WECHAT_APP_ID')
        self.app_secret = os.getenv('WECHAT_APP_SECRET')
        self.direct_publish = os.getenv('WECHAT_DIRECT_PUBLISH', 'false').lower() == 'true'
        if not all([self.app_id, self.app_secret]):
            logging.error("微信公众号配置未设置！请在.env文件中设置WECHAT_APP_ID和WECHAT_APP_SECRET")
            raise ValueError("微信公众号配置未设置")
        self.client = WeChatClient(self.app_id, self.app_secret)
        logging.info(f"微信公众号发布器初始化完成，{'直接发布' if self.direct_publish else '保存为草稿'}")

    def publish(self, title: str, content: str) -> str:
        """发布文章到微信公众号
        Args:
            title: 文章标题
            content: 文章内容
        Returns:
            str: 发布结果的 media_id 或 None
        """
        logging.info("开始发布文章到微信公众号...")
        try:
            cover_url = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            response = requests.get(cover_url)
            if response.status_code != 200:
                raise Exception("下载封面图片失败")
            with open('temp_cover.jpg', 'wb') as f:
                f.write(response.content)
            with open('temp_cover.jpg', 'rb') as f:
                thumb = self.client.material.add('image', f)
            os.remove('temp_cover.jpg')
            articles = [{
                'title': title,
                'content': content,
                'thumb_media_id': thumb['media_id'],
                'need_open_comment': 0,
                'only_fans_can_comment': 0,
                'show_cover_pic': 1,
                'digest': content.split('\n')[0][:120],
                'content_source_url': 'https://github.com/trending'
            }]
            if self.direct_publish:
                result = self.client.material.add_articles(articles)
                logging.info("文章已直接发布")
            else:
                url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self.client.access_token}"
                data = {"articles": articles}
                json_str = json.dumps(data, ensure_ascii=False).encode('utf-8')
                headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                    'Accept-Charset': 'utf-8'
                }
                response = requests.post(url, data=json_str, headers=headers)
                result = response.json()
                if 'media_id' in result:
                    logging.info(f"文章已保存为草稿，media_id: {result.get('media_id')}")
                else:
                    error_msg = result.get('errmsg', '未知错误')
                    logging.error(f"保存草稿失败: {error_msg}")
                    raise Exception(f"保存草稿失败: {error_msg}")
            return result.get('media_id')
        except Exception as e:
            logging.error(f"发布文章到微信公众号失败: {str(e)}")
            raise 