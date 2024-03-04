import json
from pydantic import Field
from typing import Optional
from langchain_core.pydantic_v1 import BaseModel
from langchain.tools import StructuredTool
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from llm_init.llm_init import LLMInit


class ClassInforSchema(BaseModel):
    package: str = Field(description="package")
    clazz: str = Field(description="class")


class MethodInforSchema(ClassInforSchema):
    method: str = Field(description="method")


class VariableSchema(MethodInforSchema):
    variable: str = Field(description="variable")


class CodeTool:

    _instance = None
    method_information = dict()
    all_methods = list()
    class_information = dict()
    method_be_invoked = dict()
    file_path: str
    tool_agent: initialize_agent

    def __init__(self, file_path):
        self.file_path = file_path
        self.get_code_information()
        self.get_tool_agent()

    def get_tool_agent(self):
        tools = [
                StructuredTool.from_function(
                    func=self.be_invoked,
                    name='Get method invoked',
                    description="Get data about who invoked the method",
                    args_schema=MethodInforSchema
                ),
                StructuredTool.from_function(
                    func=self.get_method_metadata,
                    name='Get method metadata',
                    description='Get method metadata based on package, class and method',
                    args_schema=MethodInforSchema
                ),
                StructuredTool.from_function(
                    func=self.get_all_methods,
                    name='Get all methods',
                    description='Get all methods'
                ),
                StructuredTool.from_function(
                    func=self.get_all_classes,
                    name='Get all classes',
                    description='Get all classes'
                ),
                StructuredTool.from_function(
                    func=self.get_class_metadata,
                    name='Get class metadata',
                    description='Get class metadata based on package and class',
                    args_schema=ClassInforSchema
                )
            ]
        llm_init = LLMInit()
        self.tool_agent = initialize_agent(tools, llm_init.llm,
                                           agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                                           verbose=True)

    def get_code_information(self):
        code_summary = json.load(open(self.file_path))
        for class_info in code_summary:
            package = class_info['package']
            clazz = class_info['class']
            self.class_information[(package, clazz)] = class_info
            if 'methods' in class_info:
                for method in class_info['methods']:
                    self.all_methods.append({'package': package, 'class': clazz, 'method': method['methodName']})
                    method_tuple = (package, clazz, method['methodName'])
                    method['package'] = class_info['package']
                    method['class'] = class_info['class']
                    if 'memberVariables' in class_info:
                        method['classMemberVariables'] = class_info['memberVariables']
                    if 'constants' in class_info:
                        method['classConstants'] = class_info['constants']
                    if 'javaType' in class_info:
                        method['classType'] = class_info['javaType']
                    self.method_information[method_tuple] = method
                    for invoke_method in method['invoke']:
                        if 'this' == invoke_method['invokePackageName']:
                            invoke_method['invokePackageName'] = package
                        invoked_method_name = (invoke_method['invokePackageName'],
                                               invoke_method['invokeClassName'],
                                               invoke_method['invokeMethodName'])
                        method_result = {
                            "package": package,
                            "class": clazz,
                            "method": method['methodName']
                        }
                        if invoked_method_name not in self.method_be_invoked.keys():
                            self.method_be_invoked[invoked_method_name] = set()
                        self.method_be_invoked[invoked_method_name].add(json.dumps(method_result))

    def get_all_methods(self):
        return self.all_methods

    def get_all_classes(self):
        class_item = []
        for tuple_item in self.class_information.keys():
            class_item.append({"package": tuple_item[0], "class": tuple_item[1]})
        return class_item

    def get_class_metadata(self, package, clazz):
        if (package, clazz) in self.class_information.keys():
            return self.class_information[(package, clazz)]
        else:
            return dict()

    def be_invoked(self, package: str, clazz: str, method: str):
        path = (package, clazz, method)
        if path in self.method_be_invoked.keys():
            return self.method_be_invoked[path]
        else:
            return set()

    def get_method_metadata(self, package, clazz, method):
        path = (package, clazz, method)
        if path in self.method_information.keys():
            return self.method_information[path]
        if method is None:
            return self.get_class_metadata(package, clazz)

    def run(self, prompt):
        return self.tool_agent.run(prompt)


# code_tool = CodeTool('code_method_summary.json')
# pass