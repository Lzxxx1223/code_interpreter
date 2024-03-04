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
            You are a very patience Java export and provide following Java source code: {text}
            
            Analyst each method in the Java code, create a JSON object with following keys:
            - `javaType`: <value should be one fo the class, interface, abstract and enum>
            - `package`: <The name of the Java package>
            - `class`: <The name of the Java class>
            - `implement`: <list implements of the Java class>  
                - `implementName`: <The name of the implement>
            - `extent`: <The extends of the Java class> : 
                - `extentPackage`: <The package name of the extent class>
                - `extentClass`: <The class name of the extent class>
            - `constants`: <List of constant value>
                - `constantsName`: <The name of the constant>
                - `constantsParameters` : <The parameters of the constant>
                    - `constantsParameterName`: <The name of the constant parameter>
                    - `constantsParameterValue`: <The value of the constant parameter>
            - `constructors`: <List constructor of Java class> 
                - `constructorName`: <The name of the constructor parameter>
                    - `constructorParameterType`: <The data type of the constructor parameter>
                    - `constructorParameterName`: <The name of the constructor parameter>
            - `memberVariables`: <List member variable of Java class> 
                - `memberVariableName`: <The name of the member variable>
                - `memberVariableType`: <The data type of the member variable>
                - `memberVariableValue`: <he value of the member variable>
            - `methods`: <List methods of the Java class> 
                - `methodName`: <The name of the method>
                - `returnType`: <The return type of the method>
                - `parameters`: <The parameters of the method>
                    - `name`: <The name of the parameter>
                    - `type`: <The data type of the parameter>
                - `invoke`: <List the method only be invoked in the current method>
                    - `invokePackageName`: <The package name of the invoked method>
                    - `invokeClassName`: <The class name of the invoked method>
                    - `invokeMethodName`: <The method name of the invoked method>
                    - `parameters`: <The parameters of the invoked method>
                        - `value`: <The value of the parameter>
                        - `type`: <The data type of the parameter>
                - `explanations`: <Explain of the single Java method line by line, explain in as much detail as possible, including the methods and raw parameters used in each line>
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


# code_analyzer = CodeAnalyzer('/Users/liuzhongxu/Documents/Learning/demo 2/src/main/java')
