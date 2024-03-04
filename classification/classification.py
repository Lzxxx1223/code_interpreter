import json
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from llm_init.llm_init import LLMInit


class Classification:

    sql_path: str
    prompt = """
        Based on the SQL file:
        {sql_content}
        
        There are three classification: java code, database and both.
        Determine whether the input {input} is java code related or database related or both java code and database related.
        
        provide the classification, response should only be "java code", "database" or "both"
        """

    def __init__(self, sql_path):
        self.sql_path = sql_path

    def classification(self, user_input) -> str:
        sql_content = open(self.sql_path).read()
        prompt_template = PromptTemplate.from_template(self.prompt)
        llm_init = LLMInit()
        llm_chain = LLMChain(llm=llm_init.llm, prompt=prompt_template)
        return llm_chain.run(sql_content=sql_content, input=user_input)


# classification = Classification("/Users/liuzhongxu/PycharmProjects/code_interpreter/db_analyzer/database.sql")
# print(classification.classification("What are the member variables of the `ProcessController` method?"))

# print(classification.classification("How is the value of the attribute dca1 of pin 1 generated?"))
