import dspy
from codeschematoolspec import CodeSchemaToolSpec
from llama_index.core.tools.tool_spec.base import BaseToolSpec
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import AgentRunner, ReActAgentWorker, ReActAgent
from llama_index.core.agent import ReActAgent


#QueryDecomposer Signature. 
class QueryDecomposerSignature(dspy.Signature):
    """
    Signature for a module that decomposes complex codebase questions into simpler, actionable sub-queries.
    """

    # Input field for the complex question about the codebase
    complex_question = dspy.InputField(
        desc="A complex question about the codebase that may require multi-faceted information."
    )

    # Output field for the list of simpler sub-queries
    simpler_queries = dspy.OutputField(
        desc="A list of 3 - 4 simpler, more focused , distinct queries derived from the complex question. Let the simpler queries be focused on modules , classes or functions"
    )

ollama_model = dspy.OllamaLocal(model="llama3:8b-instruct-fp16")

dspy.settings.configure(lm=ollama_model)

llm = Ollama(model="llama3:8b-instruct-fp16",request_timeout=30)

class CypherQuerySignature(dspy.Signature):
    """
    Signature for a module that decomposes complex codebase queries into simpler, actionable sub-queries.
    """

    # Input field for the complex question about the codebase
    question = dspy.InputField(
        desc="A question about a component of a code base , like class , function etc"
    )

    # Output field for the list of simpler sub-queries
    cypher_query = dspy.OutputField(
        desc="An equivalent cypherquery of the question"
    )


class CypherComposer(dspy.Module):

    def __init__(self):
        super().__init__()   
        self.generate_cyperquery = dspy.ChainOfThought(CypherQuerySignature)
    
    def forward(self,question):
        return self.generate_cyperquery(question=question)


class QueryDecomposer(dspy.Module):

    def __init__(self , max_hops=4):
        super().__init__()
        
        self.generate_smaller_query = dspy.ChainOfThought(QueryDecomposerSignature)
        self.max_hops = max_hops
        self.query_list = []
    

    def forward(self,question):
        query_blob = self.generate_smaller_query(complex_question = question).simpler_queries
        print(f" query blob {query_blob}")
        self.query_list = query_blob.strip().split('\n')
        print(f"sub query list {self.query_list}")
        return self.query_list
        
        


uncompiled_qd = QueryDecomposer()

uncompiled_cc = CypherComposer()

codetoolspec = CodeSchemaToolSpec()
react_agent = ReActAgent.from_tools(llm=llm, tools=CodeSchemaToolSpec().to_tool_list(), verbose=True)

def question_parse(question):
    pred = uncompiled_qd(question)
    for que in pred:
        print(f"subquestion : {que}")
        output = react_agent.chat(que)
        print(f"answer : {output}")



#Convert this to a ChatEngine
while True:
    user_input = input("Enter an question (or 'exit' to stop): ")
    
    if user_input == 'exit':
        break
    
    try:
        question = str(user_input)
        question_parse(question=question)
        #print("You entered the integer:", number)
    except ValueError:
        print("That's not a valid question. Try again.")
#print(pred)