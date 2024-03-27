import time
import requests
import hmac
from hashlib import sha256

APIURL = "https://open-api-vst.bingx.com"
APIKEY = "YOUR_APIKEY"
SECRETKEY = "YOUR_SECRETKEY"

def get_sign(api_secret, payload):
    signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
    print("sign=" + signature)
    return signature


def send_request(method, path, urlpa, payload):
    url = "%s%s?%s&signature=%s" % (APIURL, path, urlpa, get_sign(SECRETKEY, urlpa))
    print(url)
    headers = {
        'X-BX-APIKEY': APIKEY,
    }
    response = requests.request(method, url, headers=headers, data=payload)
    return response.text


def praseParam(paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    return paramsStr+"&timestamp="+str(int(time.time() * 1000))

# ------------------------------- #
# ------------------------------- #
# --------- Our Function -------- #
# ------------ Below ------------ #
# ------------------------------- #

def BingX_trade_order_MARTKET_VST(symbol="BTC-USDT", action="BUY", quantity=0) :

    payload = {}
    path = '/openApi/swap/v2/trade/order'
    method = "POST"
    
    positionSide = ""
    if action == "BUY" :
        positionSide = "LONG"
    else :
        positionSide = "SHORT"

    paramsMap = {
        "symbol": symbol,
        "type": "MARKET",
        "side": action,
        "positionSide": positionSide,
        "quantity": quantity,
        "stopPrice": 0,
        "recvWindow": 0,
        "timeInForce": ""
    } # paramsMap

    paramsStr = praseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)

def BingX_trade_marginType(symbol="BTC-USDT", marginType="", recvWindow=0) :

    payload = {}
    path = '/openApi/swap/v2/trade/marginType'
    method = "POST"

    paramsMap = {
    "symbol": symbol,
    "marginType": marginType, # ISOLATED, CROSSED
    "recvWindow": 0
    }   # paramsMap

    paramsStr = praseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)

# Correspond : Bianace_open_market_by_quantity(symbol, action, entry, quantity, leverage, client)
def BingX_trade_order(symbol="BTC-USDT", action="BUY", entry=1800.0, quantity=0 ) :

    payload = {}
    path = '/openApi/swap/v2/trade/order'
    method = "POST"
    
    positionSide = ""
    if action == "BUY" :
        positionSide = "LONG"
    else :
        positionSide = "SHORT"

    paramsMap = {
        "symbol": symbol,
        "side": action,
        "price" : entry,
        "positionSide": positionSide,
        "type": "",
        "quantity": quantity,
        "takeProfit": ""
    } # paramsMap

    paramsStr = praseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)

# Correspond : Close_specifiy_position(symbol, precision, client)
def BingX_Close_A_Position(symbol="BTC-USDT", action="BUY", entry=1800.0, quantity=0 ) :

    payload = {}
    path = '/openApi/swap/v2/trade/order'
    method = "POST"
    
    positionSide = ""
    if action == "BUY" :
        positionSide = "SHORT"
    else :
        positionSide = "LONG"

    paramsMap = {
        "symbol": symbol,
        "side": action,
        "price" : entry,
        "positionSide": positionSide,
        "type": "",
        "quantity": quantity,
        "takeProfit": ""
    } # paramsMap

    paramsStr = praseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)

def BingX_get_market_openInterest():
    payload = {}
    path = '/openApi/swap/v2/quote/openInterest'
    method = "GET"
    paramsMap = {
    "symbol": "BTC-USDT"
}
    paramsStr = praseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)

def BingX_get_position_info():
    payload = {}
    path = '/openApi/swap/v2/user/positions'
    method = "GET"
    paramsMap = {
    "symbol": "BTC-USDT",
    "recvWindow": 0
}
    paramsStr = praseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)


def BingX_close_all_position() :
    payload = {}
    path = '/openApi/swap/v2/trade/closeAllPositions'
    method = "POST"
    paramsMap = {
        "recvWindow": 0
    } # paramsMap

    paramsStr = praseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)

if __name__ == '__main__':

    print("Hi")
    # Remember to change this code for testing...
    # print("demo:", Your_function())