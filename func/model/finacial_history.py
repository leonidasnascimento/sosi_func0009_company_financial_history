from datetime import datetime
from typing import List

class History():
    description: str = ""
    date: datetime.date = None
    value: float = 0.00

    def __init__(self, _desc:str, _date: datetime.date, _value: float):
        self.date = _date
        self.value = _value
        self.description = _desc
        pass
    pass

class FinancialHistory():
    code: str = ""
    dt_processing: str = "" 
    balance_sheet: List[History] = []
    cash_flow: List[History] = []
    
    def __init__(self, _code: str, _dt_processing: str):
        self.code = _code
        self.dt_processing = _dt_processing
        self.cash_flow = []
        self.balance_sheet = []
        pass
    pass