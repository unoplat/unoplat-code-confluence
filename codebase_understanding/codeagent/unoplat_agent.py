from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI
import json
# Define tools (assuming some tools are already created, replace with actual tools if needed)
# from your_tool_library import SpecificTool1, SpecificTool2, SpecificTool3
import os
os.environ["OPENAI_API_KEY"] = "NA"



output_file_reader_tool = FileReadTool(file_path="unoplat_tech_doc.md")
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
    goal="Analyze the evolving summary for accuracy and insights based on all available classes' metadata.",
    backstory="You work for unoplat. A detail-oriented tech doc specialist who specializes in tech documentation and focuses on triggers and flow within the codebase.",
    memory=True,
    verbose=True,
    llm=llm,
    allow_delegation=False
    # tools=[SpecificTool2()]
)

agent3 = Agent(
    role='CommonMark Markdown specification Expert',
    goal="""Strictly check if it follows the CommonMark specification and make changes happen if it does not follow""",
    backstory="Been doing markdown validation since ages and have become an expert",
    memory=True,
    verbose=True,
    llm=llm,
    allow_delegation=False
    
    # tools=[SpecificTool3()]
)

# Define tasks
task1 = Task(
    description='Process and summarize class metadata {class_metadata} based on {unoplat_markdown_spec} .',
    agent=agent1,
    expected_output='Initial summary based on class metadata converted into component based info according to unoplat markdown spec.',
    output_file = 'unoplat_tech_doc.md'
)
task2 = Task(
    description="""Now the goal is to output the content into final markdown based file based on specification {unoplat_markdown_spec}. So use a tool to check
     if file exists or not. If it exists then read the content and then modify at the whole content based on current summary received if content already exists.
       Keep in mind always that The output carries overall summary of entire codebase.If file does not exist just output a new file. """,
    agent=agent1,
    expected_output='Overall summary of codebase in unoplat spec.',
    output_file = 'unoplat_tech_doc.md',
    context=[task1],
    tools=[output_file_reader_tool]
)

task3 = Task(
    description='Review and refine summary for accuracy and completeness according to the unoplat markdown spec based on {unoplat_markdown_spec}.',
    agent=agent2,
    expected_output='Refined summary with corrections and keep it concise. Remember it is summary the focus is on components and its internal flows and external flows. Strictly do not include more than that.',
    context=[task2],
    output_file = 'unoplat_tech_doc.md',

    
)

task4 = Task(
    description='Go line by line and check if the the markdown file does not follow markdown specification.',
    agent=agent3,
    expected_output='Final report incorporating all refinements in markdown following common mark specification.',
    context=[task3],
    output_file="unoplat_tech_doc.md"
)

# Assemble the crew without a manager
unoplat_crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[task1, task2, task3,task4],
    process='sequential',  # Sequential process to ensure order of task execution
    verbose=2
)

def read_json_file(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
        
def read_md_unoplat_spec(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to kick off the crew tasks iteratively
def run_crew():
    
    json_data = read_json_file('codebase_summary.json')
    md_spec_data = read_md_unoplat_spec('codebase_overview_spec.md')    
    # Process each item in the JSON data iteratively and dynamically
    for item in json_data:
        print("Processing item:", item['summary'])
        unoplat_crew.kickoff({'class_metadata': item,'unoplat_markdown_spec':md_spec_data})  # Process the current item

    print("Crew tasks completed. Check outputs for details.")

# Example usage
if __name__ == "__main__":
    run_crew()


