import json
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from llm_init.llm_init import LLMInit
from internal_database.mongo_client import MongoDB


class ORMChangeDB:

    prompt = """       
            Please analyze the provided the database and ORM (Object-Relational Mapping) information 
            to answer which ORM method can modify the value of provided the database information :

            1. For each method in ORMMethods of ORM information and find insert or update method
            2. Analyzer each method's SQL to identify whether this sql can potential modify this database information
            
            Please format the extracted information as a JSON List object with the following structure:
            - `canChange` : <Whether this orm method can modify this database information, value is True or False>
            - `package`: <the package of this orm method>
            - `class`: <the class of this orm method>
            - `method`: <the name of this orm method>
            
            Database:
            {db}
            
            ORM:
            {orm}
            """

    def analyzer(self, db):
        result = list()
        orm = MongoDB().get_all_orm()
        for orm_item in orm:
            prompt_template = PromptTemplate.from_template(self.prompt)
            llm_chain = LLMChain(llm=LLMInit().llm, prompt=prompt_template)
            response = json.loads(llm_chain.run(orm=orm_item, db=db).replace("```json", '').replace("```", ''))
            for response_item in response:
                if response_item['canChange']:
                    result.append(response_item)
        return result


# code_change_db = CodeChangeDB()
# print(code_change_db.analyzer(
#     """
#     - Table Name: product.dc
# - Column Name: dca1
# - Data Type: VARCHAR(40)
# - Description: column name is pin attribute physical name, value is pin attribute value
# - Example Value: 'vendor_dca1_value'
# """
# ))
#