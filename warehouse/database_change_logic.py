from langchain.chains import SequentialChain
from langchain_core.pydantic_v1 import Field
from langchain_core.pydantic_v1 import BaseModel
from langchain.tools import StructuredTool
from langchain.agents import AgentType, AgentExecutor
from langchain.agents import initialize_agent
from llm_init.llm_init import LLMInit
from db_analyzer.db_analyzer import DBAnalyzer
from analyzer_agent.orm_change_db import ORMChangeDB
from analyzer_agent.meta_change_db import MetaChangeDB
from analyzer_agent.method_chain_agent import MethodChainAgent
from analyzer_agent.method_change_variable_agent import MethodChangeVariableAgent
from analyzer_agent.method_get_variable_agent import MethodGetVariableAgent
from internal_database.mongo_client import MongoDB
from internal_database.weaviate_client import WeaviateClient
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate


class ClassInforSchema(BaseModel):
    package: str = Field(description="package")
    clazz: str = Field(description="class")


class MethodInforSchema(ClassInforSchema):
    method: str = Field(description="method")


class VariableSchema(ClassInforSchema):
    variable: str = Field(description="variable")


class DataBaseChangeLogic:

    overall_chain: SequentialChain
    db_analyzer = DBAnalyzer()
    orm_change_db = ORMChangeDB()
    meta_change_db = MetaChangeDB()
    method_chain_agent = MethodChainAgent()
    method_change_variable_agent = MethodChangeVariableAgent()
    method_get_variable_agent = MethodGetVariableAgent()
    mongo_client = MongoDB()
    weaviate_client = WeaviateClient()

    prompt = """
        Please gather each steps result, generate a comprehensive and detailed summary to answer the provided question:

        1. Analyze the database information
        2. Get ORM methods that can change the database
        3. Get code methods and code classes that can change the database
        4. Get the methods who invoked step 2 and step 3 methods
        5. Get metadata explanations for step 4 methods

        question:
        In code-interpreter project, {input}
    """

    def __init__(self):
        tools = [
            StructuredTool.from_function(
                func=self.mongo_client.get_all_methods,
                name='Get all methods',
                description='Get all methods in code-interpreter with its corresponding package and class in the code, '
                            'response not contain the method metadata data'
            ),
            StructuredTool.from_function(
                func=self.mongo_client.get_all_classes,
                name='Get all classes',
                description='Get all classes in code-interpreter with its corresponding package in the code, '
                            'response not contain the class metadata data'
            ),
            StructuredTool.from_function(
                func=self.mongo_client.get_method_metadata,
                name='Get Method Metadata',
                description='Get method metadata in code-interpreter based on package, class and method. \
                    Response contains the method invocation, return type, parameter and corresponding class information etc',
                args_schema=MethodInforSchema
            ),
            StructuredTool.from_function(
                func=self.mongo_client.get_class_metadata,
                name='Get Class Metadata',
                description='Get class metadata in code-interpreter based on package, class. \
                    Response contains the class variables, enumInstance, annotation and explanations information etc',
                args_schema=ClassInforSchema
            ),
            StructuredTool.from_function(
                func=self.mongo_client.get_methods_in_class,
                name='Get Class Methods',
                description='Get the methods of class in code-interpreter based on package and class. Return the list of methods metadata',
                args_schema=ClassInforSchema
            ),
            StructuredTool.from_function(
                func=self.mongo_client.get_all_orm,
                name='Get All ORM Information',
                description='Get all ORM methods or configuration in code-interpreter . Response contains SQL, ResultMap and corresponding package, class and method'
            ),
            StructuredTool.from_function(
                func=self.meta_change_db.analyzer,
                name='Get Meta Change DB',
                description='Get meta methods and code classes in code-interpreter that involves constructing and executing SQL statements to change database table values. '
                            'Response is the list of method or class information'
            ),
            StructuredTool.from_function(
                func=self.orm_change_db.analyzer,
                name='Get ORM Change DB',
                description='Get ORM methods in code-interpreter that involves constructing and executing SQL statements to change database table. '
                            'Response is the list of method information'
            ),
            StructuredTool.from_function(
                func=self.method_change_variable_agent.analyzer,
                name='Get Variables Changed In Method',
                description='Get all global variables in code-interpreter changed in provided method information'
            ),
            StructuredTool.from_function(
                func=self.method_get_variable_agent.analyzer,
                name='Get Methods Can Get Variables Value',
                description='Get the provided methods in code-interpreter can get(not set) the value of provided variables information'
            ),
            StructuredTool.from_function(
                func=self.db_analyzer.analyzer,
                name='Get Database information',
                description='Get the database information in code-interpreter base on provided question'
            ),
            StructuredTool.from_function(
                func=self.method_chain_agent.analyzer,
                name='Get Be Invoked Methods',
                description='Get the methods in code-interpreter who invoked provided method'
            )
        ]

        agent_execute = initialize_agent(tools, LLMInit().llm,
                                         agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                                         verbose=True,
                                         output_key='output')
        prompt_template = PromptTemplate.from_template("""
            Explain the result
        """)
        llm_chain = LLMChain(llm=LLMInit().llm, prompt=prompt_template, output_key='text')
        self.overall_chain = SequentialChain(chains=[agent_execute, llm_chain], input_variables=['input'], verbose=True)

# while True:
#     user_input = input()
#     print(CodeTool().analyzer(user_input))
# print(CodeTool().analyzer('what is the `product` table structure in database?'))
# print(CodeTool().analyzer('What is the explanation of the "link" method under "Process" class and "com.example.demo.service" package?'))
# print(CodeTool().analyzer('How does the methods and classes insert values into `product.dc` database table.'))


# """
# Your already have a batch tools to get code and database information,
#         by only using tool to answer the provided question.
#
#         1. Analyze the database information
#         2. Get ORM methods that can change the database
#         3. Get code methods and code classes that can change the database
#         4. For each ORM and code class or method, analyzer the class and method metadata
#         5. Get the methods who invoked provided method
#
#         Based on all information answer the question
#
#         question:
#         Analyze the logic about how does the code insert values into `product.dc` database by using tool
# """
# """
#         Please gather each steps result, generate a comprehensive and detailed summary to answer the provided question:
#
#         1. Analyze the database information
#         2. Get ORM methods that can change the database
#         3. Get code methods and code classes that can change the database
#         4. Get the methods who invoked step 2 and step 3 methods
#         5. Get metadata explanations for step 4 methods
#
#         question:
#         Analyze the logic about how does the code insert values into `product.dc` database
#     """