from langchain.memory import VectorStoreRetrieverMemory
from internal_database.weaviate_client import WeaviateClient
from langchain.vectorstores import Weaviate
from common.config import Config
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from llm_init.llm_init import LLMInit


class CVM:

    weaviate_client = WeaviateClient()
    prompt = """
        Your are a Java development expert, and you working on upgrade the dependencies library version.
        Give the result how to upgrade the provided dependencies library version.
        
        Please format the extracted information as a JSON object with the following structure:
        - `filePath`: <the path of the changed file>
        - `lineNumber`: <changed rows>
        - `oldValue`: <old value in file>
        - `newValue`: <new value should replace in line>
        
        Dependencies library :
        {cvm}
        
    """

    def analyzer(self, cvm_report):
        vector_store = Weaviate(client=self.weaviate_client.weaviate_client, index_name=Config.WEAVIATE_RAW_COLLECTION,
                                text_key='text', embedding=OpenAIEmbeddings(), by_text=False)
        retriever = vector_store.as_retriever(
            search_kwargs=dict(k=1),
        )
        memory = VectorStoreRetrieverMemory(retriever=retriever)
        prompt_template = PromptTemplate.from_template(self.prompt)
        llm_chain = LLMChain(llm=LLMInit().llm, prompt=prompt_template, memory=memory)
        return llm_chain.run(cvm=cvm_report)


print(CVM().analyzer("""
    Upgrade spring-boot-start-parent library version from 3.1.5 to 3.2.3
"""))