import dspy


ollama_model = dspy.OpenAI(api_base='http://localhost:11434/v1/', api_key='ollama', model='llama3:latest', stop='\n\n', model_type='chat')

# This sets the language model for DSPy.
dspy.settings.configure(lm=ollama_model)

# This is not required but it helps to understand what is happening
my_example = {
    "question": "What game was Super Mario Bros. 2 based on?",
    "answer": "Doki Doki Panic",
}

# This is the signature for the predictor. It is a simple question and answer model.
class BasicQA(dspy.Signature):
    """Answer questions about classic video games."""

    question = dspy.InputField(desc="a question about classic video games")
    answer = dspy.OutputField(desc="often between 1 and 5 words")

# Define the predictor.
generate_answer = dspy.Predict(BasicQA)

print(generate_answer)

# Call the predictor on a particular input.
pred = generate_answer(question=my_example['question'])

# Print the answer...profit :)
print(pred.answer)



