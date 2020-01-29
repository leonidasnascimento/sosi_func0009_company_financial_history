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

# FIELDS
FIELD_SHARED_DIVIDENDS = "Dividendos Pagos"
FIELD_NET_INCOME = "Lucro Líquido"
FIELD_NET_WORTH = "Patrimônio Líquido Total"
FIELD_TOTAL_DEBITS = "Total de Passivos"


class Crawler():
    url_balance_sheet: str = ""
    url_cash_flow: str = ""
    dt_processing: str = ""
    financial_history: FinancialHistory = None
    request_headers = {
        'user-agent': "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        'cache-control': "no-cache"
    }
    
    proxies = { '167.172.135.255:8080', '36.67.212.187:3128', '112.87.77.121:9999', '163.172.136.226:8811', '118.179.36.125:80', '5.160.131.12:53281', '187.11.216.80:8080', '36.37.160.224:23500', '80.240.115.254:36539', '195.239.115.106:44413', '178.128.18.102:8080', '134.209.181.49:8080', '35.175.175.5:8080', '171.35.160.197:9999', '109.200.156.102:8080', '91.135.148.198:59384', '114.134.190.230:37294', '223.199.18.131:9999', '157.245.123.27:8888', '110.36.229.164:8080', '138.121.91.139:8080', '213.6.149.138:41088', '170.82.73.140:53281', '138.201.5.34:8080', '83.56.10.201:8080', '45.222.97.210:8080', '64.227.14.30:8080', '221.229.252.98:9797', '117.88.176.171:3000', '62.240.53.101:8080', '78.188.186.180:8080', '206.189.38.237:8080', '165.227.248.222:3128', '45.4.85.152:999', '88.86.72.161:8080', '129.205.201.239:8080', '191.97.8.171:999', '171.5.26.19:8080', '43.255.228.150:3128', '101.108.251.78:8080', '165.22.50.208:8080', '223.199.31.13:9999', '144.202.105.190:80', '180.250.216.242:3128', '5.196.89.163:3128', '51.158.111.229:8811', '123.149.141.82:9999', '45.71.113.186:3128', '149.28.158.177:8000', '85.198.250.135:3128', '197.234.179.102:3128', '103.26.54.94:8080', '163.204.245.224:9999', '171.35.169.138:9999', '180.183.129.146:8080', '200.74.14.106:8080', '47.244.10.43:8080', '139.5.71.70:23500', '112.84.52.3:9999', '14.207.123.2:8080', '121.40.119.149:3128', '47.106.59.75:3128', '183.88.13.179:8080', '222.190.125.3:8118', '14.162.145.116:55055', '83.97.111.202:41258', '109.122.81.1:44556', '95.79.55.196:53281', '182.253.60.170:8083', '113.194.31.118:9999', '125.209.126.18:8080', '177.130.140.80:8080', '195.96.76.122:8080', '154.72.73.218:8080', '181.188.166.74:8080', '223.199.22.107:9999', '36.67.47.187:40440', '77.74.79.25:8080', '14.207.204.143:8080', '200.218.255.145:8080', '198.204.253.115:3128', '122.70.148.66:808', '157.245.124.217:3128', '103.74.120.78:3128', '94.28.57.100:8080', '36.67.24.109:37641', '89.32.227.230:8080', '74.85.157.198:8080', '88.135.40.74:8080', '125.209.73.170:3128', '203.76.124.35:8080', '68.183.186.232:8080', '182.76.169.195:3129', '223.204.67.65:8080', '165.16.29.171:8080', '49.67.190.251:9999', '64.227.14.32:8080', '36.91.129.18:8080', '142.93.72.206:3128', '36.27.28.221:9999', '114.226.35.254:9999', '169.239.223.136:49027', '51.75.127.193:3128', '51.158.99.51:8811' }

    def __init__(self, _url_cash_flow: str, _url_balance_sheet: str, _dt_processing: str):
        self.url_balance_sheet = _url_balance_sheet
        self.url_cash_flow = _url_cash_flow
        self.dt_processing = _dt_processing
        pass

    def get_data(self, _stock_code: str) -> FinancialHistory:
        self.financial_history = FinancialHistory(_stock_code, self.dt_processing)

        cash_flow_rows: List[str] = [[FIELD_SHARED_DIVIDENDS, True], [FIELD_NET_INCOME, False]]
        balance_sheet_rows: List[str] = [[FIELD_NET_WORTH, False], [FIELD_TOTAL_DEBITS, False]]

        cash_flow_hist_aux = self.__get_history("Fluxo de Caixa", cash_flow_rows, _stock_code, self.url_cash_flow, True)
        balnace_hist_aux = self.__get_history("Balanço", balance_sheet_rows, _stock_code, self.url_balance_sheet, False)

        if cash_flow_hist_aux:
            self.financial_history.history.append(cash_flow_hist_aux)

        if balnace_hist_aux:
            self.financial_history.history.append(balnace_hist_aux)
        
        return self.financial_history

    def __get_history(self, _hist_description: str, _rows: List[str], _stock_code: str, url: str, _turn_value_positive: bool) -> History:
        res: requests.Response = None
        page: BeautifulSoup = None
        hist_aux: History = None
        hist_aux.periods = []

        for proxy in self.proxies:
            try:
                res = requests.get(url.format(_stock_code), headers=self.request_headers, proxies={"http": proxy, "https": proxy})
                page = BeautifulSoup(res.content)
                hist_aux: History = History(_hist_description, "{0} - {1}".format(res.status_code, res.reason))                

                if page:
                    break
            except:
                continue
                
        if not page:
            return hist_aux

        period_index: int = -1

        # gettin' the periods
        header_section: Tag = page.find("div", attrs={"class": "D(tbr) C($primaryColor)", "data-reactid": "32"})

        if header_section is None:
            return hist_aux

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
