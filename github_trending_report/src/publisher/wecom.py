# -*- coding: utf-8 -*-
import os
import requests
from typing import Dict
import logging

# 企业微信配置
from config.settings import WECOM_WEBHOOK_URLS

class WeComPublisher:
    """
    企业微信文章发布器，通过机器人以卡片式消息推送文章到群聊
    """
    
    def __init__(self):
        if not WECOM_WEBHOOK_URLS:
            raise ValueError("企业微信Webhook URL列表未配置，请检查环境变量")
        self.webhook_urls = WECOM_WEBHOOK_URLS
    
    def publish_article(self, article_data: Dict) -> str:
        """
        发布文章到企业微信群聊
        
        :param article_data: 文章数据，包含标题、简介、链接等
        :return: 文章发布后的URL
        """
        failed_urls = []
        for webhook_url in self.webhook_urls:
            if not webhook_url.strip():
                continue
            try:
                title = article_data.get("title", "无标题文章")
                description = article_data.get("description", "暂无文章简介")
                article_url = article_data.get("url", "#")
                pic_url = article_data.get("pic_url", "#")
                
                payload = {
                    "msgtype": "news",
                    "news": {
                        "articles": [
                            {
                                "title": title,
                                "description": description,
                                "url": article_url,
                                "picurl": pic_url
                            }
                        ]
                    }
                }
                
                response = requests.post(webhook_url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                if result.get("errcode") != 0:
                    failed_urls.append(webhook_url)
                    logging.error(f"企业微信消息推送失败，URL: {webhook_url}, 错误信息: {result.get('errmsg')}")
            except Exception as e:
                failed_urls.append(webhook_url)
                logging.error(f"企业微信消息推送失败，URL: {webhook_url}, 错误信息: {str(e)}")
        
        if failed_urls:
            raise Exception(f"部分企业微信群消息推送失败，失败URL: {', '.join(failed_urls)}")
        return ""