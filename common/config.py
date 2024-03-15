import os


class Config:

    WEAVIATE_URL = 'http://localhost:8080'
    MONGO_URL = 'mongodb://localhost:27017'
    WEAVIATE_METHOD_COLLECTION = 'Method'
    WEAVIATE_CLASS_COLLECTION = 'Clazz'
    OPENAI_MODEL = 'gpt-3.5-turbo'
    SQL_DDL_DML_FILE_PATH = '/Users/liuzhongxu/PycharmProjects/code_interpreter/database.sql'
    CODE_PATH = '/Users/liuzhongxu/Documents/Learning/demo 2/src/main'
    os.environ['OPENAI_API_KEY'] = 'sk-hoZTk62z0b57ff585b04T3BlbKFJF9Ad5F81CC3d41f1BA4c'
    os.environ['OPENAI_API_BASE'] = 'https://api.ohmygpt.com/v1'

