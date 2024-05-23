from typing import List
from crewai_tools import BaseTool

class CurrentItem(BaseTool):
    name: str = "Current item processed out of total items"
    description: str = "Use this tool to figure out current item processed out of total items"
    items: List[dict] = []
    total_items: int = 0


    def __init__(self, items: List[dict]):
        super().__init__()
        self.items = items
        self.total_items = len(items)

    def _run(self, args: str) -> str:
        if self.curr_item >= self.total_items:
            raise Exception("No more data exists to fetch")
        result = self.curr_item
        self.curr_item += 1
        return self.items[result]['summary']
