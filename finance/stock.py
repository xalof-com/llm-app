import requests
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
import re, json
from typing import Any

def fetch_stock_price(tickers:str):
    
    if tickers.startswith('[') and tickers.endswith(']'):
        tickers = json.loads(tickers)
    elif tickers.startswith('{"symbols":'):
        tmp = json.loads(tickers)
        tickers = tmp['symbols']
    else:
        tickers = re.split(';|,| ', tickers.replace('`', '').replace('\n', ''))
    
    list_prices = []
    for symbol in tickers:
        symbol = symbol.upper().strip()

        if symbol == '':
            continue
        
        ticker_type = _get_ticker_type(symbol)
        price = -1
        current_time = ''
        # if _is_market_close() == True:
        #     data = _ticker_price_by_vnd(symbol)
        #     if data != None:
        #         price = data[0]['adClose'] * 1000
        # else:
        data = None
        for i in ['5m', '1m']:
            data = _ticker_price_by_entrade(symbol, ticker_type=ticker_type, interval=i)
        if data != None:
            price = data[0]['close'] if ticker_type == 'index' else data[0]['close'] * 1000
            current_time = data[0]['datetime']
        currency = 'VND'
        if ticker_type == 'index':
            currency = ' '
        
        list_prices.append({'ticker': symbol, 'price': price, 'updated_time': current_time, 'currency': currency})

    return list_prices




def _ticker_price_by_entrade(ticker:str, start_time:str=None, end_time:str=None, ticker_type:str='stock', interval:str='1D'):
    ENTRADE_ROOT_STOCK_URI = "https://services.entrade.com.vn/chart-api/v2/ohlcs"
    
    interval_map = {
        '1H': '1H',
        '1D': '1D',
        '1W': '1W',
        '1M': '1M',
        '1m': '1',
        '5m': '5',
        '15m' : '15',
        '30m' : '30'
    }

    keys_mapping = {
        'ts': 't',
        'datetime': 't',
        'open': 'o',
        'high': 'h',
        'low': 'l',
        'close': 'c',
        'volume': 'v'
    }

    _headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0', 
        'DNT': '1'
    }

    if start_time == None:
        # _start = datetime.now(tz=ZoneInfo("Asia/Ho_Chi_Minh")).replace(hour=0, minute=0, second=0)
        _start = datetime.combine(_get_weekday(), time.min)
    else:
        _start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')

    if end_time == None:
        # _end = datetime.now(tz=ZoneInfo("Asia/Ho_Chi_Minh")).replace(hour=23, minute=59, second=59)
        _end = datetime.combine(_get_weekday(), time.max)
    else:
        _end = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    resolution = interval_map[interval]

    url = f"{ENTRADE_ROOT_STOCK_URI}/{ticker_type}"
    _params = {
        'from': int(_start.timestamp()),
        'to': int(_end.timestamp()),
        'symbol': ticker,
        'resolution': resolution
    }

    try:
        response = requests.get(url, params=_params, headers=_headers)
        json_data = response.json()
        # print(json_data)
        if response.status_code == 200:
            # cols = list(json_data.keys())
            # cols.remove('nextTime')           
            if len(json_data['t']) == 0:
                return None

            list_prices = []
            for i in range(len(json_data['t'])):
                item = {
                    'ticker': ticker
                }
                for k in keys_mapping:
                    data_key = keys_mapping[k]
                    if k == 'datetime':
                        item[k] = datetime.fromtimestamp(json_data[data_key][i], tz=ZoneInfo('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        item[k] = json_data[data_key][i]
                list_prices.append(item)

            return sorted(list_prices, key=lambda x: x['ts'], reverse=True)
            
    except Exception as err:
        print('ERROR: ', err)
        
    return None 

def _ticker_price_by_vnd(ticker:str, start_date:str=None, end_date:str=None):
    VNDIRECT_ROOT_URI = "https://finfo-api.vndirect.com.vn/v4/stock_prices/"

    if start_date == None:
        _start = _get_weekday()
    else:
        _start = datetime.strptime(start_date, '%Y-%m-%d')

    if end_date == None:
        _end = _get_weekday()
    else:
        _end = datetime.strptime(end_date, '%Y-%m-%d')

    query = 'code:' + ticker + '~date:gte:' + _start.strftime('%Y-%m-%d') + '~date:lte:' + _end.strftime('%Y-%m-%d')
    delta = _end - _start
    _params = {
        "sort": "date",
        "size": delta.days + 1,
        "page": 1,
        "q": query
    }

    _headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0', 
        'DNT': '1'
    }

    try:
        response = requests.get(VNDIRECT_ROOT_URI, params=_params, headers=_headers)
        data = response.json()['data']        
        return data
    except Exception as err:
        print("ERROR: ", err)
    
    return None


def _ticker_price_by_tcbs(ticker:str, start_date:str=None, end_date:str=None, type:str='stock'):
    TCBS_ROOT_STOCK_URI = "https://apipubaws.tcbs.com.vn/stock-insight/v2/stock/bars-long-term"

    if start_date == None:
        _start = datetime.now()
    else:
        _start = datetime.strptime(start_date, '%Y-%m-%d')

    if end_date == None:
        _end = datetime.now()
    else:
        _end = datetime.strptime(end_date, '%Y-%m-%d')

    _resolution = '1m'

    delta = (_end - _start).days + 1

    # convert end_date to timestamp
    _end_date_timestamp = int(_end.timestamp())

    count = 1
    days = 365
    if delta > days:
        count = delta // days
        if delta % days != 0:
            count = count + 1
    
    data = []
    while count > 0:
        count_back = days
        if delta < days:
            count_back = delta

        url = f"{TCBS_ROOT_STOCK_URI}?ticker={ticker}&type={type}&resolution={_resolution}&to={_end_date_timestamp}&countBack={count_back}"
        try:
            response = requests.get(url)
            payload = response.json()
            if 'data' in payload:
                data = data + payload['data']
            count -= 1
            delta -= days
        except Exception as e:
            print("RequestException", e)

    if len(data) == 0:
        return None
    return data

def _get_ticker_type(ticker:str):
    if ticker.upper() in ['VNINDEX', 'VN30', 'HNX', 'HNX30']:
        return 'index'
    return 'stock'

def _is_market_close():
    open_time = datetime.now(tz=ZoneInfo("Asia/Ho_Chi_Minh")).replace(hour=9, minute=0, second=0)
    current_time = datetime.now(tz=ZoneInfo("Asia/Ho_Chi_Minh"))
    close_time = datetime.now(tz=ZoneInfo("Asia/Ho_Chi_Minh")).replace(hour=15, minute=0, second=0)

    if open_time < current_time  and current_time < close_time:
        return False

    return True

def _get_weekday():
    wday = datetime.now(tz=ZoneInfo("Asia/Ho_Chi_Minh"))
    while wday.weekday() > 4:
        wday -= timedelta(days=1)
    return wday
        