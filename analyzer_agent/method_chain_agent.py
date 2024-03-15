from langchain.chains.llm import LLMChain
from llm_init.llm_init import LLMInit
from internal_database.mongo_client import MongoDB
from langchain.prompts import PromptTemplate
import json


class MethodChainAgent:

    mongo_client = MongoDB()
    prompt = """       
                Analyze provided method information to extract package, class and method information.
                
                Please format the extracted information as a JSON object with the following structure:
                - `package` : <the package name>
                - `class`: <the class name>
                - `method`: <the method name>

                Method:
                {method_information}

                """

    def analyzer(self, method_information):
        prompt_template = PromptTemplate.from_template(self.prompt)
        llm_chain = LLMChain(llm=LLMInit().llm, prompt=prompt_template)
        response = json.loads(llm_chain.run(method_information=method_information)
                              .replace("```json", '').replace("```", ''))
        method_metadata = self.mongo_client.get_method_metadata(response['package'], response['class'],
                                                                response['method'])
        if method_metadata is not None and 'beInvoked' in method_metadata:
            return method_metadata['beInvoked']
        return list()

