import json
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from internal_database.mongo_client import MongoDB
from llm_init.llm_init import LLMInit


class ORMExtractor:

    mongo_client = MongoDB()

    orm_prompt = """
            Please analyze the provided code and/or configuration file to extract the ORM (Object-Relational Mapping) information:

            1. Identify the ORM library or framework being used.
            2. List the database tables or entities defined in the code or configuration.
            3. For each entity or table, provide the following details:
               - Entity/table name
               - Attributes/columns with their data types
               - Relationships (if any) with other entities/tables
            4. Mention any additional ORM-specific configurations or mappings present in the code or configuration file.

            Please format the extracted information as a JSON object with the following structure:
            - `docPath`: <document path>
            - `ormFramework`: <ORM library or framework being used>
            - `package`: <corresponding package or orm namespace package>
            - `class`: <corresponding class or orm namespace class>
            - `resultMaps`: <List of result map>
                - `id`: <the name of result map>
                - `package`: <corresponding entity package> 
                - `class`: <corresponding entity class>
                - `mapping`: <the mapping between entity field and sql result column>
                    - `attribute`: <the name of the entity attribute>
                    - `column`: <the name of the column>
                - `relationships`: <Relationships (if any) with other resultMap>
                    - `type`: <relationship type>
                    - `target`: <target result map name>
            - `ORMMethods`: <list all orm methods>
                - `name`: <the method name or id>
                - `type`: <operation of method, like insert, update, delete and select>
                - `parameterType`: <corresponding parameter type>
                - `resultType`: 
                    - `package`: <corresponding result type package> 
                    - `class`: <corresponding result type class>
                - `resultMap`: <result map name>
                - `SQL`: <the sql of the method>

            Code (if applicable):
            {code}

            Configuration File (if applicable):
            {configuration}

            """

    def analyzer(self, code, configuration):
        orm_prompt_template = PromptTemplate.from_template(self.orm_prompt)
        orm_llm_chain = LLMChain(llm=LLMInit().llm, prompt=orm_prompt_template)
        response = orm_llm_chain.run(code=[code], configuration=[configuration]).replace("```json", '').replace("```", '')
        orm_response = json.loads(response)
        if 'ormFramework' in orm_response \
                and not (len(orm_response['resultMaps']) == 0 and len(orm_response['ORMMethods']) == 0) \
                and orm_response['ormFramework'] is not None \
                and 'Not' not in orm_response['ormFramework'] \
                and 'N/A' not in orm_response['ormFramework'] \
                and '' != orm_response['ormFramework'] \
                and 'No' not in orm_response['ormFramework']:
            self.mongo_client.insert_code_orm(orm_response)




