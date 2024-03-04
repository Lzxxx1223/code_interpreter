import json
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from llm_init.llm_init import LLMInit


class DBAnalyzer:

    sql_path: str
    prompt = """
        Based on the SQL file:
        {sql_content}
        
        Find the table name where this information `{information}` is located.
        
        Provide them in JSON format with the following keys:
        - `schema`: <schema name>
        - `table`: <table name>
        - `column`: <column name>
        """

    basic_prompt = """
        Based on the SQL file:
        {sql_content}
        
        Provide the answer of the `{user_input}`
        """

    def __init__(self, sql_path):
        self.sql_path = sql_path

    def get_llm_chain(self, prompt_detail):
        llm_init = LLMInit()
        return LLMChain(llm=llm_init.llm, prompt=prompt_detail)

    def basic_information(self, user_input):
        sql_content = open(self.sql_path).read()
        prompt_template = PromptTemplate.from_template(self.basic_prompt)
        llm_chain = self.get_llm_chain(prompt_template)
        return llm_chain.run(sql_content=sql_content, user_input=user_input)

    def db_analyzer(self, information):
        sql_content = open(self.sql_path).read()
        prompt_template = PromptTemplate.from_template(self.prompt)
        llm_chain = self.get_llm_chain(prompt_template)
        return json.loads(llm_chain.run(sql_content=sql_content, information=information))


# prompt = """
#         Based on the SQL, analyzer the table structure and column comments:
#         {sql_content}
#
#         Find the table name where this information `{information}` is located.
#
#         return as JSON format:
#
#         parameter `schema` : table schema
#         parameter `table` : table name
#         parameter `column` : column name.
#
#     """

#
# db_analyzer = DBAnalyzer('database.sql')
# print(db_analyzer.db_analyzer('pin attribute dca1'))
#
# result = """
# {
#     "table": "product.dc",
#     "column": "dca1"
# }
# """
