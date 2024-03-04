import json

from code_analyzer.code_tool import CodeTool
from analyzer_agent.invoke_agent.method_chain_agent import InvokeMethodAgent
from analyzer_agent.invoke_agent.method_global_variable_agent import MethodParameterAgent
from analyzer_agent.invoke_agent.variable_get_agent import VariableGetAgent
from analyzer_agent.invoke_agent.variable_invoked_agent import VariableInvokedAgent
from langchain.tools import StructuredTool
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from code_analyzer.code_tool import MethodInforSchema
from code_analyzer.code_tool import VariableSchema
from llm_init.llm_init import LLMInit


class AnalyzerAgent:

    file_path: str
    code_tool: CodeTool
    tool_agent: initialize_agent
    prompt = """
            Provide following JSON with a list of Java code descriptions that can change the database table "dc" under database schema "product": 
            ###
            {information}
            ###
            For each description to get information:
                If "type" field equals "method":
                    step 1 : get explanations field of the method from the method metadata
                    step 2 : get invoke field of the method from the method metadata
                    step 3 : get the invoked chain data of the method by using tool  
                else if "type"  field equals "class":
                    step 1 : get class metadata
            Then your job is to analyzer all the information and produce a final detailed explanation 
            about how these Java codes change the database table 'dc' under the database schema 'product'.
            """

    basic_prompt = """
        Provide the answer of the `{user_input}` by using tool
        """

    def __init__(self, file_path):
        self.file_path = file_path
        self.code_tool = CodeTool(self.file_path)
        self.get_tool_agent()

    def get_tool_agent(self):
        tools = [
                StructuredTool.from_function(
                    func=self.method_chain_invoke,
                    name='Get method invoked chain',
                    description="Get the invoked chain data of the method",
                    args_schema=MethodInforSchema
                ),
                StructuredTool.from_function(
                    func=self.method_global_variable,
                    name='Get member variables',
                    description='Get JSON data for member Variables changed in this method',
                    args_schema=MethodInforSchema
                ),
                StructuredTool.from_function(
                    func=self.variable_used,
                    name='Get method used variable',
                    description='Get JSON data about which methods can obtain member variables, input have package, class, method, variable',
                    args_schema=VariableSchema
                ),
                StructuredTool.from_function(
                    func=self.variable_invoked,
                    name='Get variable invoked chain',
                    description='Get JSON data about which methods invoke the variable',
                    args_schema=VariableSchema
                )
            ]
        tools.extend(self.code_tool.tool_agent.tools)
        llm_init = LLMInit()
        self.tool_agent = initialize_agent(tools, llm_init.llm,
                                           agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                                           verbose=True)

    def method_chain_invoke(self, package, clazz, method):
        method_data = {'class': clazz, 'method': method, 'package': package}
        print("----------------------------------------------")
        print("------------- method chain start -------------")
        print("----------------------------------------------")
        invoke_agent = InvokeMethodAgent(self.code_tool)
        response = invoke_agent.get_invoke_chain(method_data)
        print("----------------------------------------------")
        print("------------ method chain response -----------")
        print("----------------------------------------------")
        print(response)
        print("-------------- method chain end --------------")
        return response

    def method_global_variable(self, package, clazz, method):
        method_data = {'class': clazz, 'method': method, 'package': package}
        print("----------------------------------------------")
        print("-------- method global variable start --------")
        print("----------------------------------------------")
        global_variable_agent = MethodParameterAgent(self.code_tool)
        response = global_variable_agent.global_variables_changed_in_method(method_data)
        print("----------------------------------------------")
        print("------ method global variable response -------")
        print("----------------------------------------------")
        print(response)
        print("-------- method global variable end --------")
        return response

    def variable_used(self, package, clazz, method, variable):
        method_data = {'class': clazz, 'method': method, 'package': package, 'variable': variable}
        print("----------------------------------------------")
        print("------------- variable used start ------------")
        print("----------------------------------------------")
        variable_used_agent = VariableGetAgent(self.code_tool)
        response = variable_used_agent.variables_used(method_data)
        print("----------------------------------------------")
        print("------------ variable used response ----------")
        print("----------------------------------------------")
        print(response)
        print("-------------- variable used end -------------")
        return response

    def variable_invoked(self, package, clazz, method, variable):
        method_data = {'class': clazz, 'method': method, 'package': package, 'variable': variable}
        print("----------------------------------------------")
        print("----------- variable invoked start -----------")
        print("----------------------------------------------")
        variable_invoked_agent = VariableInvokedAgent(self.code_tool)
        response = variable_invoked_agent.variables_invoked(method_data)
        print("----------------------------------------------")
        print("---------- variable invoked response ---------")
        print("----------------------------------------------")
        print(response)
        print("------------ variable invoked end ------------")
        return response

    def basic_knowledge(self, user_input):
        final_prompt = (self.basic_prompt
                        .replace('{user_input}', user_input))
        return self.tool_agent.run(final_prompt)

    def code_interpreter(self, input_information):
        final_prompt = (self.prompt
                        .replace('{information}', json.dumps(input_information, indent=4)))
        return self.tool_agent.run(final_prompt)


# input_data = [
#     {'class': 'EnumType', 'package': 'com.example.demo.entity', 'variable': 'PRODUCT', 'type': 'variable'},
#     {'method': 'processVin', 'class': 'ProcessController', 'package': 'com.example.demo.controller', 'type': 'method'},
#     {'class': 'Mapping', 'package': 'com.example.demo.model', 'type': 'class'},
#     {'class': 'DC', 'package': 'com.example.demo.model', 'type': 'class'},
#     {'method': 'link', 'class': 'Process', 'package': 'com.example.demo.service', 'variable': 'vin', 'type': 'method'},
#     {'method': 'loadSchema', 'class': 'InitService', 'package': 'com.example.demo.service', 'type': 'method'},
#     {'method': 'insertSt', 'class': 'ProductWrite', 'package': 'com.example.demo.service', 'type': 'method'}
# ]

# analyzer_agent = AnalyzerAgent('/Users/liuzhongxu/PycharmProjects/code_interpreter/code_analyzer/code_method_summary.json')
# print(analyzer_agent.code_interpreter(input_data))
# #
# result = """
# The invoke chain of the entire Java program involves the following methods and logic:
# 1. ProductWrite.insertSt method: Takes a Concept object as input,
#     generates an SQL insert statement based on the concept's enum type and columns,
#     and stores the statement in the insertStr variable.
# 2. InitService.loadschema method: Initializes mappings and loads the schema for EnumType.VENDOR and EnumType.PRODUCT.
# 3. InitService.init method: Initializes mappings and loads the schema for EnumType.VENDOR and EnumType.PRODUCT.
# 4. Process.link method: Performs operations to link vendor and product concepts by retrieving maximum pin value,
#     concepts, mappings, generating insert statement, and inserting it into the SQL process.
# """

# """
# The invoke chain within the Java program based on the provided JSON data and method metadata is as follows:
# insertSt method in ProductWrite class (com.example.demo.service) invokes link method in Process class (com.example.demo.service).
# The insertSt method generates an SQL insert statement based on a Concept object and stores it in the insertStr variable.
# The link method in Process class performs operations to link vendor and product concepts,
# involving various services and methods to handle data processing and insertion.
# """

# prompt = """
#      Knowledge 1 - Provide a detailed analysis of the method metadata, including the method name, class, and package involved in a specific format:
#          {"method":"{method}","class":"{clazz}","package":"{package}"}
#      Knowledge 2 - Present JSON data illustrating the invoked chain of this method:
#          {method_chain_response}
#      Knowledge 3 - Detail the JSON data showcasing the global variables altered within this method:
#          {method_global_variable_response}
#      Knowledge 4 - Elaborate on which methods have access to the values of the modified global variables through the following JSON data:
#          {variable_used_response}
#      Knowledge 5 -Describe the invoked chain involving these global variables in JSON format:
#          {variable_method_chain}
#
#      Utilize the provided JSON data and the explanations of each method's metadata to elucidate the entire invoke chain within the Java program. Delve into the logic behind each method.
#      """

# if input_information['method'] is None or 'N/A' == input_information['method']:
#             variable_invoked_response = self.variable_invoked(input_information)
            # pass
        # method_chain_response = self.method_chain_invoke(input_data)
        # method_global_variable_response = self.method_global_variable(input_data)
        # input_data['variable'] = self.method_global_variable_response['name']

        # variable_data = dict()
        # variable_data['package'] = variable_used_response['package']
        # variable_data['class'] = variable_used_response['class']
        # variable_data['method'] = variable_used_response['method']
        # variable_chain_response = self.method_chain_invoke(variable_data)

        # method_chain_response = [{"hasInvoked": True,
        #                           "method": "loadschema",
        #                           "class": "initservice",
        #                           "package": "com.example.demo.service"},
        #                          {"hasInvoked": True, "method": "init",
        #                           "class": "initservice",
        #                           "package": "com.example.demo.service"}]
        #
        # method_global_variable_response = {"hasVariable": True,
        #                                    "name": "insertStr",
        #                                    "type": "String",
        #                                    "method": "insertSt",
        #                                    "class": "ProductWrite",
        #                                    "package": "com.example.demo.service"}
        #
        # variable_used_response = {"hasMethod": True,
        #                           "method": "getInsertStr",
        #                           "class": "ProductWrite",
        #                           "package": "com.example.demo.service"}
        #
        # variable_method_chain = [{"hasInvoked": True,
        #                           "method": "link",
        #                           "class": "process",
        #                           "package": "com.example.demo.service"}]
        #
        # final_prompt = (self.prompt
        #                 .replace('{method}', input_information['method'])
        #                 .replace('{clazz}', input_information['class'])
        #                 .replace('{package}', input_information['package'])
        #                 .replace('{method_chain_response}', json.dumps(method_chain_response))
        #                 .replace('{method_global_variable_response}', json.dumps(method_global_variable_response))
        #                 .replace('{variable_used_response}', json.dumps(variable_used_response))
        #                 .replace('{variable_method_chain}', json.dumps(variable_method_chain))
        #                 )
        # return self.code_tool.run(final_prompt)

#
# Now that we have gathered information about the Java classes and methods related to changing the database table "dc" under the database schema "product", let's summarize the data generation process based on the analyzed Java JSON items:
#
# 1. EnumType Class:
#    - Constants:
#      - PRODUCT:
#        - tableName: product.dc
#        - fieldName: pin
#    - Constructors:
#      - EnumType(tableName)
#      - EnumType(fieldName)
#    - Member Variables:
#      - tableName: String
#      - fieldName: String
#
# 2. ProcessController Class:
#    - Method: processVin
#      - Explanation: Handles GET requests to the root URL and invokes the 'link' method of the 'Process' class.
#      - Invoked Method Chain: link method of the Process class
#
# 3. Mapping Class:
#    - Constructors:
#      - Mapping(vinDCAId, pinDCAId)
#    - Member Variables:
#      - vinDCAId: Integer
#      - pinDCAId: Integer
#
# 4. DC Class:
#    - Constructors:
#      - DC(dcId, table, name)
#    - Member Variables:
#      - dcId: Integer
#      - table: String
#      - name: String
#
# 5. Process Class:
#    - Method: link
#      - Explanation: Main method of the Process class that interacts with various other classes to retrieve data and insert into the database.
#      - Invoked Method Chain:
#        - findMaxPin in SQLProcess
#        - getConceptSchema in InitService
#        - getSt in VendorWrite
#        - getMappings in InitService
#        - getInsertStr in ProductWrite
#
# 6. InitService Class:
#    - Method: loadSchema
#      - Explanation: Loads schema for a given EnumType, interacts with SQLProcess and ProductWrite classes to insert data into the database.
#      - Invoked Method Chain:
#        - selectDCByDCTable in SQLProcess
#        - selectDCAByDCId in SQLProcess
#        - insertSt in ProductWrite
#
# 7. ProductWrite Class:
#    - Method: insertSt
#      - Explanation: Builds an SQL insert statement based on the Concept object provided.
#      - Invoked Method Chain: None
#
# Based on the analyzed information, the data generation process for the database table "dc" under the database schema "product" involves handling requests in the ProcessController, loading schema in InitService, and inserting data using ProductWrite. The Process class plays a central role in coordinating these operations.


# Based on the gathered information, the data generation process of the database table 'dc' under the database schema 'product' involves the following steps:
#
# 1. EnumType Class (com.example.demo.entity):
#    - No method or variable information available.
#
# 2. ProcessController Class (com.example.demo.controller):
#    - Method 'processVin':
#      - This method is annotated with @GetMapping and handles GET requests to the root URL.
#      - It calls the 'link' method of the 'process' object, which is an instance of the 'Process' class injected via @Autowired.
#
# 3. Mapping Class (com.example.demo.model):
#    - Constructor: Mapping(Integer vinDCAId, Integer pinDCAId)
#
# 4. DC Class (com.example.demo.model):
#    - Constructor: DC(Integer dcId, String table, String name)
#
# 5. Process Class (com.example.demo.service):
#    - Method 'link':
#      - Retrieves the max pin value from SQLProcess class.
#      - Gets the vendor concept schema from InitService class.
#      - Gets the product concept schema from InitService class.
#      - Retrieves the vendor identifier using VendorWrite class.
#      - Retrieves the mappings using InitService class.
#      - Creates a mapping between vendor and product attributes.
#      - Creates a product identifier.
#      - Replaces placeholders in the insert statement with actual values.
#      - Inserts the data into the database.
#
# 6. InitService Class (com.example.demo.service):
#    - Method 'loadSchema':
#      - Loads the schema for a given EnumType.
#      - Creates a new Concept object and sets its properties based on the data retrieved from the database.
#      - Inserts the concept into the conceptSchema map.
#      - If the EnumType is PRODUCT, it also inserts the concept using the ProductWrite class.
#
# 7. ProductWrite Class (com.example.demo.service):
#    - Method 'insertSt':
#      - Takes a Concept object as a parameter.
#      - Creates a StringBuilder object to dynamically build an SQL insert statement.
#      - Iterates over the columns of the Concept object and appends them to the SQL statement.
#      - Sets the insertStr member variable to the generated SQL statement.

# """
#  Based on the information gathered, the Java codes provided can change the database table 'dc' under the database schema 'product' in the following way:
#  The 'link' method in the 'Process' class is the main method responsible for this change. It retrieves the max pin value from the 'SQLProcess' class,
#  gets the vendor concept schema from the 'InitService' class, retrieves the vendor identifier using the 'VendorWrite' class,
#  retrieves the mappings using the 'InitService' class, creates a mapping between vendor and product attributes, creates a product identifier,
#  replaces placeholders in the insert statement with actual values, and finally inserts the data into the database table 'dc' under the database schema 'product'.
#  """

