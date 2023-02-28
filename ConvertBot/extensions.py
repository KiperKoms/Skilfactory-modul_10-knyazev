import json
import requests
from config import keys, API_KEY



class APIException(Exception):
    pass

class Convertermoney:
    @staticmethod
    def get_price(quote: str, base: str, amount: str):

        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту {quote}')

        try:
            base_ticker = keys[base]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту {base}')

        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество {amount}')

        if quote == base:
            raise APIException(f'Указаны одинаковые валюты {base}')

        r = requests.get(f'https://currate.ru/api/?get=rates&pairs={quote_ticker}{base_ticker}&key={API_KEY}')
        total_base = json.loads(r.content)['data'][quote_ticker + base_ticker]

        return total_base