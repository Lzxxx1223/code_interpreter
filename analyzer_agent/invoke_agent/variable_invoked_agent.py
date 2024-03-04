import json
from code_analyzer.code_tool import CodeTool


class VariableInvokedAgent:

    code_tool: CodeTool
    prompt = """
            Based on the metadata of the class `{class}` package `{package}`, 
            Analyze the member variables, static variables and each method explanation in the class metadata to determine whether they are related to the variable `{variable}`

            Provide them in JSON format with the following keys:
            - `hasRelated` : <whether the method related this variable, value should be True or False>
            - `method` : <method name>
            - `class` :  <class name>
            - `package` : <package name>
            """

    def __init__(self, code_tool):
        self.code_tool = code_tool

    def variables_invoked(self, input_data):
        result = list()
        classes = self.code_tool.get_all_classes()
        for clazz in classes:
            final_prompt = (self.prompt
                            .replace('{variable}', input_data['variable'])
                            .replace('{class}', clazz['class'])
                            .replace('{package}', clazz['package']))
            response = self.code_tool.run(final_prompt)
            print(response)
            if isinstance(response, str) and 'hasRelated' in response and response.startswith('{') and response.endswith('}'):
                try:
                    response = json.loads(response)
                finally:
                    pass
            if isinstance(response, dict) and 'hasRelated' in response:
                if isinstance(response['hasRelated'], list):
                    for item in response['hasRelated']:
                        if 'hasRelated' in item and item['hasRelated']:
                            result.append(item)
                elif response['hasRelated']:
                    result.append(response)
        return result


# global_input_data = dict()
# global_input_data['variable'] = 'EnumType.Product'
# global_code_tool = CodeTool('/Users/liuzhongxu/PycharmProjects/code_interpreter/code_analyzer/code_method_summary.json')
# invoke_method_agent = VariableInvokedAgent(global_code_tool)
# print(invoke_method_agent.variables_invoked(global_input_data))

# result = [
#     {'hasRelated': True, 'method': 'EnumType.Product', 'class': 'EnumType', 'package': 'com.example.demo.entity'},
#     {'hasRelated': True, 'method': 'init', 'class': 'InitService', 'package': 'com.example.demo.service'},
#     {'hasRelated': True, 'method': 'loadSchema', 'class': 'InitService', 'package': 'com.example.demo.service'}
# ]
