
from llama_index.core.llms import ChatMessage

from llama_index.llms.ollama import Ollama

llm = Ollama(model="llama3", request_timeout=30)

resp = llm.complete("who is paul graham ?")

#print(resp)

from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(
        role="system", content="You are a pirate with a colorful personality"
    ),
    ChatMessage(role="user", content="What is your name"),
]
resp = llm.stream_chat(messages)
print(resp)
print("here there")
for r in resp:
    print(r.delta, end="")

