from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI
import json
# Define tools (assuming some tools are already created, replace with actual tools if needed)
# from your_tool_library import SpecificTool1, SpecificTool2, SpecificTool3
import os
os.environ["OPENAI_API_KEY"] = "NA"


file_reader_tool = FileReadTool(file_path="codebase_overview_spec_copy.md")
output_file_reader_tool = FileReadTool(file_path="unoplat_tech_doc.md.md")
llm = ChatOpenAI(
    model = "phi3:14b-medium-4k-instruct-q8_0",
    base_url = "http://localhost:11434/v1")

# Create agents with memory enabled and specific goals and backstories
agent1 = Agent(
    role='Senior Software Engineer',
    goal="""User will be sharing one class metadata at a time based on standard markdown spec. Then First you will a specification read a file using a tool.
     Second you will understand the spec and make sure based on the data shared from user
     lands into that spec. Third you will convert the shared class metadata into component level information based on package responsibility
     and to fill in the markdown spec.Keep the component name as package name
     Now the goal is to output the content into final markdown based file. So use a tool to check
     if file exists or not. If it exists then read the content and then modify/append at appropriate position.
     If file does not exist just output a new file. From nexttime onwards the file will exist""",
    backstory="""An experienced engineer skilled in synthesizing complex data into actionable insights. You work
    for Unoplat a platform company which is strigent in following specifications.""",
    memory=True,
    verbose=True,
    llm=llm,
    allow_delegation=False
)

agent2 = Agent(
    role='Senior Tech Documentation Specialist',
    goal="Analyze the evolving summary for accuracy and insights based on all available classes' metadata use [] for the same.",
    backstory="You work for unoplat. A detail-oriented tech doc specialist who specializes in data interpretation and error correction.",
    memory=True,
    verbose=True,
    llm=llm
    # tools=[SpecificTool2()]
)

agent3 = Agent(
    role='CommonMark Markdown specification Expert',
    goal="""Strictly check if it follows the CommonMark specification and make changes happen if it does not follow""",
    backstory="Been doing markdown validation since ages and have become an expert",
    memory=True,
    verbose=True,
    llm=llm
    
    # tools=[SpecificTool3()]
)

# Define tasks
task1 = Task(
    description='Process and summarize class metadata {class_metadata} and .',
    agent=agent1,
    expected_output='Initial summary based on class metadata converted into component based info according to unoplat markdown spec.',
    output_file = 'unoplat_tech_doc.md',
    tools=[file_reader_tool]
)
task2 = Task(
    description="""Now the goal is to output the content into final markdown based file. So use a tool to check
     if file exists or not. If it exists then read the content and then modify/append at appropriate position. Keep in mind
     always that The output file carries overall summary of entire codebase.If file does not exist just output a new file. From nexttime onwards the file will exist""",
    agent=agent1,
    expected_output='Overall summary of codebase in unoplat spec.',
    output_file = 'unoplat_tech_doc.md',
    tools=[output_file_reader_tool]
)

task3 = Task(
    description='Review and refine summary for accuracy and completeness according to the unoplat markdown spec based on file.',
    agent=agent2,
    expected_output='Refined summary with corrections and additional insights',
    output_file = 'unoplat_tech_doc.md',
    tools=[file_reader_tool]
)

task4 = Task(
    description='Go line by line and check if the the markdown file does not follow markdown specification.',
    agent=agent3,
    expected_output='Final report incorporating all refinements in markdown following common mark specification.',
    output_file="unoplat_tech_doc.md"
)

# Assemble the crew without a manager
unoplat_crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[task1, task2, task3],
    process='sequential',  # Sequential process to ensure order of task execution
    verbose=2
)

# Function to kick off the crew tasks iteratively
def run_crew():
    

    def read_json_file(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    json_data = read_json_file('codebase_summary.json')
    
    # Process each item in the JSON data iteratively and dynamically
    for item in json_data:
        print("Processing item:", item['summary'])
        unoplat_crew.kickoff({'class_metadata': item})  # Process the current item

    print("Crew tasks completed. Check outputs for details.")

# Example usage
if __name__ == "__main__":
    run_crew()


