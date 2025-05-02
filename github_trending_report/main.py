import json
import logging
from datetime import datetime
from pathlib import Path

from src.crawler.github_trending import fetch_trending_repos
from src.generator.article_generator import ArticleGenerator
from src.publisher.wechat import WeChatPublisher
from src.publisher.confluence import ConfluencePublisher
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
    trending_repos = fetch_trending_repos(language=GITHUB_TRENDING_LANGUAGE, since=GITHUB_TRENDING_SINCE)
    
    if not trending_repos:
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
    for article_type in required_article_types:
        article_file = DATA_DIR / f"{today}_{article_type}.text"
        
        # 如果文章已存在则跳过生成
        if article_file.exists():
            logger.info(f"文章{article_type}已存在，跳过生成")
            with open(article_file, "r", encoding="utf-8") as f:
                articles[article_type] = f.read()
            continue
            
        # 生成新文章
        logger.info(f"生成文章{article_type}...")
        articles.update(generator.generate_article(trending_repos, article_type))
        
        # 保存生成的文章
        logger.info(f"生成文章{article_type}生成完成，保存文章...")
        with open(article_file, "w", encoding="utf-8") as f:
            f.write(articles[article_type])
    
    # 3. 发布文章
    logger.info("所有文章生成完成，正在发布文章到各平台...")
    
    # 按文章类型和渠道发布
    for article_type, channels in ARTICLE_CHANNEL_MAPPING.items():
        if article_type not in articles:
            logger.warning(f"文章类型{article_type}未生成，跳过发布")
            continue
            
        logger.info(f"开始发布{article_type}到{', '.join(channels)}...")
        
        for channel in channels:
            logger.info(f"正在发布{article_type}文章{channel}平台...")
               
            try:
                if channel == "wechat":
                    # 发布到微微信公众号
                    wechat_publisher = WeChatPublisher()
                    wechat_data = {
                        "title": f"每{'日' if GITHUB_TRENDING_SINCE == 'daily' else '周' if GITHUB_TRENDING_SINCE == 'weekly' else '月'}GitHub技术趋势({today}期)",
                        "content": articles[article_type],
                        # "digest": "每周精选GitHub热门项目技术分析"，不传，微信自动截取54个字作为摘要介绍
                    }
                    wechat_publisher.publish_article(wechat_data)
                elif channel == "confluence":
                    # 发布到Confluence
                    confluence_publisher = ConfluencePublisher()
                    confluence_data = {
                        "title": f"GitHub技术趋势分析({today})",
                        "content": articles[article_type]
                    }
                    confluence_publisher.publish_article(confluence_data, space_key="TECH")
        
            except Exception as e:
                logger.error(f"发布{article_type}到{channel}失败: {str(e)}")
    
    logger.info("GitHub技术趋势报告生成流程完成!")


if __name__ == "__main__":
    main()