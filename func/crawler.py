import sys
import time
import threading
import re
import requests

from typing import List
from datetime import (date, datetime)
from .model.finacial_history import (FinancialHistory, History)
from .parser import Parser
from bs4 import (BeautifulSoup, Tag)

# FIELDS
FIELD_SHARED_DIVIDENDS = "Dividendos Pagos"
FIELD_NET_INCOME = "Lucro Líquido"
FIELD_NET_WORTH = "Patrimônio Líquido Total"

class Crawler():
    url_balance_sheet: str = ""
    url_cash_flow: str = ""
    dt_processing: str = ""
    financial_history: FinancialHistory = None
    request_headers = {
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            'cache-control': "no-cache",
            'postman-token': "146ba02b-dc25-fb1a-9fbc-a8df1248db26"
        }

    def __init__(self, _url_cash_flow: str, _url_balance_sheet: str, _dt_processing: str):
        self.url_balance_sheet = _url_balance_sheet
        self.url_cash_flow = _url_cash_flow
        self.dt_processing = _dt_processing
        pass

    def get_data(self, _stock_code: str) -> FinancialHistory:
        self.financial_history = FinancialHistory(_stock_code, self.dt_processing)
        
        # Cash flow
        self.financial_history.cash_flow.extend(self.__setHistoryDate(FIELD_SHARED_DIVIDENDS,_stock_code, self.url_cash_flow, True))
        self.financial_history.cash_flow.extend(self.__setHistoryDate(FIELD_NET_INCOME, _stock_code, self.url_cash_flow, False))
        
        # Balance Sheet
        self.financial_history.balance_sheet.extend(self.__setHistoryDate(FIELD_NET_WORTH, _stock_code, self.url_balance_sheet, False))
        
        return self.financial_history
        
    def __setHistoryDate(self, _description: str, _stock_code: str, url: str, _turn_value_positive: bool):
        res = requests.get(url.format(_stock_code), headers=self.request_headers)
        page = BeautifulSoup(res.content)
        return_lst: List[History] = []

        if not page:
            return
    
        period_index: int = -1 

        # gettin' the periods/
        header_section: Tag = page.find("div", attrs={"class": "D(tbr) C($primaryColor)", "data-reactid": "32"})

        if header_section is None:
            return

        columns: List[Tag] = header_section.select("div > span")
        for column in columns:
            period_index = period_index + 1

            if not (column is None):
                text_aux: str = ""

                if (str(column.get_text()).lower() == "ttm"):
                    text_aux = datetime.today().strftime("%d/%m/%Y")
                else:
                    text_aux = column.get_text()

                _date_aux = text_aux.split("/")

                if not (_date_aux is None or _date_aux == "" or len(_date_aux) < 3):
                    period = date(int(_date_aux[2]), int(_date_aux[1]), int(_date_aux[0])).isoformat()
                    
                    # getting the values
                    value_row: Tag = page.find("span", text=re.compile(_description, re.IGNORECASE))
                    if value_row is None:
                        continue

                    value_cell: List[Tag] = list(value_row.parent.parent.parent.children)
                    if value_cell is None or len(value_cell) == 0:
                        continue

                    if value_cell[period_index] is None:
                        continue

                    value_span: Tag = value_cell[period_index].find("span")
                    if value_span is None:
                        continue

                    formatted_value_aux = 0.00

                    if _turn_value_positive is True:
                        formatted_value_aux = (Parser.ParseFloat(value_span.get_text()))

                        if (formatted_value_aux < 0):
                            formatted_value_aux = formatted_value_aux * -1
                            pass
                    else:
                        formatted_value_aux = Parser.ParseFloat(value_span.get_text())
                        pass

                    hist_data: History = History(_description, period, (formatted_value_aux * 1000))
                    return_lst.append(hist_data)
                    pass
                pass
            continue        
        return return_lst
    pass
