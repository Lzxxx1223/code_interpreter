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
                - `explanations`: <Explain of the single Java method line by line, explain in as much detail as possible, 
                including the methods and raw parameters used in each line, return as String>
            - `explanations`: <Detail explanation of the single Java class>
            """

    def analyzer(self, code):
        meta_prompt_template = PromptTemplate.from_template(self.meta_prompt)
        llm_chain = LLMChain(llm=LLMInit().llm, prompt=meta_prompt_template)
        response = llm_chain.run(code=[code]).replace("```json", '').replace("```", '')
        class_response = json.loads(response)

        class_info = copy.deepcopy(class_response)
        class_info.pop('methods')
        self.mongo_client.insert_code_class(class_info)

        class_key = dict()
        class_key['package'] = class_response['package']
        class_key['class'] = class_response['class']
        class_key['method'] = ''
        class_vec = dict()
        class_vec['explanations'] = class_response['explanations']
        class_vec['comments'] = class_response['comments']
        class_vec['enumInstance'] = class_response['enumInstance']
        class_vec['variables'] = class_response['variables']
        class_vector = OpenAIEmbeddings().embed_query(json.dumps(class_vec))
        self.weaviate_client.create_object(Config.WEAVIATE_CLASS_COLLECTION, class_key, class_vector)

        if 'methods' in class_response.keys() and len(class_response['methods']) > 0:
            for method in class_response['methods']:
                method_info = dict()
                method_info['package'] = class_response['package']
                method_info['class'] = class_response['class']
                method_info.update(method)
                self.mongo_client.insert_code_method(method_info)

                method_key = dict()
                method_key['package'] = method_info['package']
                method_key['class'] = method_info['class']
                method_key['method'] = method_info['name']
                method_vec = dict()
                method_vec['explanations'] = method_info['explanations']
                method_vec['parameters'] = method_info['parameters']
                method_vector = OpenAIEmbeddings().embed_query(json.dumps(method_vec))
                self.weaviate_client.create_object(Config.WEAVIATE_METHOD_COLLECTION, method_key, method_vector)



