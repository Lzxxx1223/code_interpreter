from code_analyzer.code_tool import CodeTool


class MethodParameterAgent:

    code_tool: CodeTool
    prompt = """
            FInd all global variables changed 
            in this method `{method}`, package `{package}` and class `{clazz}`, 
            
            Provide them in JSON format with the following keys:            
            - `hasVariable`: <whether the method changed the global variables, value should be True or False>
            - `name`: <global variable name>
            - `type`: <global variable java type>
            - `method`: <method name>
            - `class`:  <class name>
            - `package`: <package name>
            """

    def __init__(self, code_tool):
        self.code_tool = code_tool

    def global_variables_changed_in_method(self, input_data):
        final_prompt = (self.prompt
                        .replace('{method}', input_data['method'])
                        .replace('{package}', input_data['package'])
                        .replace('{clazz}', input_data['class']))
        variable_analyser = self.code_tool.run(final_prompt)
        if isinstance(variable_analyser, str):
            no_parameter = dict()
            no_parameter['hasVariable'] = False
            return no_parameter
        return variable_analyser

