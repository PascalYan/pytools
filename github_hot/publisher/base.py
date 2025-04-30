from abc import ABC, abstractmethod

class ArticlePublisher(ABC):
    """文章发布基类"""
    @abstractmethod
    def publish(self, title, content):
        """发布文章"""
        pass 