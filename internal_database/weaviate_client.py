import weaviate
from common.config import Config
from langchain.embeddings import OpenAIEmbeddings


def singleton(cls, *args, **kwargs):

    instances = {}

    def wrapper():
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper


@singleton
class WeaviateClient:

    weaviate_client = None
    weaviate_method = {"class": Config.WEAVIATE_METHOD_COLLECTION}
    weaviate_class = {"class": Config.WEAVIATE_CLASS_COLLECTION}
    weaviate_raw = {"class": Config.WEAVIATE_RAW_COLLECTION}

    def __init__(self):
        self.weaviate_client = weaviate.Client(Config.WEAVIATE_URL)
        response = self.weaviate_client.schema.get()
        method_exist = False
        class_exist = False
        raw_exist = False
        for item in response['classes']:
            if self.weaviate_method['class'].lower() == item['class'].lower():
                method_exist = True
            if self.weaviate_class['class'].lower() == item['class'].lower():
                class_exist = True
            if self.weaviate_raw['class'].lower() == item['class'].lower():
                raw_exist = True
        if not method_exist:
            self.weaviate_client.schema.create_class(self.weaviate_method)
        if not class_exist:
            self.weaviate_client.schema.create_class(self.weaviate_class)
        if not raw_exist:
            self.weaviate_client.schema.create_class(self.weaviate_raw)

    def create_object(self, class_name, data, vector):
        self.weaviate_client.data_object.create(
            class_name=class_name,
            data_object=data,
            vector=vector
        )

    def delete_collection(self, class_name):
        self.weaviate_client.schema.delete_class(class_name)

    def get_method_explanation(self, user_query, limit=10):
        return self.weaviate_client.query \
            .get(Config.WEAVIATE_METHOD_COLLECTION, ["package", "class", "method"]) \
            .with_near_vector({"vector": OpenAIEmbeddings().embed_query(user_query)}) \
            .with_limit(limit) \
            .do()['data']['Get'][Config.WEAVIATE_METHOD_COLLECTION]

    def get_class_explanation(self, user_query, limit=10):
        return self.weaviate_client.query \
            .get(Config.WEAVIATE_CLASS_COLLECTION, ["package", "class"]) \
            .with_near_vector({"vector": OpenAIEmbeddings().embed_query(user_query)}) \
            .with_limit(limit) \
            .do()['data']['Get'][Config.WEAVIATE_CLASS_COLLECTION]

    def get_raw_explanation(self, user_query, limit=10):
        return self.weaviate_client.query \
            .get(Config.WEAVIATE_RAW_COLLECTION, ["text", "source"]) \
            .with_near_vector({"vector": OpenAIEmbeddings().embed_query(user_query)}) \
            .with_limit(limit) \
            .do()['data']['Get'][Config.WEAVIATE_RAW_COLLECTION]


# WeaviateClient().delete_collection(Config.WEAVIATE_CLASS_COLLECTION)
# WeaviateClient().delete_collection(Config.WEAVIATE_METHOD_COLLECTION)
# WeaviateClient().delete_collection(Config.WEAVIATE_RAW_COLLECTION)
# print(WeaviateClient().weaviate_client.schema.get())
# pass