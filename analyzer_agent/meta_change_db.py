import json
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from llm_init.llm_init import LLMInit
from internal_database.mongo_client import MongoDB
from internal_database.weaviate_client import WeaviateClient


class MetaChangeDB:

    weaviate_client = WeaviateClient()
    mongo_client = MongoDB()

    prompt = """       
            Please analyze provided database information and provided the class metadata or method metadata information
            to answer whether this class or method is directly relate or contains the provided database information:
            
            1. Analyze the enumInstance, variable and parameter check whether it contain the database table or column information
            2. According to the explanations to analyze whether this class or method has related to this database information
            
            Please format the extracted information as a JSON object with the following structure:
            - `related` : <Whether this class or method is directly relate or contains the provided database information, value is True or False>
            - `package`: <the package of this orm method>
            - `class`: <the class of this orm method>
            - `method`: <the name of this orm method>
            
            Database:
            {database}
            
            Class:
            {clazz_metadata}
                           
            Method:
            {method_metadata}
            
            """

    @staticmethod
    def merge_class_method_result(class_result, method_result):
        method_keys = list()
        for method_item in method_result:
            method_keys.append(method_item['package'] + "-" + method_item['class'])
        for class_item in class_result:
            class_keys = class_item['package'] + "-" + class_item['class']
            if class_keys not in method_keys:
                method_result.append(class_item)
        return method_result

    def analyzer(self, db):
        class_result = list()
        method_result = list()
        class_sim = self.weaviate_client.get_class_explanation(db)
        method_sim = self.weaviate_client.get_method_explanation(db, 20)
        for class_item in class_sim:
            class_metadata = self.mongo_client.get_class_metadata(class_item['package'], class_item['class'])
            prompt_template = PromptTemplate.from_template(self.prompt)
            llm_chain = LLMChain(llm=LLMInit().llm, prompt=prompt_template)
            response = json.loads(llm_chain.run(database=db, clazz_metadata=class_metadata, method_metadata='')
                                  .replace("```json", '').replace("```", ''))
            if response['related']:
                class_result.append(response)
        for method_item in method_sim:
            method_metadata = self.mongo_client.get_method_metadata(method_item['package'], method_item['class'], method_item['method'])
            prompt_template = PromptTemplate.from_template(self.prompt)
            llm_chain = LLMChain(llm=LLMInit().llm, prompt=prompt_template)
            response = json.loads(llm_chain.run(database=db, clazz_metadata='', method_metadata=method_metadata)
                                  .replace("```json", '').replace("```", ''))
            if response['related']:
                method_result.append(response)
        return self.merge_class_method_result(class_result, method_result)


# code_change_db = MetaChangeDB()
# print(code_change_db.analyzer(
#     """
#     - Table Name: product.dc
# - Column Name: dca1
# - Data Type: VARCHAR(40)
# - Description: column name is pin attribute physical name, value is pin attribute value
# - Example Value: 'vendor_dca1_value'
# """
# ))
