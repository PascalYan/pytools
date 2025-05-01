import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

########################################
# 基础目录配置
########################################
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"  # 数据存储目录
DATA_DIR.mkdir(exist_ok=True)

########################################
# GitHub API 相关配置
########################################
GITHUB_TRENDING_URL = "https://github.com/trending"  # GitHub趋势页面URL
GITHUB_API_URL = "https://api.github.com"  # GitHub API基础URL
GITHUB_REQUEST_TIMEOUT = 10  # API请求超时时间(秒)
GITHUB_TRENDING_SINCE = "weekly"  # 趋势时间范围: daily(日)/weekly(周)/monthly(月)
GITHUB_TRENDING_LANGUAGE = ""  # 趋势语言筛选: 空字符串表示所有语言

########################################
# AI 服务配置
########################################
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # DeepSeek API密钥
DEEPSEEK_API_URL = "https://api.deepseek.com/v1"  # DeepSeek API地址
DEEPSEEK_MODEL = "deepseek-chat"  # 使用的DeepSeek模型

########################################
# 发布平台配置
########################################

# 微信公众号配置
WECHAT_APP_ID = os.getenv("WECHAT_APP_ID")  # 微信公众号AppID
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET")  # 微信公众号AppSecret
WECHAT_PUBLISH_MODE = "draft" # 发布模式: draft(草稿)/publish(正式)
WECHAT_AUTHOR="码农AI助手"
WECHAT_THUMB_MEDIA_ID = os.getenv("WECHAT_THUMB_MEDIA_ID")  # 微信公众号封面素材ID，避免每次都要上传一个封面图片

# Confluence配置
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")  # Confluence实例URL
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")  # Confluence用户名
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")  # Confluence API令牌

# 文章类型与发布渠道映射关系
ARTICLE_CHANNEL_MAPPING = {
    # "NEWS_REPORT_TEMPLATE": ["wechat","confluence"],  # 新闻报告模板发布渠道
    # "TECH_ANALYSIS_TEMPLATE": ["confluence"]  # 技术分析模板发布渠道
    "WEEKLY_TREADING_WECHAT": ["wechat"]  # 技术分析模板发布渠道
}