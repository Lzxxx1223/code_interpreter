from langchain.memory import VectorStoreRetrieverMemory
from internal_database.weaviate_client import WeaviateClient
from langchain.vectorstores import Weaviate
from common.config import Config
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from llm_init.llm_init import LLMInit


class CVM:

    prompt = """
        Your are a Java development expert, and you working on upgrade the dependencies library version.
        Give the answer how to upgrade the provided dependencies library version and other dependencies library need to upgrade at the same time.
        
        Please format the extracted information as a JSON object with the following structure:
        - `filePath`: <path of the changed file>
        - `line`: <the line need to change>
        - `oldValue`: <old value in file>
        - `newValue`: <new value should replace in line>
        
        Dependencies library :
        {input}
        
    """

    def get_llm_chain(self):
        vector_store = Weaviate(client=WeaviateClient().weaviate_client, index_name=Config.WEAVIATE_RAW_COLLECTION,
                                text_key='text', embedding=OpenAIEmbeddings(), by_text=False)
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs=dict(k=8),
        )
        memory = VectorStoreRetrieverMemory(retriever=retriever)
        prompt_template = PromptTemplate.from_template(self.prompt)
        return LLMChain(llm=LLMInit().llm, prompt=prompt_template, memory=memory)

