from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from llm_init.llm_init import LLMInit
from internal_database.mongo_client import MongoDB
import json


class MethodGetVariableAgent:

    information_prompt = """       
                Analyze provided class information to extract package and class information.

                Please format the extracted information as a JSON object with the following structure:
                - `package` : <the package name>
                - `class`: <the class name>

                Class:
                {class_information}

                """

    prompt = """
            Find the provided methods can get(not set) the value of provided variables information:
            
            Provide them in List JSON format with the following keys:
            - `name`: <variable name>
            - `methods`: <List method can return the value of corresponding variable>
                - `method` : <method name>
                - `class` :  <class name>
                - `package` : <package name>
            
                        
            Variables:
            {variables}
            
            Methods:
            {methods}
            
            """

    def analyzer(self, class_information):
        prompt_template = PromptTemplate.from_template(self.information_prompt)
        llm_chain = LLMChain(llm=LLMInit().llm, prompt=prompt_template)
        method_data = json.loads(llm_chain.run(class_information=class_information).replace("```json", '').replace("```", ''))
        method_metadata = MongoDB().get_methods_in_class(method_data['package'], method_data['class'])
        prompt_template = PromptTemplate.from_template(self.prompt)
        llm_chain = LLMChain(llm=LLMInit().llm, prompt=prompt_template)
        response = llm_chain.run(methods=method_metadata, variables=method_data['variable'])
        return response


# variable = VariableGetAgent()
# print(variable.analyzer({"package": "com.example.demo.service", "class": "ProductWrite"}, """Global variables changed in the provided method information:
# 1. insertStr"""))