from .base import ArticlePublisher

PUBLISHER_REGISTRY = {}

def register_publisher(name: str):
    def decorator(cls):
        if not issubclass(cls, ArticlePublisher):
            raise TypeError("Publisher must inherit from ArticlePublisher")
        PUBLISHER_REGISTRY[name] = cls
        return cls
    return decorator 