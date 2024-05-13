#Class representing the toolspec for json query

from llama_index.core.tools.tool_spec.base import BaseToolSpec
from llama_index.llms.ollama import Ollama

from llama_index.core.agent import ReActAgent


func_spec_static = {
        "Name": "processMessage",
        "ReturnType": "CompletionStage<Void>",
        "Parameters": [
          {
            "TypeValue": "samplePojo",
            "TypeType": "SamplePojo"
          }
        ],
        "FunctionCalls": [
          {
            "Package": "org.acme.impl",
            "NodeName": "Math",
            "FunctionName": "sin",
            "Parameters": [
              {
                "TypeValue": "StrictMath.cos(res)",
                "TypeType": ""
              }
            ],
            "Position": {
              "StartLine": 19,
              "StartLinePosition": 28,
              "StopLine": 19,
              "StopLinePosition": 51
            }
          },
          {
            "Package": "org.acme.impl",
            "NodeName": "StrictMath",
            "FunctionName": "cos",
            "Parameters": [
              {
                "TypeValue": "res",
                "TypeType": ""
              }
            ],
            "Position": {
              "StartLine": 19,
              "StartLinePosition": 43,
              "StopLine": 19,
              "StopLinePosition": 50
            }
          },
          {
            "Package": "java.util.concurrent",
            "Type": "CHAIN",
            "NodeName": "CompletableFuture",
            "FunctionName": "completedStage",
            "Parameters": [
              {
                "TypeValue": "null",
                "TypeType": ""
              }
            ],
            "Position": {
              "StartLine": 22,
              "StartLinePosition": 37,
              "StopLine": 22,
              "StopLinePosition": 56
            }
          }
        ],
        "Position": {
          "StartLine": 14,
          "StartLinePosition": 11,
          "StopLine": 24,
          "StopLinePosition": 4
        },
        "LocalVariables": [
          {
            "TypeValue": "samplePojo",
            "TypeType": "SamplePojo"
          },
          {
            "TypeValue": "res",
            "TypeType": "double"
          },
          {
            "TypeValue": "i",
            "TypeType": "int"
          }
        ],
        "BodyHash": 258195030,
        "Content": "CompletionStage<Void> processMessage(SamplePojo samplePojo)    {            double res = 0;            for (int i = 0; i < 1000; i++) {                res += Math.sin(StrictMath.cos(res)) * 2;            }            samplePojo.waveFormData= samplePojo.waveFormData + res;            return CompletableFuture.completedStage(null);    "
      }

class CodeSchemaToolSpec(BaseToolSpec):
    """CodeSchema tool spec."""
    spec_functions = ["load_function", "load_module","load_class"]

    def __init__(self) -> None:
          super().__init__()
          

    def load_function(
          self, name
          
      )->str :
          """Fetch a list of relevant function."""
          #print(f"hello from the load_function function {name}")
          return str(func_spec_static)
    
    def load_module(
          self, name
      ) ->None:
          """Fetch a list of relevant modules."""
          print(f"hello from the load_module function {name}")
    def load_class(
          self,name
      ) -> str:
          """Fetch a list of relevant class."""
          print(f"hello from the load_class function {name}")
          return "Summary of class is class-summary"

def init():
      print("dry run")
      llm = Ollama(model="llama3:8b-instruct-fp16",request_timeout=30)
      codetoolspec = CodeSchemaToolSpec()
      react_agent = ReActAgent.from_tools(llm=llm, tools=CodeSchemaToolSpec().to_tool_list(), verbose=True)
      #react_agent.chat("What does the function hellothere do ?")
      output = react_agent.chat("Provide an overview of the function processMessage?")
      print(f"answer : {output}")

    
if __name__ == "__main__":
      init()