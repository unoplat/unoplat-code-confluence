# from typing import Any, List
# from crewai_tools import BaseTool

# class CurrentItem(BaseTool):
#     name: str = "Get class summary."
#     description: str = "Use this tool to get current class summary. The tool will throw an error when we have reached end of items."
    

#     def __init__(self, items: List[dict]):
#         self.items = items
#         self.total_items = len(items)
#         self.curr_item = 0

#     def _run(self, **kwargs: Any) -> str:
#         if self.curr_item >= self.total_items:
#             raise Exception("No more data exists to fetch")
#         result = self.curr_item
#         self.curr_item += 1
#         return self.items[result]['summary']
