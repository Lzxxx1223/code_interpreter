from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from llm_init.llm_init import LLMInit
from internal_database.mongo_client import MongoDB
import json


class MethodChangeVariableAgent:

    information_prompt = """       
                   Analyze provided method information to extract package, class and method information.

                   Please format the extracted information as a JSON object with the following structure:
                   - `package` : <the package name>
                   - `class`: <the class name>
                   - `method`: <the method name>

                   Method:
                   {method_information}

                   """

    prompt = """
            List all global variables changed in provided method information:
            
            Method:
            {method_metadata}
            
            """

    def analyzer(self, method_information):
        prompt_template = PromptTemplate.from_template(self.information_prompt)
        llm_chain = LLMChain(llm=LLMInit().llm, prompt=prompt_template)
        method_data = json.loads(llm_chain.run(class_information=method_information).replace("```json", '').replace("```", ''))
        method_metadata = MongoDB().get_method_metadata(method_data['package'], method_data['clazz'], method_data['method'])
        prompt_template = PromptTemplate.from_template(self.prompt)
        llm_chain = LLMChain(llm=LLMInit().llm, prompt=prompt_template)
        response = llm_chain.run(method_metadata=method_metadata)
        return response


# method_agent = MethodChangeAgent()
# print(method_agent.analyzer({"package": "com.example.demo.service", "class": "ProductWrite", "method": "insertSt"}))