import copy
from code_analyzer.code_tool import CodeTool


class InvokeMethodAgent:

    code_tool: CodeTool
    prompt = """
            Who invoked the method : `{method}`, package `{package}` and class `{clazz}`, 
            
            Provide them in JSON format with the following keys:
            - `hasInvoked`: <whether the method has the invoked method, True or False>
            - `method`: <invoke method name>
            - `class`: <invoke method class name>
            - `package`: <invoke method package name>
            """

    def __init__(self, code_tool):
        self.code_tool = code_tool

    def get_invoke_method(self, package, clazz, method):
        final_prompt = (self.prompt
                        .replace('{method}', method)
                        .replace('{package}', package)
                        .replace('{clazz}', clazz))
        invoke_chain_analyser = self.code_tool.run(final_prompt)
        if isinstance(invoke_chain_analyser, str):
            no_invoke_response = dict()
            no_invoke_response['hasInvoked'] = False
            return no_invoke_response
        elif len(invoke_chain_analyser) == 1:
            return list(invoke_chain_analyser.values())[0]
        else:
            return invoke_chain_analyser

    def get_invoke_chain(self, input_data):
        init = True
        invoke_chain = list()
        while init or (isinstance(input_data, dict) and 'hasInvoked' in input_data and input_data['hasInvoked']):
            input_data = self.get_invoke_method(input_data['package'], input_data['class'], input_data['method'])
            if isinstance(input_data, dict):
                if input_data['hasInvoked']:
                    invoke_chain.append(copy.deepcopy(input_data))
                init = False
            else:
                init = False
        return invoke_chain

#
# global_input_data = dict()
# global_input_data['package'] = 'com.example.demo.service'
# global_input_data['class'] = 'ProductWrite'
# global_input_data['method'] = 'insertSt'
# global_code_tool = CodeTool('../../code_analyzer/code_method_summary.json')
# invoke_method_agent = InvokeMethodAgent(global_code_tool)
# print(invoke_method_agent.get_invoke_chain(global_input_data))