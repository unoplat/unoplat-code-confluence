from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI
import json
# Define tools (assuming some tools are already created, replace with actual tools if needed)
# from your_tool_library import SpecificTool1, SpecificTool2, SpecificTool3
import os
os.environ["OPENAI_API_KEY"] = "NA"


file_reader_tool = FileReadTool(file_path="codebase_overview_spec_copy.md")
llm = ChatOpenAI(
    model = "phi3:14b-medium-4k-instruct-q8_0",
    base_url = "http://localhost:11434/v1")

# Create agents with memory enabled and specific goals and backstories
agent1 = Agent(
    role='Senior Software Engineer',
    goal="""User will be sharing one class metadata at a time based on standard markdown spec. Then First you will read a file using a tool.
    Second if it is a first time the file will just have placeholders. Third you will understand the data shared from user
     precisely. Fourth job is to convert the information got from user into component level information based on package
     and to fill in the markdown spec. Then gradually keep improving it.""",
    backstory="""An experienced engineer skilled in synthesizing complex data into actionable insights. You work
    for Unoplat a platform company which is strigent in following specifications.""",
    memory=True,
    verbose=True,
    llm=llm,
    allow_delegation=False,
    tools=[file_reader_tool]
)

agent2 = Agent(
    role='Senior Tech Documentation Specialist',
    goal="Analyze the evolving summary for accuracy and insights based on all available classes' metadata use memory for the same.",
    backstory="You work for unoplat. A detail-oriented tech doc specialist who specializes in data interpretation and error correction.",
    memory=True,
    verbose=True,
    llm=llm,
    tools=[file_reader_tool]
    # tools=[SpecificTool2()]
)

agent3 = Agent(
    role='Unoplat Tech Report Generator',
    goal="""Generate and refine comprehensive report from analyzed data and check if it follows the provided 
    unoplat markdown spec and it is CommonMark markdown compliant.
    u.""",
    backstory="Dedicated to producing detailed and accurate documentation, adapting to new information.",
    memory=True,
    verbose=True,
    llm=llm
    
    # tools=[SpecificTool3()]
)

# Define tasks
task1 = Task(
    description='Process and summarize class metadata {class_metadata} and append it to the existing unoplat markdown based summary if available.',
    agent=agent1,
    expected_output='Initial summary based on class metadata in unoplat markdown spec. Append/Modify. Never overwrite.',
    output_file = 'unoplat_tech_doc.md'
)

task2 = Task(
    description='Review and refine summary for accuracy and completeness according to the markdown spec based on file.',
    agent=agent2,
    expected_output='Refined summary with corrections and additional insights',
    output_file = 'unoplat_tech_doc.md' 
)

task3 = Task(
    description='Go line by line and improve final, comprehensive report based on refined summaries',
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


