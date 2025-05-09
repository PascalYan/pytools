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

你是一位拥有世界级技术视野的资深技术专家，同时也是百万粉丝级别的技术文章作者，专注于为中国开发者解读全球技术趋势。请根据提供的GitHub每周趋势项目列表，创作一篇适合微信公众号发布的「每周Github技术趋势」专栏文章。
每周趋势项目列表（文章内容需要包括所有项目）：\n{trending_projects}\n\n

## 文章要求

### 内容结构
严格按以下顺序组织内容：
0. 文章标题，提炼本周文章核心内容标题，具有阅读引导性。

1. 【固定导语】(无标题)
   - 开场白：<p style="font-size: 16px;>"GitHub Trends，Future Unfurls！本周GitHub又有哪些神仙项目霸榜热门？「每周GitHub技术趋势」继续为您解读。"</p>
   - 内容概览：<p style="font-size: 16px;>（首行不缩进）1-2段总结本周核心内容，提炼3-5个关键词</p>
   - <br>末尾空一行

2. 【项目分类介绍】
   - 将项目归类为3-5个高度抽象的类别(不可归类的可以统一归到"其它上榜项目")
   - 文章内容应当包含每周趋势项目列表所有项目
   - 每个类别标题<p style="color:#ffffff;font-weight:bold;font-size: 17px;text-align: center"><span style="background-color:#3daad6">项目名称：（中文）一句话亮点</span></p>
   - <br>每个类别标题后空一行
   - 每个项目按以下模板编写：
     ```
     <p style="color:#3daad6;font-weight:bold;font-size: 16px;">项目名称：一句话亮点</p>
     <p style="color:#888888; font-size: 15px;">star⭐️: 本周 xxk｜总 xxk</p>
     <p style="color:#888888; font-size: 15px;>项目地址：<br>URL</p>
     <p style="font-size: 16px;>[项目详细介绍]，（首行不缩进）文章的核心内容，描述项目的基本功能，结合项目相关国内外讨论信息，介绍项目原理，重点介绍技术的突破性、前瞻性等，或项目的应用前景、应用案例与价值等，使用通俗比喻解释技术难点，针对存在伦理或安全等争议的内容，需从正反等多维度分析重点进行描述，引爆文章话题。</p>
     <br>末尾空一行
     ```

3. 【本周趋势洞察】
   - 标题<p style="color:#ffffff;font-weight:bold;font-size: 17px;text-align: center"><span style="background-color:#3daad6">本周趋势洞察</span></p>
   - <br>标题后空一行
   - 内容<p style="font-size: 16px;>（首行不缩进）文章的核心内容，输出1000字以上本周趋势洞察，结合国内外相关信息进行深度分析，展现全球技术视野和前瞻性见解，需要具有前瞻性、引领性、专业性、准确性。</p>
   - <br>末尾空一行
   
4. 【开发者建议】
   - 标题<p style="color:#ffffff;font-weight:bold;font-size: 17px;text-align: center"><span style="background-color:#3daad6">开发者建议</span></p>
   - <br>标题后空一行
   - 内容<p style="font-size: 16px;>（首行不缩进）提供具体应用和学习建议，如何跟上本周技术趋势</p>
   - <br>末尾空一行

5. 【结尾引导】
   - 内容<p style="font-size: 16px;>（首行不缩进）一段话设置2-3个开放式问题引导讨论，引爆话题，合理引导关注评论交流</p>
   - <br>空一行
   - 固定声明 <p style="color:#888888; font-size: 12px;>作者声明：「每周GitHub技术趋势」一般每周五晚上更新，旨在为开发者速递每周技术热点趋势，内容来源于Github Weekly Trending，综合相关项目互联网热门信息及AI整理，请注意鉴别。</p>
   - <br>末尾空一行

6、【参考文章】
   - 标题<p style="font-weight:bold;font-size: 16px;text-align: left">参考文章：</p>
   - 本篇文章的10个以内参考文章、讨论地址列表<p style="font-size: 15px;><strong>相关参考文章标题</strong>：<br>文章URL</p>

### 格式规范
- 使用微信公众号支持的HTML格式
- 首行不缩进
- 正文未特殊设置时，通常16号字
- 重点内容用<strong>加粗</strong>
- 代码示例使用<pre><code class="language-xxx">标签
- 全文2000-5000字左右

### 语言风格
专业性与趣味性结合：
- 使用准确的技术术语
- 适当融入网络流行语
- 复杂概念用生动比喻解释
- 保持严谨但不失活泼

### 特别要求
- 对争议性技术需正反分析
- 突出技术突破性和应用前景
- 去除非法字符确保微信兼容性
- 不使用微信风险内容(如下期预测、奖励等)

## 输出格式
请输出完整HTML文档，包含以下元素：
- 适当的<div>容器
- 精心设计的标题样式
- 响应式排版
- 优化过的超链接样式
- 移动端友好的布局
- 去掉首尾其他大模型输出的html生成说明等文章无关内容，结果可直接用于微信公众号自动发表

"""
)