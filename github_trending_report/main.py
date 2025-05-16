import json
import logging
from datetime import datetime
from pathlib import Path

from src.crawler.github_trending import fetch_trending_repos
from src.generator.article_generator import ArticleGenerator
from src.publisher.wechat import WeChatPublisher
from src.publisher.confluence import ConfluencePublisher
from src.publisher.wecom import WeComPublisher
from config.settings import DATA_DIR

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    主流程：爬取GitHub趋势项目 -> 生成文章 -> 发布到各平台
    """
    logger.info("开始GitHub技术趋势报告生成流程...")
    
    # 1. 爬取GitHub趋势项目
    logger.info("正在爬取GitHub趋势项目...")
    from config.settings import GITHUB_TRENDING_SINCE, GITHUB_TRENDING_LANGUAGE
    crawler_content = fetch_trending_repos(language=GITHUB_TRENDING_LANGUAGE, since=GITHUB_TRENDING_SINCE)
    
    if not crawler_content:
        logger.warning("未获取到趋势项目数据，流程终止")
        return
    
    
    # 2. 生成所有需要的文章
    articles = {}
    from config.settings import ARTICLE_CHANNEL_MAPPING
    today = datetime.now().strftime("%Y%m%d")
    
    # 获取所有需要生成的文章类型（去重）
    required_article_types = set(ARTICLE_CHANNEL_MAPPING.keys())
    
    logger.info(f"需要生成的文章类型: {', '.join(required_article_types)}")
    generator = ArticleGenerator()
    
    # 检查并生成文章
    for article_prompt_template_name in required_article_types:
        article_file = DATA_DIR / f"{today}_{GITHUB_TRENDING_SINCE}_{article_prompt_template_name}.text"
        
        # 如果文章已存在则跳过生成
        if article_file.exists():
            logger.info(f"文章{article_prompt_template_name}已存在，跳过生成")
            with open(article_file, "r", encoding="utf-8") as f:
                articles[article_prompt_template_name] = f.read()
            continue
            
        # 生成新文章
        logger.info(f"生成文章{article_prompt_template_name}...")
        articles.update(generator.generate_article(article_prompt_template_name, trending_projects=crawler_content))
        
        # 保存生成的文章
        logger.info(f"生成文章{article_prompt_template_name}生成完成，保存文章...")
        with open(article_file, "w", encoding="utf-8") as f:
            f.write(articles[article_prompt_template_name])
    
    # 3. 发布文章
    logger.info("所有文章生成完成，正在发布文章到各平台...")
    article_urls = {}
    
    # 按文章类型和渠道发布
    for article_prompt_template_name, channels in ARTICLE_CHANNEL_MAPPING.items(): 
        if article_prompt_template_name not in articles:
            logger.warning(f"文章类型{article_prompt_template_name}未生成，跳过发布")
            continue
            
        logger.info(f"开始发布{article_prompt_template_name}到{', '.join(channels)}...")
        article_urls[article_prompt_template_name] = {}
        
        for channel in channels:
            logger.info(f"正在发布{article_prompt_template_name}文章到{channel}平台...")
            
            try:
                if channel == "wechat":
                    # 发布到微信公众号
                    wechat_publisher = WeChatPublisher()
                    wechat_data = {
                        "title": f"每{'日' if GITHUB_TRENDING_SINCE == 'daily' else '周' if GITHUB_TRENDING_SINCE == 'weekly' else '月'}GitHub技术趋势({today}期)",
                        "content": articles[article_prompt_template_name],
                        # "digest": "每周精选GitHub热门项目技术分析"，不传，微信自动截取54个字作为摘要介绍
                    }
                    article_url = wechat_publisher.publish_article(wechat_data)
                    article_urls[article_prompt_template_name][channel] = article_url
                elif channel == "confluence":
                    # 发布到Confluence
                    confluence_publisher = ConfluencePublisher()
                    confluence_data = {
                        "title": f"每{'日' if GITHUB_TRENDING_SINCE == 'daily' else '周' if GITHUB_TRENDING_SINCE == 'weekly' else '月'}GitHub技术趋势({today}期)",
                        "content": articles[article_prompt_template_name]
                    }
                    article_url = confluence_publisher.publish_article(confluence_data)
                    article_urls[article_prompt_template_name][channel] = article_url
                elif channel == "wecom":
                    # 发布到企业微信
                    enterprise_wechat_publisher = WeComPublisher()
                    # ！！！TODO这里需要自行修改获取其他渠道的文章地址, 这里使用confluence的地址作为企业微信的文章地址
                    article_link_url = article_urls[article_prompt_template_name]["confluence"]
                    if not article_link_url or article_link_url == "#":
                        logger.warning(f"文章{article_prompt_template_name}在Confluence平台未发布或无法获取文章链接，跳过企业微信发布，请确认后再发布")
                        continue
                    # 生成企业微信卡片消息内容
                    enterprise_wechat_data = {
                        "title": f"每{'日' if GITHUB_TRENDING_SINCE == 'daily' else '周' if GITHUB_TRENDING_SINCE == 'weekly' else '月'}GitHub技术趋势({today}期)",
                        "description":  articles[article_prompt_template_name],
                        "url": article_link_url,
                        "pic_url": "https://p3-flow-imagex-sign.byteimg.com/ocean-cloud-tos/image_skill/3a16d434-f260-43f6-b0e1-c52d444befa7_1747378622636380176_origin~tplv-a9rns2rl98-image-dark-watermark.png?rk3s=b14c611d&x-expires=1778914622&x-signature=ezzVk2TSTjr%2FSrfx4wTuP9JoWME%3D"
                    }
                    enterprise_wechat_publisher.publish_article(enterprise_wechat_data)
                    article_urls[article_prompt_template_name][channel] = "#" # 企业微信没用文章地址，这里使用#代替

            except Exception as e:
                logger.error(f"发布{article_prompt_template_name}到{channel}失败: {str(e)}")
                article_urls[article_prompt_template_name][channel] = "#"

    logger.info("GitHub技术趋势报告生成流程完成!")


if __name__ == "__main__":
    main()