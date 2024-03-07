import json
from langchain.text_splitter import Language
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from llm_init.llm_init import LLMInit


def write_response_to_file(result):
    with open("code_method_summary.json", "w") as f:
        json.dump(result, f, indent=4)


class CodeAnalyzer:

    code_path: str
    prompt = """
            Analyze the following Java code snippet and extract the relevant information:
            
            ```java
            {text}
            ```
            
            Extract the following information from the code:
            
            1. Class name
            2. Class attributes (name, type, modifiers)
            3. Method names and signatures (name, return type, parameters, modifiers)
            4. Method parameters (name, type, return types)
            5. Method return types
            6. Method invocations (invoked method names and their corresponding class names)
            7. SQL queries or ORM interactions (query strings, accessed attributes or columns)
            8. Conditional statements and loops (if-else, switch-case, for, while)
            9. Exception handling (try-catch blocks, caught exceptions)
            10. Annotations and configuration (relevant annotations, configuration files or classes)
            11. Comments and TODO notes
            12. Variable names and usage (related to attribute changes or database interactions)
            
            Provide the extracted information in a structured format, such as JSON or a well-formatted list.
            """

    def __init__(self, code_path):
        self.code_path = code_path

    def load_and_split(self):
        loader = GenericLoader.from_filesystem(
            self.code_path,
            glob="**/*",
            suffixes=[".java"],
            parser=LanguageParser()
        )

        documents = loader.load()
        java_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.JAVA)
        return java_splitter.split_documents(documents)

    def run(self):
        prompt_template = PromptTemplate.from_template(self.prompt)
        llm_init = LLMInit()
        llm_chain = LLMChain(llm=llm_init.llm, prompt=prompt_template)

        stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name='text')
        result = list()
        texts = self.load_and_split()
        for i in range(0, len(texts)):
            print(i)
            response = stuff_chain.run([texts[i]])
            result.append(json.loads(response))
        # result.append(json.loads(stuff_chain.run([texts[13]])))
        # result.append(json.loads(stuff_chain.run([texts[12]])))
        write_response_to_file(result)


code_analyzer = CodeAnalyzer('/Users/liuzhongxu/Documents/Learning/demo 2/src/main/java')
code_analyzer.run()