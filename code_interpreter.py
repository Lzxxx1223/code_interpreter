from code_analyzer.code_analyzer import CodeAnalyzer
from analyzer_agent.analyzer_agent import AnalyzerAgent
from code_db_mapping.code_change_db import CodeChangeDB
from db_analyzer.db_analyzer import DBAnalyzer
from classification.classification import Classification


class CodeInterpreter:

    code_analyzer_file_path: str
    db_sql_file_path: str
    analyzer_agent: AnalyzerAgent
    code_change_db: CodeChangeDB
    db_analyzer: DBAnalyzer

    def __init__(self, code_analyzer_file_path, db_sql_file_path):
        self.code_analyzer_file_path = code_analyzer_file_path
        self.db_sql_file_path = db_sql_file_path
        self.analyzer_agent = AnalyzerAgent(self.code_analyzer_file_path)
        self.code_change_db = CodeChangeDB(self.code_analyzer_file_path)
        self.db_analyzer = DBAnalyzer(self.db_sql_file_path)

    def code_interpreter(self, used_input):
        classification = Classification(self.db_sql_file_path)
        classification_result = classification.classification(used_input)
        if 'java code' in classification_result.lower():
            return self.analyzer_agent.basic_knowledge(used_input)
        elif 'database' in classification_result.lower():
            return self.db_analyzer.basic_information(used_input)
        elif 'both' in classification_result.lower():
            db_analyzer_response = self.db_analyzer.db_analyzer(used_input)
            code_change_db_response = self.code_change_db.code_change_db(db_analyzer_response)
            return self.analyzer_agent.code_interpreter(code_change_db_response)
        else:
            return "I cannot understand"


code_interpreter = CodeInterpreter('/Users/liuzhongxu/PycharmProjects/code_interpreter/code_analyzer/code_method_summary.json',
                                   '/Users/liuzhongxu/PycharmProjects/code_interpreter/db_analyzer/database.sql')

print('Please enter a question to get started!')
while True:
    question = input('')
    print(code_interpreter.code_interpreter(question))

# what is the `product` table structure in database?
# What is the explanation of the "link" method, "Process" class, "com.example.demo.service" package in java code
# How is the value of the attribute dca1 of pin 1 generated?