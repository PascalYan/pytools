import logging

class FreeTranslator:
    """免费无需配置的翻译服务（基于 googletrans 包）"""
    def __init__(self):
        try:
            from googletrans import Translator
            self.translator = Translator()
            self.enabled = True
            logging.info("免费翻译服务（googletrans）初始化完成")
        except ImportError:
            logging.warning("未安装 googletrans 包，将跳过翻译功能。请运行 pip install googletrans==4.0.0-rc1")
            self.enabled = False

    def translate(self, text, from_lang='en', to_lang='zh-cn'):
        if not self.enabled or not text:
            return text
        try:
            result = self.translator.translate(text, src=from_lang, dest=to_lang)
            return result.text
        except Exception as e:
            logging.warning(f"免费翻译失败: {e}")
            return text 