from llama_index.core.tools import FunctionTool

def calculate_average(values: list[float]) -> float: 
    """
    Calculates the average of the provided values.
    """
    return sum(values) / len(values)
average_tool = FunctionTool.from_defaults(
    fn=calculate_average
)
