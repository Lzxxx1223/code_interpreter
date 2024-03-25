import json
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from internal_database.weaviate_client import WeaviateClient
from langchain.embeddings import OpenAIEmbeddings
from internal_database.mongo_client import MongoDB
from llm_init.llm_init import LLMInit
import copy
from common.config import Config


class MetaExtractor:

    weaviate_client = WeaviateClient()
    mongo_client = MongoDB()

    class_prompt = """
        You are Java code interpreter tool, your job is analyst provided Java source code and generate the detail Java class description.
        
        Please format the extracted information as a JSON object with the following structure:
        - `package` : <package name>
        - `class` : <class name>
        - `description` : <detail explanation of the Java class, return as the string>
        
        Source class:
        {code}
        
        """

    method_prompt = """
        You are Java code interpreter tool, your job is analyst provided Java source code and generate the detail Java methods line by line.

        Please format the extracted information as a List JSON object with the following structure:
        - `package` : <package name>
        - `class` : <class name>
        - `method` : <method name>
        - `description`: <Explain the Java method step by step, return as the string>

        Source class:
        {code}

    """

    meta_prompt = """
            You are a very patience Java export and provide following Java source code: {code}

            Analyst each method in the Java code, create a JSON object with following keys:
            - `javaType`: <value should be one fo the class, interface, abstract and enum>
            - `comments`: <The comments of the Java class, default is empty string>
            - `package`: <The name of the Java package>
            - `class`: <The name of the Java class>
            - `annotation` <list annotations of the Java class, default is empty List>
            - `modifier`: <The modifier of the Java class, default is 'protect'>
            - `interface`: <interface of the Java class, default is empty string>  
            - `extent`: <List extends of the Java class, default is empty List> : 
                - `package`: <The package name of the extent>
                - `class`: <The class na me of the extent>
            - `enumInstance`: <List of enum instance value, default is empty List>
                - `name`: <The name of the enum instance>
                - `instances` : <The parameters of the enum instance, default is empty List>
                    - `instanceName`: <The name of the enum instance>
                    - `instanceType`: <The type of the enum instance>
                    - `instanceValue`: <The value of the enum instance, default is empty string>
            - `variables`: <List member variables of Java class, default is empty List> 
                - `name`: <The name of the member variable>
                - `type`: <The data type of the member variable>
                - `value`: <The value of the member variable, default is empty string>
                - `usage` : <The usage of the variable>
            - `methods`: <List methods of the Java class, default is empty List> 
                - `comments`: <The comment out of the method, default is empty string>
                - `name`: <The name of the method>
                - `modifier`: <The modifier of the Java method, default is 'protect'>
                - `annotation` <list annotations of the method, default is empty List>
                - `returnType`: <The return type of the method>
                - `parameters`: <The parameters of the method>
                    - `name`: <The name of the parameter>
                    - `type`: <The data type of the parameter>
                - `invocations`: <Invoked method in the same method not the same Java class, default is empty List>
                    - `package`: <The package name of the invoked method>
                    - `class`: <The class name of the invoked method>
                    - `method`: <The method name of the invoked method>
                    - `parameters`: <The parameters of the invoked method>
                        - `value`: <The value of the parameter, default is empty string>
                        - `type`: <The data type of the parameter>
            """

    def class_analyst(self, code):
        prompt_template = PromptTemplate.from_template(self.class_prompt)
        llm_chain = LLMChain(llm=LLMInit().llm, prompt=prompt_template)
        response = llm_chain.run(code=[code]).replace("```json", '').replace("```", '')
        class_response = json.loads(response)
        class_vector = OpenAIEmbeddings().embed_query(json.dumps(class_response['description']))
        self.weaviate_client.create_object(Config.WEAVIATE_CLASS_COLLECTION, class_response, class_vector)

    def method_analyst(self, code):
        prompt_template = PromptTemplate.from_template(self.method_prompt)
        llm_chain = LLMChain(llm=LLMInit().llm, prompt=prompt_template)
        response = llm_chain.run(code=[code]).replace("```json", '').replace("```", '')
        method_response = json.loads(response)
        for item in method_response:
            method_vector = OpenAIEmbeddings().embed_query(json.dumps(item['description']))
            self.weaviate_client.create_object(Config.WEAVIATE_METHOD_COLLECTION, item, method_vector)

    def meta_analyst(self, code):
        self.class_analyst(code)
        self.method_analyst(code)

        meta_prompt_template = PromptTemplate.from_template(self.meta_prompt)
        llm_chain = LLMChain(llm=LLMInit().llm, prompt=meta_prompt_template)
        response = llm_chain.run(code=[code]).replace("```json", '').replace("```", '')
        class_response = json.loads(response)

        class_info = copy.deepcopy(class_response)
        class_info.pop('methods')
        self.mongo_client.insert_code_class(class_info)

        if 'methods' in class_response.keys() and len(class_response['methods']) > 0:
            for method in class_response['methods']:
                method_info = dict()
                method_info['package'] = class_response['package']
                method_info['class'] = class_response['class']
                method_info.update(method)
                self.mongo_client.insert_code_method(method_info)

    def analyzer(self, code):
        self.class_analyst(code)
        self.method_analyst(code)
        self.meta_analyst(code)



