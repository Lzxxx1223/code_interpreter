import os
from langchain.chat_models import ChatOpenAI


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

    def __init__(self,
                 open_ai_key='sk-hoZTk62z0b57ff585b04T3BlbKFJF9Ad5F81CC3d41f1BA4c',
                 open_ai_base='https://api.ohmygpt.com/v1',
                 model='gpt-3.5-turbo'):
        os.environ['OPENAI_API_KEY'] = open_ai_key
        self.llm = ChatOpenAI(openai_api_base=open_ai_base, model=model, temperature=0, max_tokens=4096)


# from langchain.chains.llm import LLMChain
# from langchain.prompts import PromptTemplate
# prompt_template = PromptTemplate.from_template("Design the JSON file can describe the {java} class")
# llm_init = LLMInit()
# llm_chain = LLMChain(llm=llm_init.llm, prompt=prompt_template)
# print(llm_chain.run(java='java'))
