from langgraph.graph import StateGraph,START,END
from typing import TypedDict
from chatGpt import read_test_cases

class State(TypedDict):
    excel_path:str
    test_cases:list

def load_excel(state:State):
    test_cases=read_test_cases(state["excel_path"])
    return test_cases
