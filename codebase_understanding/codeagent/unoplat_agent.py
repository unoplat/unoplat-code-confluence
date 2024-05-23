from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI
from codeagent.current_item import CurrentItem
import json
# Define tools (assuming some tools are already created, replace with actual tools if needed)
# from your_tool_library import SpecificTool1, SpecificTool2, SpecificTool3
import os


os.environ["OPENAI_API_KEY"] = "NA"

class UnoplatAgent:
    def __init__(self):
        self.md_spec_data = self.read_md_unoplat_spec('codebase_overview_spec.md')
        self.json_data = self.read_json_file('codebase_summary.json')
        self.output_file_reader_tool = FileReadTool(file_path="unoplat_tech_doc.md")
        self.item_reader_tool = CurrentItem(self.json_data)
        self.llm = ChatOpenAI(
            model="phi3:14b-medium-4k-instruct-q8_0",
            base_url="http://localhost:11434/v1"
        )
        self.agent1 = Agent(
            role='Data Engineer',
            goal="""Goal is to fetch data item from tool.""",
            backstory="""An experienced engineer who knows how to fetch data from the tool. 
            Post successful fetch format the data properly as per markdown syntax.
            The only reason if data is not returned is that we are done with entire data and there is no more data to process. When that happens it is time to shutdown and exit.""",
            memory=True,
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )
        # Create agents with memory enabled and specific goals and backstories
        self.agent2 = Agent(
            role='Software Engineer',
            goal="""The first transformation will be done here. First you will understand each and everything in the class metadata and the spec.
             Second you will convert the shared class metadata into component level information based on package responsibility
             and will prepare the markdown content based on the {unoplat_markdown_spec}. Pro tip: Keep the component name as package name.""",
            backstory="""An experienced engineer skilled in synthesizing complex data into actionable insights. You work
            for Unoplat a platform company which is stringent in following specifications.""",
            memory=True,
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )

        self.agent3 = Agent(
            role='Senior Software Engineer',
            goal="""the goal is to understand the refine overall summary based on current summary received.
            """,
            backstory="You are a senior software engineer with over 10 years of experience in writing codebase summary",
            memory=True,
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )

        self.agent4 = Agent(
            role='Senior Technical Documentation Specialist',
            goal="Analyze the evolving summary for accuracy and insights based on all available classes' metadata.",
            backstory="You work for Unoplat. A detail-oriented tech doc specialist who specializes in tech documentation and focuses on triggers and flow within the codebase.",
            memory=True,
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )

        self.agent5 = Agent(
            role='CommonMark Markdown specification Expert',
            goal="""Strictly check if it follows the CommonMark specification and make changes happen if it does not follow""",
            backstory="Been doing markdown validation since ages and have become an expert",
            memory=True,
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )

        self.manager_agent = Agent(
            role='Tech Doc Manager',
            goal="""Goal is to go over each data item from a list of items. Each item is fetched from Data Engineer and then converted into right unoplat markdown spec by
           Software Engineer and then current item summary is added to overall codebase summary again based on {unoplat_markdown_spec} by Senior Software Engineer.
             The testing of markdown spec based on commonmark and unoplat are overseen by CommonMark Markdown specification Expert and Senior Technical Documentation Specialist respectively """,
            backstory="You are a manager who knows how to manage the crew and ensure that the crew is working on the tasks in the right order and that the data is being passed between the agents correctly.",
            memory=True,
            verbose=True,
            llm=self.llm
        )

      
        # Define tasks
        self.task1 = Task(
            description='Fetch data from tool till end of items. Tool would tell if we have reached the end',
            expected_output='Nicely formatted and spaced markdown'
        )
        self.task2 = Task(
            description="""Now the goal is to output the content into markdown based on specification {unoplat_markdown_spec}.""",
            expected_output='Current summary of codebase in unoplat markdown spec.'
        )

        self.task3 = Task(
            description='Look at overall summary that we have and current summary for item that we received just now and then review and refine overall summary for accuracy and completeness according to the unoplat markdown spec based on {unoplat_markdown_spec}.',
            expected_output='Overall codebase Summary in markdown for all components which includes- Refined summary with corrections and keep it concise. Remember it is summary so focus is on components and its internal flows and external flows. Strictly do not include more than that.',
            
        )

        self.task4 = Task(
            description='Go line by line and check if the markdown file does not follow Unoplat markdown specification{unoplat_markdown_spec} .',
            expected_output='Unoplat based markdown - Final report incorporating all refinements in markdown following common mark specification.',
        )

        self.task5 = Task(
            description='Go line by line and check if the markdown file does not follow Common markdown specification.',
            expected_output='Commonmark based markdown - Final report incorporating all refinements in markdown following common mark specification.',
        )

        # Assemble the crew without a manager
        self.unoplat_crew = Crew(
            agents=[self.agent1, self.agent2, self.agent3,self.agent4,self.agent5],
            tasks=[self.task1, self.task2, self.task3, self.task4,self.task5],
            process='hierarchical', 
            manager_agent=self.manager_agent,
            verbose=2
        )

    def read_json_file(self, file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    def read_md_unoplat_spec(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()

    # Function to kick off the crew tasks iteratively
    def run_crew(self):
        
        self.unoplat_crew.kickoff
        (
            {'unoplat_markdown_spec': self.md_spec_data}
        )  # Process the current item

        print("Crew tasks completed. Check outputs for details.")
# Example usage




