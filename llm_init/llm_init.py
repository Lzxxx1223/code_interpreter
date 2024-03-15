from langchain.chat_models import ChatOpenAI
from common.config import Config


def singleton(cls, *args, **kwargs):

    instances = {}

    def wrapper():
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper


@singleton
class LLMInit:

    llm: ChatOpenAI

    def __init__(self):
        self.llm = ChatOpenAI(model=Config.OPENAI_MODEL, temperature=0, max_tokens=4096)
