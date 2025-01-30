from typing import List, Optional


def badly_formatted_function(   x:int,y:Optional[str]   =None)->List[str]:
    
    # Bad relative import
    
    results=[]
    if x>10:
        results.append(   str(x))
    if y:
        results.append(y)
    
    return results

class BadlyFormattedClass:
    def __init__(self,name:str):
        self.name=name
    
    def do_something(self,  input:List[int]   ):
        # Wrong import order
        
        return input 