from langchain.text_splitter import Language
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from internal_database.weaviate_client import WeaviateClient
from common.config import Config
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Weaviate


class RawCodeExtractor:

    weaviate_client = WeaviateClient()

    def analyzer(self):
        loader = GenericLoader.from_filesystem(
            Config.CODE_PATH,
            glob="**/*",
            suffixes=[".java", ".xml", ".yaml", ".properties", ".sql"],
            parser=LanguageParser()
        )
        documents = loader.load()
        java_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.JAVA)
        texts = java_splitter.split_documents(documents)
        Weaviate.from_documents(texts, OpenAIEmbeddings(), client=self.weaviate_client.weaviate_client, by_text=False, index_name=Config.WEAVIATE_RAW_COLLECTION)


# RawCodeExtractor().analyzer()