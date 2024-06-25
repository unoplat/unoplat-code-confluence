import dspy
from data_models.dspy.dspy_o_function_summary import DspyFunctionSummary
from data_models.dspy.dspy_unoplat_fs_function_subset import DspyUnoplatFunctionSubset
from data_models.dspy.dspy_unoplat_fs_node_subset import DspyUnoplatNodeSubset
import json
from data_models.chapi_unoplat_node import Node
from data_models.dspy.dspy_unoplat_fs_annotation_subset import DspyUnoplatAnnotationSubset
from data_models.dspy.dspy_unoplat_fs_function_call_subset import DspyUnoplatFunctionCallSubset
from data_models.dspy.dspy_unoplat_fs_function_subset import DspyUnoplatFunctionSubset
from data_models.dspy.dspy_unoplat_fs_node_subset import DspyUnoplatNodeSubset
from dspy.primitives.assertions import assert_transform_module, backtrack_handler


ollama_codestral = dspy.OllamaLocal(model='codestral:22b-v0.1-q8_0')
dspy.configure(lm=ollama_codestral)

ollama_llama_70b = dspy.OllamaLocal(model='llama3:70b-instruct')
dspy.configure(lm=ollama_llama_70b)

# gpt3.5-turbo = dspy.OpenAI(model='gpt-4-1106-preview', max_tokens=1000, model_type='chat')

# Define the signature for automatic assessments.
# class Assess(dspy.Signature):
#     """Assess the quality of a tweet along the specified dimension."""
#     assessed_text = dspy.InputField()
#     assessment_question = dspy.InputField()
#     assessment_answer = dspy.OutputField(desc="Yes or No")

# def metric(input, pred, trace=None):
#     question, answer, tweet = gold.question, gold.answer, pred.output

#     engaging = "Does the assessed text make for a self-contained, engaging tweet?"
#     correct = f"The text should answer `{question}` with `{answer}`. Does the assessed text contain this answer?"
    
#     with dspy.context(lm=gpt4T):
#         correct =  dspy.Predict(Assess)(assessed_text=tweet, assessment_question=correct)
#         engaging = dspy.Predict(Assess)(assessed_text=tweet, assessment_question=engaging)

#     correct, engaging = [m.assessment_answer.lower() == 'yes' for m in [correct, engaging]]
#     score = (correct + engaging) if correct and (len(tweet) <= 280) else 0

#     if trace is not None: return score >= 2
#     return score / 2.0

# import dspy
# from dspy.evaluate import Evaluate
# from dspy.evaluate.metrics import answer_exact_match
# from dspy.teleprompt.signature_opt_typed import optimize_signature

# turbo = dspy.OpenAI(model='gpt-3.5-turbo', max_tokens=4000)
# gpt4 = dspy.OpenAI(model='gpt-4', max_tokens=4000)
# dspy.settings.configure(lm=turbo)

# evaluator = Evaluate(devset=devset, metric=answer_exact_match, num_threads=10, display_progress=True)

# result = optimize_signature(
#     student=dspy.TypedPredictor(QASignature),
#     evaluator=evaluator,
#     initial_prompts=6,
#     n_iterations=100,
#     max_examples=30,
#     verbose=True,
#     prompt_model=gpt4,
# )


class CodeConfluenceFunctionSignature(dspy.Signature):
    """This signature contains class metadata and function metadata with function content and returns descriptive function summary. Strictly respond only with  dspy_function_summary in json format"""
    dspy_class_subset: DspyUnoplatNodeSubset = dspy.InputField(desc="This will contain class metadata in json")
    dspy_function_subset: DspyUnoplatFunctionSubset = dspy.InputField(desc="This will contain function metadata with function content in json")
    dspy_function_summary: DspyFunctionSummary = dspy.OutputField(desc="This will contain function summary in json")

# class CodeConfluenceFunctionSummaryOptimiserSignature(dspy.Signature):
#     """This signature contains function objective and implementation summary and returns factual and very concise function implementation summary and objective. Strictly respond only with  enhanced_objective_summary_output in json format"""
#     objective_summary_input: DspyFunctionSummary = dspy.InputField(alias="objective_summary_input",desc="This will contain function summary in json")
#     enhanced_objective_summary_output: DspyFunctionSummary = dspy.OutputField(alias="enhanced_objective_summary_output",desc="This will contain optimised function summary in json")


class CodeConfluenceFunctionModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_function_summary = dspy.TypedChainOfThought(CodeConfluenceFunctionSignature)
        # self.optimise_function_summary = dspy.TypedPredictor(CodeConfluenceFunctionSummaryOptimiserSignature)

    def forward(self, function_metadata, class_metadata):
        function_summary = self.generate_function_summary( dspy_class_subset = class_metadata, dspy_function_subset= function_metadata)
        # dspy.Suggest(
        #         "observe the error if any and correct the json structure",
        #     )
        print(function_summary)
        # optimised_function_summary = self.optimise_function_summary(objective_summary_input=function_summary.dspy_function_summary)
        # dspy.Suggest(
        #         "observe the error if any and correct the json structure",
        #     )
        # print(optimised_function_summary.enhanced_objective_summary_output)
        return function_summary
    

   
if __name__ == "__main__":
    #dspy_pipeline = assert_transform_module(CodeConfluenceFunctionModule(), backtrack_handler)
    #dspy_pipeline = CodeConfluenceFunctionModule()
    try:
        with open('springstarterjava1_codes.json', 'r') as file:
            springstarterjava1_codes = json.load(file)
    except FileNotFoundError:
        print("Error: File 'springstarterjava1_codes.json' not found.")
        springstarterjava1_codes = []
    except json.JSONDecodeError:
        print("Error: File 'springstarterjava1_codes.json' contains invalid JSON.")
        springstarterjava1_codes = []

    node_subsets = []

    function_subsets = []
    count = 0
    for item in springstarterjava1_codes:
        try:
            node = Node(**item)
            print("node name",node.node_name)
            node_subset = DspyUnoplatNodeSubset(
                NodeName=node.node_name,
                Imports=node.imports,
                Extend=node.extend,
                MultipleExtend=node.multiple_extend,
                Fields=node.fields,
                Annotations=[DspyUnoplatAnnotationSubset(Name=annotation.name,KeyValues=annotation.key_values) for annotation in node.annotations]
            )
            count = count + 1
            
            for func in node.functions:
                print(func)
                function_subset = DspyUnoplatFunctionSubset(
                    Name=func.name,
                    ReturnType=func.return_type,
                    Annotations=[DspyUnoplatAnnotationSubset(Name=annotation.name,KeyValues=annotation.key_values) for annotation in node.annotations],
                    LocalVariables=func.local_variables,
                    Content=func.content,
                    FunctionCalls=[DspyUnoplatFunctionCallSubset(NodeName=call.node_name, FunctionName=call.function_name, Parameters=call.parameters) for call in func.function_calls]
                )
                pred = dspy_pipeline(function_metadata=function_subset,class_metadata=node_subset)
                
        except AttributeError as e:
            print(f"Error processing node data: {e}")
    

    