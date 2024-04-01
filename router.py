from langchain.chains import MultiPromptChain
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from langchain.chains.router.llm_router import RouterOutputParser
from langchain.chains.router.llm_router import LLMRouterChain
from langchain.prompts import PromptTemplate
from llm_init.llm_init import LLMInit
from warehouse.cvm import CVM
from warehouse.code_meta import CodeMeta
from warehouse.database_change_logic import DataBaseChangeLogic


prompt_information = [
    {
        "name": "meta",
        "description": "Very professional when consulting method metadata, class metadata and database information"
    },
    {
        "name": "code_change_db",
        "description": "Very professional when analyze the logic for how the code change the database"
    },
    {
        "name": "cvm",
        "description": "Very professional when you want to upgrade library version"
    }
]
destinations = [f"{p['name']}: {p['description']}" for p in prompt_information]
destinations_str = "\n".join(destinations)

router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations_str)
router_prompt = PromptTemplate(
    template=router_template,
    input_variables=['input'],
    output_parser=RouterOutputParser(),
)

router_chain = LLMRouterChain.from_llm(LLMInit().llm, router_prompt)
default_chain = CodeMeta().overall_chain

destination_chains = dict()
destination_chains['meta'] = CodeMeta().overall_chain
destination_chains['code_change_db'] = DataBaseChangeLogic().overall_chain
destination_chains['cvm'] = CVM().get_llm_chain()


chain = MultiPromptChain(
    router_chain=router_chain,
    destination_chains=destination_chains,
    default_chain=default_chain,
    verbose=True,
)

print(chain.run("Upgrade spring-boot-start-parent library version from 3.1.5 to 3.2.3"))
# result = chain.run('what is the `product` table structure in database?')
# print(chain.run('Analyze the logic about how does the code insert values into `product.dc` database by using tool'))

pass