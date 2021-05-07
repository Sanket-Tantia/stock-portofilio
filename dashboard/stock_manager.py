from nsetools import Nse
from bsedata.bse import BSE

class NSE:
    nse_obj = Nse()

    @classmethod
    def get_all_stock_codes(cls)->list:
        return [{'stock_code': stock_code, 'companyName':companyName} 
        for stock_code,companyName in cls.nse_obj.get_stock_codes().items()]

    @classmethod
    def get_stock_info(cls, stock_code)->dict:
        stock_quote = cls.nse_obj.get_quote(stock_code)
        if stock_quote:
            return {
                'companyName': stock_quote.get('companyName'),
                'isinCode': stock_quote.get('isinCode'),
                'symbol': stock_quote.get('symbol'),
                'exchange': 'NSE',
                'series': stock_quote.get('series')
            }
        else:
            return None
        

    @classmethod
    def get_stock_daily_price(cls, stock_code)->dict:
        stock_quote = cls.nse_obj.get_quote(stock_code)
        return {
            'secDate': stock_quote.get('secDate'),
            'dayHigh': stock_quote.get('dayHigh'),
            'dayLow': stock_quote.get('dayLow'),
            'lastPrice': stock_quote.get('lastPrice'),
            'open': stock_quote.get('open'),
            'closePrice': stock_quote.get('closePrice')
        }


class BSE:
    bse_obj = BSE()

    @classmethod
    def get_stock_info(cls, stock_code)->dict:
        stock_quote = cls.bse_obj.getQuote(stock_code)
        return stock_quote