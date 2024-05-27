import dspy

ollama_3 = dspy.OllamaLocal(model='llama3:latest')

print(ollama_3("how many zeroes are there in 1000?"))

#ollama_3.inspect_history(n=1)

dspy.settings.configure(lm=ollama_3)
qa = dspy.ChainOfThought('question -> answer', n=3)

response = qa(question="how many zeroes are there in 1000")

print(response.answer)


#check sentiment analysis

predict_signature = dspy.Predict('sentence -> sentiment')
sentence = "it's a charming and often affecting journey." 

response = predict_signature(sentence=sentence)

print(response.sentiment)

#check chainofthought

context = "explain like i were 5 year old"
cot_signature = dspy.ChainOfThought('question,context -> answer')

question = "why is the sky so blue ?"

response = cot_signature(question=question,context=context)

print(response.answer)

question = "What's something nice about the ColBERT retrieval model?"

# 1) Declare with a signature, and pass some config.
classify = dspy.ChainOfThought('question -> answer', n=5)

# 2) Call with input argument.
response = classify(question=question)

# 3) Access the outputs.
#print(response.completions.answer)
print(f"Rationale : {response.rationale}")
print(f"Answer : {response.answer}")


