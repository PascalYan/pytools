import logging
from typing import List, Dict
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_MODEL, DEEPSEEK_API_URL
import config.prompts as prompts
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

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
            openai_api_base=DEEPSEEK_API_URL,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
        self.logger.debug("ArticleGenerator初始化完成")
    
    def generate_article(self, template_name: str, **kwargs) -> Dict[str, str]:
        """
        根据模板名称生成文章
        
        :param template_name: 提示词模板名称
        :param kwargs: 任意关键字参数，用于填充提示词模板
        :return: 包含文章类型和内容的字典
        """
        self.logger.info(f"开始生成文章，模板: {template_name}")

        try:
            self.logger.debug(f"尝试获取模板: {template_name}")
            template = getattr(prompts, template_name)
        except AttributeError as e:
            self.logger.error(f"模板获取失败: {str(e)}")
            raise ValueError(f"未知的模板名称: {template_name}")

        try:
            self.logger.info(f"使用LLM生成文章内容，模板: {template_name}")
            class LoggingCallbackHandler(StreamingStdOutCallbackHandler):
                def on_llm_new_token(self, token: str, **kwargs) -> None:
                    self.logger.info(f"接收到流式回答新令牌: {token}")
            
            chain = LLMChain(llm=self.llm, prompt=template, callbacks=[LoggingCallbackHandler()])
            content = chain.run(**kwargs)
            
            if not content:
                self.logger.warning("LLM返回空内容")
                return {template_name: ""}
                
            self.logger.debug(f"文章生成成功，模板: {template_name}")
            return {template_name: content}
            
        except Exception as e:
            self.logger.error(f"文章生成过程中发生错误: {str(e)}")
            raise