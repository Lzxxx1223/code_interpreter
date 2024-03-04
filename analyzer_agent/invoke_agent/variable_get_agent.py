from code_analyzer.code_tool import CodeTool


class VariableGetAgent:

    code_tool: CodeTool
    prompt = """
            Find all methods in the class `{clazz}`, package `{package} `
            can directly return the global variable `{variable}`
            
            Provide them in JSON format with the following keys:
            - `hasMethod` : <whether the method changed the global variables, value should be True or False>
            - `method` : <method name>
            - `class` :  <class name>
            - `package` : <package name>
            """

    def __init__(self, code_tool):
        self.code_tool = code_tool

    def variables_used(self, input_data):
        final_prompt = (self.prompt
                        .replace('{variable}', input_data['variable'])
                        .replace('{package}', input_data['package'])
                        .replace('{clazz}', input_data['class']))
        variable_analyser = self.code_tool.run(final_prompt)
        if isinstance(variable_analyser, str):
            no_parameter = dict()
            no_parameter['hasMethod'] = False
            return no_parameter
        return variable_analyser

