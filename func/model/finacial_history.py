from datetime import datetime
from typing import List

class Row():
    description: str = ""
    value: float = 0.00

    def __init__(self, _desc:str,  _value: float):
        self.value = _value
        self.description = _desc
        pass   
    pass

class Period():
    date: datetime.date = None
    rows: List[Row] = []
    
    def __init__(self, _date: datetime.date):
        self.date = _date
        self.rows = []
        pass
    pass

class History():
    description: str = ''
    periods: List[Period] =[]

    def __init__(self, _desc: str):
        self.description = _desc
        self.periods = []
        pass
    pass

class FinancialHistory():
    code: str = ""
    dt_processing: str = "" 
    history: List[History] = []
    
    def __init__(self, _code: str, _dt_processing: str):
        self.code = _code
        self.dt_processing = _dt_processing
        self.history = []
        pass
    pass