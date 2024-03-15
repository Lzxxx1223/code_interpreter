from langchain.text_splitter import Language
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from meta_extractor import MetaExtractor
from orm_extractor import ORMExtractor
from invoked_extractor import InvokedExtractor
from common.config import Config


class CodeExtractor:

    @staticmethod
    def load_and_split():
        loader = GenericLoader.from_filesystem(
            Config.CODE_PATH,
            glob="**/*",
            suffixes=[".java", ".xml", ".yaml"],
            parser=LanguageParser()
        )
        documents = loader.load()
        java_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.JAVA)
        return java_splitter.split_documents(documents)

    def analyzer(self):
        meta_analyzer = MetaExtractor()
        orm_analyzer = ORMExtractor()
        invoked_extractor = InvokedExtractor()

        texts = self.load_and_split()
        for i in range(0, len(texts)):
            print(i)
            doc = texts[i]
            if '.java' in doc.metadata['source']:
                meta_analyzer.analyzer(doc)
                orm_analyzer.analyzer(doc, '')
            else:
                orm_analyzer.analyzer('', doc)
        invoked_extractor.analyzer()
