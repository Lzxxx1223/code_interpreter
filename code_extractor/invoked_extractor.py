import json
from internal_database.mongo_client import MongoDB


class InvokedExtractor:

    mongo_client = MongoDB()

    def analyzer(self):
        final_result = dict()
        methods = list(self.mongo_client.mongo_code_method.find())
        for method in methods:
            invoked_dict = dict()
            invoked_dict['package'] = method['package']
            invoked_dict['class'] = method['class']
            invoked_dict['method'] = method['name']
            if 'invocations' in method:
                for invocation in method['invocations']:
                    key_tuple = (invocation['package'], invocation['class'], invocation['method'])
                    if key_tuple not in final_result:
                        final_result[key_tuple] = set()
                    final_result[key_tuple].add(json.dumps(invoked_dict))

        for key_tuple, invoked in final_result.items():
            result_list = list()
            for invoked_item in invoked:
                result_list.append(json.loads(invoked_item))
            self.mongo_client.mongo_code_method.update_one({'package': key_tuple[0], 'class': key_tuple[1], 'name': key_tuple[2]},
                                                           {"$set": {'beInvoked': result_list}})


# InvokedExtractor().analyzer()