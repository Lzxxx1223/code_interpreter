from code_analyzer.code_tool import CodeTool


class CodeChangeDB:

    file_path: str
    code_tool: CodeTool
    prompt = """            
            Based on the class `{class}` package `{package}` metadata.
            If class javaType not `interface` then analyze the explanation, member variables and constant of the class metadata,
            to determine whether this class can change the database table `{table}` under database schema `{schema}`
            
            Provide them in JSON format with the following keys:
            - `hasRelated`: <whether this class is related the table, True or False>
            - `method`: <method name, if none then remove this field>
            - `class`:  <class name>
            - `package`: <package name>
            - `variable`: <constant name related to table `{table}` and schema `{schema}`, if none then remove this field>
            """

    def __init__(self, file_path):
        self.file_path = file_path
        self.code_tool = CodeTool(self.file_path)

    def code_change_db(self, input_db_data):
        result = list()
        classes = self.code_tool.get_all_classes()
        for clazz in classes:
            final_prompt = (self.prompt
                            .replace('{table}', input_db_data['table'])
                            .replace('{schema}', input_db_data['schema'])
                            .replace('{class}', clazz['class'])
                            .replace('{package}', clazz['package']))
            response = self.code_tool.run(final_prompt)
            if isinstance(response, dict) and response['hasRelated']:
                final_response = dict()
                final_response['package'] = response['package']
                final_response['class'] = response['class']
                final_response['type'] = 'class'
                if 'variable' in response and response['variable'] is not None:
                    final_response['variable'] = response['variable']
                    final_response['type'] = 'variable'
                if 'method' in response and response['method'] is not None:
                    final_response['method'] = response['method']
                    final_response['type'] = 'method'
                result.append(final_response)
        return result


# input_data = {
#     "schema": "product",
#     "table": "dc",
#     "column": "dca1"
# }
# code_change_db = CodeChangeDB('/Users/liuzhongxu/PycharmProjects/code_interpreter/code_analyzer/code_method_summary.json')
# print(code_change_db.code_change_db(input_data))
#
# input_data = [
#     {'hasRelated': True, 'method': None, 'class': 'EnumType', 'package': 'com.example.demo.entity',
#      'constantsName': 'PRODUCT', 'javaType': 'enum',
#      'reason': "The class has a constant related to the table 'dc' under schema 'product'."
#      },
#     {'hasRelated': True, 'method': 'processVin', 'class': 'ProcessController', 'package': 'com.example.demo.controller',
#      'constantsName': None, 'javaType': 'class',
#      'reason': "The 'processVin' method in the 'ProcessController' class can directly change the database table 'dc' under the database schema 'product' "
#                "by invoking the 'link' method of the 'Process' class."
#      },
#     {'hasRelated': True, 'method': None, 'class': 'Mapping', 'package': 'com.example.demo.model', 'constantsName': None, 'javaType': 'class',
#      'reason': 'The class has member variables that could be related to the table, but without methods or constants specifically '
#                'related to the table `dc` under schema `product`, direct changes cannot be determined.'
#      },
#     {'hasRelated': True, 'method': None, 'class': 'DC', 'package': 'com.example.demo.model', 'constantsName': None, 'javaType': 'class',
#      'reason': 'The class has constructors and member variables that could be used to directly '
#                'change the database table `dc` under the database schema `product`.'
#      },
#     {'hasRelated': True, 'method': 'link', 'class': 'Process', 'package': 'com.example.demo.service',
#      'constantsName': 'vin', 'javaType': 'class',
#      'reason': "The class can change the table by invoking the 'link' method which interacts "
#                "with various classes to insert data into the database."
#      },
#     {'hasRelated': True, 'method': 'loadSchema', 'class': 'InitService', 'package': 'com.example.demo.service',
#      'constantsName': None, 'javaType': 'class',
#      'reason': 'This class can change the database table `dc` under the database schema `product` through the `loadSchema` method.'
#      },
#     {'hasRelated': True, 'method': 'insertSt', 'class': 'ProductWrite', 'package': 'com.example.demo.service',
#      'constantsName': None, 'javaType': 'class',
#      'reason': "The method insertSt in the ProductWrite class is related to changing the database table 'dc' under the database schema 'product'."
#      }
# ]