import sys
import time
import threading
import re
import requests
import traceback

from typing import List
from datetime import (date, datetime)
from .model.finacial_history import (FinancialHistory, History, Row, Period)
from .parser import Parser
from bs4 import (BeautifulSoup, Tag)
from random import randint

# FIELDS
FIELD_SHARED_DIVIDENDS = "Dividendos Pagos"
FIELD_NET_INCOME = "Lucro Líquido"
FIELD_NET_WORTH = "Patrimônio Líquido Total"
FIELD_TOTAL_DEBITS = "Total de Passivos"


class Crawler():
    url_balance_sheet: str = ""
    url_cash_flow: str = ""
    dt_processing: str = ""
    default_sleep_time_sec: int = 0
    financial_history: FinancialHistory = None
    request_headers = {
        'user-agent': "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    }

    def __init__(self, _url_cash_flow: str, _url_balance_sheet: str, _dt_processing: str, _default_sleep_time_sec: int = 0):
        self.url_balance_sheet = _url_balance_sheet
        self.url_cash_flow = _url_cash_flow
        self.dt_processing = _dt_processing
        self.default_sleep_time_sec = _default_sleep_time_sec
        pass

    def get_data(self, _stock_code: str) -> FinancialHistory:
        self.financial_history = FinancialHistory(_stock_code, self.dt_processing)

        cash_flow_rows: List[str] = [[FIELD_SHARED_DIVIDENDS, True], [FIELD_NET_INCOME, False]]
        balance_sheet_rows: List[str] = [[FIELD_NET_WORTH, False], [FIELD_TOTAL_DEBITS, False]]

        # We're changing scraping order to fool target site crawler detection layer 
        if ((randint(0, 10) % 2) == 0):
            cash_flow_hist_aux = self.__get_history("Fluxo de Caixa", cash_flow_rows, _stock_code, self.url_cash_flow, True)
            time.sleep(randint(0, self.default_sleep_time_sec))
            balnace_hist_aux = self.__get_history("Balanço", balance_sheet_rows, _stock_code, self.url_balance_sheet, False)
        else:
            balnace_hist_aux = self.__get_history("Balanço", balance_sheet_rows, _stock_code, self.url_balance_sheet, False)
            time.sleep(randint(0, self.default_sleep_time_sec))
            cash_flow_hist_aux = self.__get_history("Fluxo de Caixa", cash_flow_rows, _stock_code, self.url_cash_flow, True)

        if cash_flow_hist_aux:
            self.financial_history.history.append(cash_flow_hist_aux)

        if balnace_hist_aux:
            self.financial_history.history.append(balnace_hist_aux)
        
        return self.financial_history

    def __get_history(self, _hist_description: str, _rows: List[str], _stock_code: str, url: str, _turn_value_positive: bool) -> History:
        res: requests.Response = None
        page: BeautifulSoup = None
        hist_aux: History = None

        res = requests.get(url.format(_stock_code), headers=self.request_headers)
        page = BeautifulSoup(res.content)
        hist_aux: History = History(_hist_description, "{0} - {1}".format(res.status_code, res.reason))                
        hist_aux.periods = []
                
        if not page:
            return History(_hist_description, "Target server refused the connection")

        period_index: int = -1

        # gettin' the periods
        header_section: Tag = page.find("div", attrs={"class": "D(tbr) C($primaryColor)", "data-reactid": "32"})

        if header_section is None:
            return History(_hist_description, "Section not found")

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
                    period_date: date = date(int(_date_aux[2]), int(_date_aux[1]), int(_date_aux[0])).isoformat()
                    period_obj: Period = Period(period_date)

                    for row in _rows:
                        desc: str = row[0]
                        turn_positive: bool = (row[1] if row[1] else False) if len(row) > 1 else False  

                        # Row
                        period_obj.rows.append(self.__get_row(page, period_index, desc, turn_positive))
                        pass
                    
                    # Period
                    hist_aux.periods.append(period_obj)
                    pass
                pass
            pass 
        return hist_aux

    def __get_row(self, _page: BeautifulSoup, _period_index: int, _description: str, _turn_value_positive: bool) -> Row:
        if not _page:
            return None

        # getting the values
        value_row: Tag = _page.find("span", text=re.compile(
            "^{}$".format(_description), re.IGNORECASE))
        
        if value_row is None:
            return None

        value_cell: List[Tag] = list(value_row.parent.parent.parent.children)
        if value_cell is None or len(value_cell) == 0:
            return None

        if value_cell[_period_index] is None:
            return None

        value_span: Tag = value_cell[_period_index].find("span")
        if value_span is None:
            return None

        formatted_value_aux = 0.00

        if _turn_value_positive is True:
            formatted_value_aux = (Parser.ParseFloat(value_span.get_text()))

            if (formatted_value_aux < 0):
                formatted_value_aux = formatted_value_aux * -1
                pass
        else:
            formatted_value_aux = Parser.ParseFloat(value_span.get_text())
            pass

        return_row: Row = Row(_description, (formatted_value_aux * 1000))
        return return_row
    pass
