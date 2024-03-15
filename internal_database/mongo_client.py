from typing import Mapping, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from common.config import Config


def singleton(cls, *args, **kwargs):

    instances = {}

    def wrapper():
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper


@singleton
class MongoDB:

    mongo_client = MongoClient(Config.MONGO_URL)
    mongo_db: Database[Mapping[str, Any]]
    mongo_code_method: Collection[Mapping[str, Any]]
    mongo_code_class: Collection[Mapping[str, Any]]
    mongo_code_orm: Collection[Mapping[str, Any]]

    def __init__(self):
        self.mongo_db = self.mongo_client['code-interpreter']
        self.mongo_code_method = self.mongo_db['code-method']
        self.mongo_code_class = self.mongo_db['code-class']
        self.mongo_code_orm = self.mongo_db['code-orm']

    def insert_code_class(self, class_item):
        self.mongo_code_class.insert_one(class_item)

    def insert_code_method(self, method_item):
        self.mongo_code_method.insert_one(method_item)

    def insert_code_orm(self, ora_item):
        self.mongo_code_orm.insert_one(ora_item)

    def get_all_methods(self):
        return list(self.mongo_code_method.find({}, {'_id': 0, 'package': 1, 'class': 1, 'name': 1}))

    def get_all_classes(self):
        return list(self.mongo_code_class.find({}, {'_id': 0, 'package': 1, 'class': 1}))

    def get_all_orm(self):
        return list(self.mongo_code_orm.find({}, {"_id": 0}))

    def get_method_metadata(self, package, clazz, method):
        return self.mongo_code_method.find_one({'package': package, 'class': clazz, 'name': method}, {"_id": 0})

    def get_class_metadata(self, package, clazz):
        return self.mongo_code_class.find_one({'package': package, 'class': clazz}, {"_id": 0})

    def get_methods_in_class(self, package, clazz):
        return list(self.mongo_code_method.find({'package': package, 'class': clazz}, {"_id": 0}))

