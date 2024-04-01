from common.config import Config
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from llm_init.llm_init import LLMInit


class DBAnalyzer:

    prompt = """
        Please analyze the provided SQL file and give an answer for provided question:

        SQL file:
        {sql_content}
        
        Question:
        {question}
        """

    def analyzer(self, question):
        with open(Config.SQL_DDL_DML_FILE_PATH, 'r') as f:
            sql_content = f.read()
        prompt_template = PromptTemplate.from_template(self.prompt)
        llm_chain = LLMChain(llm=LLMInit().llm, prompt=prompt_template)
        return llm_chain.run(sql_content=sql_content, question=question)
