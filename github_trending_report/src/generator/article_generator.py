import logging
from typing import List, Dict
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_MODEL, DEEPSEEK_API_URL
import config.prompts as prompts

class ArticleGenerator:
    """
    技术文章生成器，根据提示词模板动态生成文章
    """

class ArticleGenerator:
    """
    技术文章生成器，根据提示词模板动态生成文章
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm = ChatOpenAI(
            openai_api_key=DEEPSEEK_API_KEY,
            model_name=DEEPSEEK_MODEL,
            temperature=0.7,
            openai_api_base=DEEPSEEK_API_URL
        )
        self.logger.debug("ArticleGenerator初始化完成")
    
    def generate_article(self, trending_projects: List[Dict], template_name: str) -> Dict[str, str]:
        """
        根据模板名称生成文章
        
        :param template_name: 提示词模板名称
        :param trending_projects: GitHub热门项目列表
        :return: 包含文章类型和内容的字典
        """
        self.logger.info(f"开始生成文章，模板: {template_name}")
        
        # 验证输入参数
        if not trending_projects:
            self.logger.warning("传入的项目列表为空")
            return {template_name: ""}
            
        try:
            self.logger.debug(f"尝试获取模板: {template_name}")
            template = getattr(prompts, template_name)
        except AttributeError as e:
            self.logger.error(f"模板获取失败: {str(e)}")
            raise ValueError(f"未知的模板名称: {template_name}")
            
        try:
            self.logger.info(f"使用LLM生成文章内容，模板: {template_name}")
            chain = LLMChain(llm=self.llm, prompt=template)
            content = chain.run(trending_projects=trending_projects)
            
            if not content:
                self.logger.warning("LLM返回空内容")
                return {template_name: ""}
                
            self.logger.debug(f"文章生成成功，模板: {template_name}")
            return {template_name: content}
            
        except Exception as e:
            self.logger.error(f"文章生成过程中发生错误: {str(e)}")
            raise