from typing import List, Tuple

#credentials to this class AI
class Action:
    """
    Class with an action to be executed in the datacube.
    """
    def __init__(self, op_type: str, operands: List, **kwargs):
        self.op_type = op_type
        self.operands = operands
        self.kwargs = kwargs# Assuming slices is passed as a keyword argument



