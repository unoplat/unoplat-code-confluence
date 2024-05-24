from typing import  List
from crewai_tools import BaseTool

class CurrentItem(BaseTool):
    name: str = "Get Class Metadata"
    description: str = "Use this tool to fetch latest class summary in string out of total classes. the tool will also throw error when there is no more data to fetch. No Need to pass any arguments to this tool"
    items: List[dict] = []
    total_items: int = 0
    curr_item_index: int = 0

    def __init__(self, items: List[dict]):
        super().__init__()
        self.items = items
        self.total_items = len(items)

    def _run(self) -> str: 
        if self.curr_item_index >= self.total_items:
            raise Exception("No more data exists to fetch")
        print(f"current index is {self.curr_item_index}")
        result = self.curr_item_index
        self.curr_item_index += 1
        return self.items[result]['summary']
