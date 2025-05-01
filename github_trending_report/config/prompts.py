from langchain.prompts import PromptTemplate



# 技术分析文章模板
TECH_ANALYSIS_TEMPLATE = PromptTemplate(
    input_variables=["trending_projects"],
    template="""作为技术专家，请分析以下GitHub热门项目：\n{trending_projects}\n\n，结合互联网搜索信息，撰写一篇专业的技术分析文章，包含：\n1. 项目技术栈分析\n2. 创新点解读\n3. 行业应用场景\n4. 未来发展预测\n"""
)

# 新闻简报模板
NEWS_REPORT_TEMPLATE = PromptTemplate(
    input_variables=["trending_projects"],
    template="""根据以下GitHub热门项目：\n{trending_projects}\n\n撰写一篇技术新闻简报，要求：\n1. 简明扼要\n2. 突出关键技术创新\n3. 包含项目链接\n4. 适合社交媒体传播\n"""
)

# 教程风格模板
TUTORIAL_TEMPLATE = PromptTemplate(
    input_variables=["trending_projects"],
    template="""基于这些热门项目：\n{trending_projects}\n\n创作一篇实战教程，包含：\n1. 环境搭建步骤\n2. 核心功能实现\n3. 代码示例\n4. 常见问题解答\n"""
)

# 公众号每周热点趋势专栏
WEEKLY_TREADING_WECHAT = PromptTemplate(
    input_variables=["trending_projects"],
    template="""
你是一个世界级技术视野的技术专家，百万粉丝级的技术文章作者，旨在为中国国内普及每周全球热点技术趋势。请根据以下GitHub weekly Trending项目列表，生成一篇适合微信公众号「每周Github技术趋势」专栏的周更新文章。
GitHub weekly Trending项目列表：\n{trending_projects}\n\n

文章内容要求：
文章结构要求：严格按照 “固定导语→项目分类介绍→趋势洞察→开发者建议→结尾引导” 顺序展开，每个板块设置醒目标题（标题文字17号字，白字加粗，居中，浅蓝色背景），固定导语和结尾引导不要标题，项目分类介绍需要总结归类为几个标题。

1、固定导语（不要标题）内容：“GitHub Trends, Future Unfurls！本周GitHub又有哪些神仙项目霸榜热门？「码了个啥｜每周GitHub技术趋势」继续为您解读。”，接着总结内容概览：用 1-2段话总结本周核心内容，提炼3个关键词。

2、项目分类介绍：将项目列表总结归类为几个高度抽象标题，每个分类标题下每个项目按以下模板编写：
项目标题（16号字，浅蓝色加粗），格式为「项目名称：一句话亮点」。
第一行：本周stars数与总stars数，以k为单位，固定格式：「Star⭐️:本周 xxk｜总xxk」，15号字。
第二行开始为项目介绍内容，描述项目的基本功能，介绍项目原理，重点介绍技术的突破性、前瞻性等，或项目的应用前景、应用案例与价值等，使用通俗比喻解释技术难点，针对存在伦理或安全等争议的内容，需从正反等多维度分析重点进行描述，引爆文章话题。
最后一段为项目地址，格式为「项目地址：项目地址URL」，项目地址URL另起一行。

3、趋势洞察：结合国内外相关信息与讨论话题进行，从多维度对本周的项目进行深度分析与总结，发挥全球技术视野，需要具有前瞻性、引领性、技术洞见性。

4、开发者建议：针对开发者给出应用或学习的建议与路径，跟上技术趋势。

5、结尾引导内容（不需要标题），文章结尾设置数个开放式问题与争议话题，引导评论区关注留言交流。不要额外添加其他预告、奖励等风险性内容。

文章整体要求：
语言风格：采用「专业术语 + 网络热梗」的行文风格。
格式规范：
全文使用微信公众号文章所支持的HTML标签严格排版，标题17号字，正文16号字，段落间距 1.5 倍，重点句子、关键词用<strong>加粗。
代码示例使用<pre><code class="language-xxx">标签，添加语法高亮。
文章长度控制在2000～5000字。
输出去掉非法字符，保证HTML的正确性。

"""
)