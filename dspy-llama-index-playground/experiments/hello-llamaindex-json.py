from llama_index.llms.ollama import Ollama
from llama_index.core.indices.struct_store import JSONQueryEngine
import json
from llama_index.core import PromptTemplate
from llama_index.core.tools import QueryEngineTool , ToolMetadata
from llama_index.core.agent import ReActAgent



#local model
llm = Ollama(model="llama3:8b-instruct-fp16", request_timeout=30)

# Load JSON schema and value from files
with open('conf/schema.json', 'r') as schema_file:
    json_schema = json.load(schema_file)

with open('conf/data.json', 'r') as data_file:
    json_value = json.load(data_file)

query_template_string= "You are an assistant who converts natural language query on json into a natural language response. No explanation needed."

json_query_template = PromptTemplate(query_template_string)

nl_query_engine = JSONQueryEngine(
    json_value=json_value,
    json_schema=json_schema,
    llm=llm,
)

raw_query_engine = JSONQueryEngine(
    json_value=json_value,
    json_schema=json_schema,
    llm=llm,
    synthesize_response=False,
)


nl_query_engine_tool_meta = ToolMetadata(
            name="blog_query",
            description=(
                "Provide information about blog posts"
                "Use a detailed plain text question as input to the tool."
            ),
        )
nl_query_engine_tool = QueryEngineTool(query_engine=nl_query_engine, metadata=nl_query_engine_tool_meta)

query_engine_tools = [nl_query_engine_tool]
react_agent = ReActAgent.from_tools(llm=llm, tools=query_engine_tools, verbose=True)
#print(raw_query_engine)
'''
nl_response = nl_query_engine.query(
    "What comments has Jerry been writing?",
)

raw_response = raw_query_engine.query(
    "What comments has Jerry been writing?",
)
print(f"Natural language response {raw_response}")

'''

while True:
    user_input = input("Enter an question (or 'exit' to stop): ")
    
    if user_input == 'exit':
        break
    
    try:
        question = str(user_input)
        
        #nl_response=nl_query_engine.query(question)
        nl_response=react_agent.chat(question)
        print(f" the nat response : {nl_response}")
        #print("You entered the integer:", number)
    except ValueError:
        print("That's not a valid question. Try again.")
#print(pred)

