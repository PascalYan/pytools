import logging
import os
from config import *
from crawler.github import GitHubHotCrawler
from generator.article import ArticleGenerator
from generator.llm_generate_article import llm_generate_article
from notifier.wechat import WeChatNotifier
from publisher.wechat_mp import WeChatMPPublisher
from publisher.csdn import CSDNPublisher
from publisher.wechat_webhook import WeChatWebhookPublisher
from publisher.juejin import JuejinPublisher
from publisher.devto import DevToPublisher
from publisher.yuque import YuquePublisher
from publisher.notion import NotionPublisher
from publisher.local_file import LocalFilePublisher
# from publisher.base import ArticlePublisher
# TODO: 导入各个发布渠道

def get_publishers():
    publishers = []
    if os.getenv('ENABLE_WECHAT_MP', 'false').lower() == 'true':
        publishers.append(('wechat_mp', WeChatMPPublisher()))
    if os.getenv('ENABLE_CSDN', 'false').lower() == 'true':
        publishers.append(('csdn', CSDNPublisher()))
    if os.getenv('ENABLE_JUEJIN', 'false').lower() == 'true':
        publishers.append(('juejin', JuejinPublisher()))
    if os.getenv('ENABLE_DEVTO', 'false').lower() == 'true':
        publishers.append(('devto', DevToPublisher()))
    if os.getenv('ENABLE_YUQUE', 'false').lower() == 'true':
        publishers.append(('yuque', YuquePublisher()))
    if os.getenv('ENABLE_NOTION', 'false').lower() == 'true':
        publishers.append(('notion', NotionPublisher()))
    if os.getenv('ENABLE_LOCAL_FILE', 'false').lower() == 'true':
        publishers.append(('local_file', LocalFilePublisher()))
    return publishers

def should_use_llm() -> bool:
    """判断是否启用大模型生成文章"""
    provider = os.getenv('LLM_PROVIDER')
    enable_llm = os.getenv('ENABLE_LLM_GENERATE', 'false').lower() == 'true'
    if not enable_llm or not provider:
        return False
    if provider == 'openai' and os.getenv('OPENAI_API_KEY'):
        return True
    # 可扩展其它模型的判断
    return False

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info("程序开始执行...")

    notifier = WeChatNotifier()
    article_urls = {}

    try:
        crawler = GitHubHotCrawler()
        repos = crawler.get_trending_repos()
        title = f"{crawler.get_language_text()} {crawler.get_report_type_text()}"
        if should_use_llm():
            logger.info("使用大模型生成文章...")
            article = llm_generate_article(
                repos,
                language=crawler.get_language_text(),
                report_type=crawler.get_report_type_text(),
                time_range=crawler.get_time_range_text(),
                provider=os.getenv('LLM_PROVIDER', 'openai')
            )
        else:
            logger.info("使用本地模板生成文章...")
            article = ArticleGenerator().generate_article(
                repos,
                language=crawler.get_language_text(),
                crawler=crawler,
                title=title
            )
        publishers = get_publishers()
        for key, publisher in publishers:
            try:
                url = publisher.publish(title, article)
                if url:
                    article_urls[key] = url
                logger.info(f"发布到 {key} 成功: {url}")
            except Exception as e:
                logger.error(f"发布到 {key} 失败: {e}")
                notifier.send_alert(e)
        # 企业微信群机器人最后发，带上所有渠道的 URL
        if os.getenv('ENABLE_WECHAT_WEBHOOK', 'false').lower() == 'true':
            try:
                wechat_webhook_publisher = WeChatWebhookPublisher()
                wechat_webhook_publisher.publish(title, article, article_urls)
                logger.info("企业微信群机器人推送成功")
            except Exception as e:
                logger.error(f"企业微信群机器人推送失败: {e}")
                notifier.send_alert(e)
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        notifier.send_alert(e)
        raise

if __name__ == '__main__':
    main() 