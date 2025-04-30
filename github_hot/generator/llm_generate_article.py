import os
from typing import List, Dict
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
# 可扩展：from langchain_community.chat_models import QianWen, WenXin, ...

def llm_generate_article(
    repos: List[Dict],
    language: str,
    report_type: str,
    time_range: str,
    provider: str = None
) -> str:
    """
    用大模型生成文章内容，支持多种 LLM 提供商
    Args:
        repos: 热门项目列表（dict，含name/desc/url/stars等）
        language: 语言
        report_type: 日报/周报/月报
        time_range: 时间范围
        provider: LLM提供商（如 openai、wenxin、qwen 等）
    Returns:
        str: 生成的 Markdown 文章
    """
    if provider is None:
        provider = os.getenv('LLM_PROVIDER', 'openai')
    repo_list_md = ""
    for i, repo in enumerate(repos, 1):
        repo_list_md += f"{i}. [{repo['name']}]({repo['url']}) - {repo['description']} (Stars: {repo['stars']})\n"
    prompt = f"""
你是一名专业的技术内容编辑，擅长用简洁、客观、易读的语言为开发者解读技术趋势。

请根据下方提供的 GitHub {language} 项目一周热门榜单，撰写一篇"本周技术热点"专栏文章，要求如下：

- 文章风格：专业、简明、客观，适合技术社区/公众号专栏发布。
- 结构建议：
  1. 简要开篇（1-2句话，点明本周技术趋势/亮点）
  2. 热门项目列表（用有序列表，项目名+一句话简评/亮点）
  3. 重点项目解读（挑选2-3个最有代表性的项目，简要分析其创新点、应用场景或社区反响）
  4. 结语（鼓励读者关注、参与或持续跟进相关技术）

- 输出格式：Markdown，注意排版美观，避免冗余和重复。

以下是本周最受关注的 GitHub {language} 项目（按 stars 排序）：

{repo_list_md}

请生成完整文章内容。
"""
    if provider == 'openai':
        llm = ChatOpenAI(model=os.getenv('OPENAI_MODEL', 'gpt-4'), temperature=0.7)
        response = llm([HumanMessage(content=prompt)])
        return response.content
    elif provider == 'deepseek':
        llm = ChatOpenAI(
            model=os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
            temperature=0.7,
            openai_api_base=os.getenv('DEEPSEEK_API_BASE'),
            openai_api_key=os.getenv('DEEPSEEK_API_KEY')
        )
        response = llm([HumanMessage(content=prompt)])
        return response.content
    elif provider in ['qwen', 'qianwen', 'ali']:
        from langchain_community.chat_models import QianWen
        llm = QianWen(
            model=os.getenv('QWEN_MODEL', 'qwen-turbo'),
            dashscope_api_key=os.getenv('QWEN_API_KEY')
        )
        response = llm([HumanMessage(content=prompt)])
        return response.content
    raise NotImplementedError(f"暂不支持的 LLM provider: {provider}") 