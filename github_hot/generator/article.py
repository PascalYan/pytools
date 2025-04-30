import logging
from translate.free_translator import FreeTranslator

class ArticleGenerator:
    """文章生成器"""
    def __init__(self):
        self.translator = FreeTranslator()
        logging.info("文章生成器初始化完成")

    def translate_content(self, text):
        if not text:
            return ""
        translated = self.translator.translate(text)
        if not translated or translated == text:
            return text
        return f"{text}\n> {translated}"

    def generate_article(self, repos, language='Python', crawler=None, title=None):
        logging.info("开始生成文章...")
        if crawler:
            time_range = crawler.get_time_range_text()
            report_type = crawler.get_report_type_text()
        else:
            time_range = '过去7天内'
            report_type = '周报'
        md = f"# {title or ''}\n\n"
        md += f"本{report_type}为大家带来 GitHub 上最受欢迎的 {language} 项目，这些项目在{time_range}获得了最多的 stars。\n\n"
        md += "## 热门项目列表\n"
        for i, repo in enumerate(repos, 1):
            desc = self.translate_content(repo["description"])
            md += f"{i}. [{repo['name']}]({repo['url']}) - {desc}\n"
        md += "\n"
        md += "## 项目详情\n"
        for i, repo in enumerate(repos, 1):
            md += f"### {i}. {repo['name']}\n"
            md += f"- **描述**: {self.translate_content(repo['description'])}\n"
            md += f"- **星标数**: {repo['stars']}\n"
            md += f"- **Fork数**: {repo['forks']}\n"
            md += f"- **主要语言**: {repo['language']}\n"
            md += f"- **项目地址**: [{repo['url']}]({repo['url']})\n"
            details_data = repo.get('details', {})
            if details_data.get('readme'):
                md += f"- **项目简介**: {self.translate_content(details_data['readme'])}\n"
            if details_data.get('contributors'):
                contributors = ', '.join([f"[{c}](https://github.com/{c})" for c in details_data['contributors']])
                md += f"- **主要贡献者**: {contributors}\n"
            if details_data.get('updated_at'):
                md += f"- **最近更新**: {details_data['updated_at']}\n"
            if details_data.get('license'):
                md += f"- **许可证**: {details_data['license']}\n"
            if details_data.get('topics'):
                topics = ', '.join(details_data['topics'])
                md += f"- **主题标签**: {topics}\n"
            if details_data.get('homepage'):
                md += f"- **项目主页**: [{details_data['homepage']}]({details_data['homepage']})\n"
            if details_data.get('open_issues'):
                md += f"- **开放问题**: {details_data['open_issues']}\n"
            if details_data.get('watchers'):
                md += f"- **关注者**: {details_data['watchers']}\n"
            md += "\n"
        md += f"---\n数据统计时间：{time_range}\n"
        logging.info("文章生成完成")
        return md 