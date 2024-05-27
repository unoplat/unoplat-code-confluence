import dspy
from dspy.datasets.gsm8k import GSM8K , gsm8k_metric

gsm8k = GSM8K()

gsm8k_trainset , gsm8k_devset = gsm8k.train[:10] , gsm8k.dev[:10]

#print(gsm8k_trainset)

#ollama_model = dspy.OpenAI(api_base='http://localhost:11434/v1/', api_key='ollama', model='llama3:latest', stop='\n\n', model_type='chat')

ollama_model = dspy.OllamaLocal(model='llama3:latest')

dspy.settings.configure(lm=ollama_model)

class CoT(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought("question -> answer")
    
    def forward(self, question):
        return self.prog(question=question)
    

from dspy.teleprompt import BootstrapFewShot

# Set up the optimizer: we want to "bootstrap" (i.e., self-generate) 4-shot examples of our CoT program.
config = dict(max_bootstrapped_demos=4, max_labeled_demos=4)

# Optimize! Use the `gsm8k_metric` here. In general, the metric is going to tell the optimizer how well it's doing.
teleprompter = BootstrapFewShot(metric=gsm8k_metric, **config)
optimized_cot = teleprompter.compile(CoT(), trainset=gsm8k_trainset, valset=gsm8k_devset)

from dspy.evaluate import Evaluate

# Set up the evaluator, which can be used multiple times.
evaluate = Evaluate(devset=gsm8k_devset, metric=gsm8k_metric, num_threads=4, display_progress=True, display_table=0)

# Evaluate our `optimized_cot` program.
evaluate(optimized_cot)

ollama_model.inspect_history(n=1)

response = optimized_cot(question='Cameron is printing her thesis in the school library and has 400 A4 pieces of paper. If 40% of the papers did not print out up to her desired quality and she separated them as invalid, calculate the total number of valid documents.')
print(response)

