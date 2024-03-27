import os
import yaml
from binance.client import Client
import datetime
from binance.helpers import round_step_size

application_path = os.getcwd()
path = os.path.join(application_path, "config_algo.yaml")

with open(path, "r", encoding='utf-8') as f:
  config = yaml.safe_load(f)

# example for multiple client
client_1 = Client(config["exchange_setting"]["api_key_1"], config["exchange_setting"]["api_secret_1"])
client_2 = Client(config["exchange_setting"]["api_key_2"], config["exchange_setting"]["api_secret_2"])
client_3 = Client(config["exchange_setting"]["api_key_3"], config["exchange_setting"]["api_secret_3"])


def Choose_client( client ) :

  if client == 1 :
    return client_1
  elif client == 2 :
    return client_2
  elif client == 3 :
    return client_3
  else :
    assert False, "client known!!"


def Get_open_orders(symbol, client):  #取得該幣種的所有委託資訊
    orders = client.futures_get_open_orders(symbol=symbol)
    return orders


def Get_position_information(symbol, client): #取得該幣種的所有開單資訊
  position_information = client.futures_position_information(symbol=symbol)
  return position_information


def Get_tick_size(symbol: str, client) -> float:  #取得tick_size 兩層迴圈!!

  info = client.futures_exchange_info()

  for symbol_info in info['symbols']:
    if symbol_info['symbol'] == symbol:
      for symbol_filter in symbol_info['filters']:
        if symbol_filter['filterType'] == 'PRICE_FILTER':

          return float(symbol_filter['tickSize'])


def Get_rounded_price(symbol: str, price: float, client) -> float:
  return round_step_size(price, Get_tick_size(symbol))


def Check_limit_open_size(symbol, client):  #查詢該幣種的最小購買數量 酷寫法

  info = client.futures_exchange_info()

  for i in range(0, len(info['symbols'])):
    if info['symbols'][i]['symbol'] == symbol:
      minQty = info['symbols'][i]['filters'][1]['minQty']

      return minQty


def Check_precision(symbol):  #查詢該幣種的價格及數量精準度

  info = client_1.futures_exchange_info()

  for i in range(0, len(info['symbols'])):
    if info['symbols'][i]['symbol'] == symbol:
      pricePrecision = info['symbols'][i]['pricePrecision']
      quantityPrecision = info['symbols'][i]['quantityPrecision']

      return pricePrecision, quantityPrecision
    
    else:
      pricePrecision = 0
      quantityPrecision = 0

  return pricePrecision, quantityPrecision


def Check_account_balance(client):  #查詢合約錢包中有多少USDT
  # get futures asset_balance
  usdt_balance = None
  futures = client.futures_account_balance()

  for check_balance in futures:
    if check_balance["asset"] == "USDT":  #Change by yourself
      usdt_balance = check_balance["balance"]

      return usdt_balance


def Change_leverage(symbol, leverage, client):
  client.futures_change_leverage(symbol=symbol, leverage=leverage)


def Bianace_open_limit(symbol, action, entry, fund, leverage, client):

  precision = Check_precision(symbol)
  buy_limit = client.futures_create_order(
    symbol=symbol,
    type='LIMIT',
    timeInForce='GTC',  # Can be changed - see link to API doc below
    #price=round(
    #  entry, precision[0]),  # The price at which you wish to buy/sell, float
    price = Get_rounded_price(symbol, entry),
    side=action.upper(),  # Direction ('BUY' / 'SELL'), string
    quantity=round(
      (fund * leverage / entry),
      precision[1]),  # Number of coins you wish to buy / sell, float
  )


def Bianace_open_market_order(symbol, action, entry, fund, leverage, client):

  precision = Check_precision(symbol)
  buy_limit = client.futures_create_order(
    symbol=symbol,
    type='MARKET',
    side=action.upper(),  # Direction ('BUY' / 'SELL'), string
    quantity=round(
      (fund * leverage / entry),
      precision[1]),  # Number of coins you wish to buy / sell, float
  )


def Bianace_open_market_order_by_quantity(symbol, action, entry, quantity, leverage, client):

  precision = Check_precision(symbol)
  buy_limit = client.futures_create_order(
    symbol=symbol,
    type='MARKET',
    side=action.upper(),  # Direction ('BUY' / 'SELL'), string
    quantity=quantity,
  )


def Set_market_closePosition_TP(symbol, action, entry, fund, tp, client):

  if action.upper() == 'SELL':
    positionside = "BUY"
  else:
    positionside = "SELL"
  order_take = client.futures_create_order(
    symbol=symbol,
    side=positionside,
    type='TAKE_PROFIT_MARKET',
    #positionSide = positionside,
    stopPrice=tp,
    closePosition=True)


def Set_market_TP(symbol, action, entry, fund, tp, leverage, client):

  precision = Check_precision(symbol)
  if action.upper() == 'SELL':
    positionside = "BUY"
  else:
    positionside = "SELL"
  order_take = client.futures_create_order(
    symbol=symbol,
    side=positionside,
    type='TAKE_PROFIT_MARKET',
    #positionSide = positionside,
    reduceOnly='true',
    stopPrice=round(tp, precision[0]),
    quantity=round(fund * leverage / entry, precision[1]))


def Set_SL(symbol, action, quantity, sl, client):
  precision = Check_precision(symbol)
  if action.upper() == 'SELL':
    positionside = "BUY"
  else:
    positionside = "SELL"
  order_take = client.futures_create_order(
    symbol=symbol,
    side=positionside,
    type='STOP_MARKET',
    positionSide = positionside,
    reduceOnly='true',
    stopPrice=round(sl, precision[0]),
    quantity=quantity)


def Set_limit_TP(symbol, action, entry, fund, tp, leverage, client):
  precision = Check_precision(symbol)
  if action.upper() == 'SELL':
    positionside = "BUY"
  else:
    positionside = "SELL"
    
  
  order_take = client.futures_create_order(
    symbol=symbol,
    side=positionside,
    timeInForce='GTC',  # Can be changed - see link to API doc below
    type='LIMIT',
    #positionSide = positionside,
    #price=round(tp, precision[0]),
    price=Get_rounded_price(symbol, tp),
    reduceOnly='true',
    quantity=round(fund * leverage / entry, precision[1]))


def Set_limit_TP_no_reduceonly(symbol, action, entry, fund, tp, leverage, client):
  precision = Check_precision(symbol)
  if action.upper() == 'SELL':
    positionside = "BUY"
  else:
    positionside = "SELL"
  order_take = client.futures_create_order(
    symbol=symbol,
    side=positionside,
    timeInForce='GTC',  # Can be changed - see link to API doc below
    type='LIMIT',
    #positionSide = positionside,
    #price=round(tp, precision[0]),
    price=Get_rounded_price(symbol, tp),
    quantity=round(fund * leverage / entry, precision[1]))


def Set_market_SL(symbol, action, sl, client):
  if action.upper() == 'SELL':
    positionside = "SELL"
  else:
    positionside = "BUY"
  order_take = client.futures_create_order(
    symbol=symbol,
    side=positionside,
    type='STOP_MARKET',
    #positionSide = positionside,
    stopPrice=sl,
    closePosition=True)


def Close_specifiy_position(symbol, precision, client):

  #關掉該symbol當前倉位的單
  position_information = client.futures_position_information(symbol=symbol)
  for coin_position in position_information:
    if coin_position["symbol"] == symbol.upper() and coin_position["positionAmt"] != "0.0" :
      positionside = 'BUY'
      positionAmt = float(coin_position["positionAmt"])
      if positionAmt > 0.0:
        positionside = 'SELL'

      buy_limit = client.futures_create_order(
        symbol = symbol,
        type = 'MARKET',  #'LIMIT'
        side = positionside,  # Direction ('BUY' / 'SELL'), string
        quantity = round( abs(positionAmt), precision[1] ),  # Number of coins you wish to buy / sell, float

        reduceOnly='true')
      
      client.futures_cancel_all_open_orders(symbol=symbol)
  

def Cancel_all_open_orders(symbol, client):
    client.futures_cancel_all_open_orders(symbol=symbol)
    

def Cancel_order(symbol,order_id, client):
    client.futures_cancel_order(symbol=symbol,orderId =(order_id), timestamp=True)
    
    
def Check_current_position(symbol, client):
  is_symbol_exist = False  ##檢查該symbol當前有無倉位
  position_information = client.futures_position_information(symbol=symbol)
  for coin_position in position_information:
    side = None
    if float(coin_position["positionAmt"]) != 0:
      is_symbol_exist = True
      side = 'BUY'
      if float(coin_position["positionAmt"]) < 0.0:
        side = 'SELL'

  return is_symbol_exist, side


def Change_market_to_limit_orders(insurance_limit_market, client):

  orders = client.futures_get_open_orders()
  single_order = orders[0]
  for single_order in orders:
    symbol = single_order["symbol"]
    if single_order["type"] == "TAKE_PROFIT_MARKET" and Check_current_position(
        symbol)[0] == True:
      precision = Check_precision(symbol)
      for check_no_reduce_only_order in orders:
        dont_excute = True
        if symbol == check_no_reduce_only_order[
            "symbol"] and check_no_reduce_only_order[
              "type"] == "LIMIT" and check_no_reduce_only_order[
                "reduceOnly"] == "False":

          dont_excute = True
        else:
          dont_excute = False

      if dont_excute == False: 
        result = client.futures_cancel_order(
          symbol=single_order["symbol"],
          orderId=single_order["orderId"],
          origClientOrderId=single_order["clientOrderId"],
          timestamp=True)
        position_information = client.futures_position_information(
          symbol=symbol)
        for info in position_information:
          info["symbol"] == symbol
          entry = float(info["entryPrice"])
          fund = abs(float(info["notional"]))
          quantity = round(abs(float(info["positionAmt"])), precision[1])
        #TP
        tp = float(single_order["stopPrice"])

        if single_order["side"] == 'SELL':
          action = "BUY"
          #開倉-(開倉-止盈)*(1+調整)
          new_tp = entry - (entry - tp) * (1 + (insurance_limit_market / 100))

        else:
          action = "SELL"
          #(止盈-開倉)*(1+調整)+開倉
          new_tp = (tp - entry) * (1 + (insurance_limit_market / 100)) + entry

        Set_limit_TP(symbol, action, entry, fund, new_tp, quantity)


def Is_position_too_close(symbol, new_position_tp, tp_proportion, client):
  orders = client.futures_get_open_orders()
  #print(orders)
  for order in orders:
    if order['symbol'] == symbol:
      old_position_tp = float(order['price'])
      if new_position_tp < old_position_tp * (
          1 + (tp_proportion / 100)) and new_position_tp > old_position_tp * (
            1 - (tp_proportion / 100)):
        return True
  return False


def Is_in_CD(coin, client): # 現在時間 - 上一個order時間 時間差若小於2分鐘就不能開單，遮頻

  order = client.futures_account_trades(symbol=coin, limit=1)
  now = datetime.datetime.now()
  if order == []:
    
    print("New Coin that never open before!")
    return False
  
  else:

    pre_time = datetime.datetime.fromtimestamp(int(order[0]['time']) / 1000)
    time_delta = now - pre_time
    minute = int(time_delta.seconds / 60)

    if minute <= 2:  
      print("Last Order Time:")
      print(pre_time)
      print("Order Info:")
      print(order[0])
      return True
    
    return False


def TP_dispersion_calculation(symbol, action, entry, fund, tp, leverage,
                              tp_adjust, tp_dispersion_rate,
                              quantity_dispersion_rate):
  
  precision = Check_precision(symbol)

  tp1 = (tp - entry) * tp_adjust + entry
  tp2 = (tp - entry) * (tp_adjust - tp_dispersion_rate) + entry
  tp3 = (tp - entry) * (tp_adjust + tp_dispersion_rate) + entry

  quantity0 = round((fund * leverage / entry), precision[1])
  quantity1 = round(quantity0 * quantity_dispersion_rate, precision[1])
  quantity2 = round(quantity0 * (1 - quantity_dispersion_rate) / 2,
                    precision[1])
  quantity3 = float(
    format(quantity0 - (quantity1 + quantity2), "." + str(precision[1]) + "f"))

  return tp1, tp2, tp3, quantity1, quantity2, quantity3


def Set_limit_TP_dispersion_3(symbol, action, entry, fund, tp, leverage,
                              tp_adjust, tp_dispersion_rate,
                              quantity_dispersion_rate, client):
  new_tp = 0
  precision = Check_precision(symbol)
  if action.upper() == 'SELL':
    positionside = "BUY"
  else:
    positionside = "SELL"

  tp_parameter = TP_dispersion_calculation(symbol, action, entry, fund, tp,
                                           leverage, tp_adjust,
                                           tp_dispersion_rate,
                                           quantity_dispersion_rate)
  tp1 = tp_parameter[0]
  tp2 = tp_parameter[1]
  tp3 = tp_parameter[2]

  quantity1 = tp_parameter[3]
  quantity2 = tp_parameter[4]
  quantity3 = tp_parameter[5]
    
  client.futures_create_order(
    symbol=symbol,
    side=positionside,
    timeInForce='GTC',  # Can be changed - see link to API doc below
    type='LIMIT',
    #positionSide = positionside,
    price=Get_rounded_price(symbol, tp1),
    reduceOnly='true',
    quantity=quantity1)
  
  client.futures_create_order(
    symbol=symbol,
    side=positionside,
    timeInForce='GTC',  # Can be changed - see link to API doc below
    type='LIMIT',
    #positionSide = positionside,
    price=Get_rounded_price(symbol, tp2),
    reduceOnly='true',
    quantity=quantity2)
  
  client.futures_create_order(
    symbol=symbol,
    side=positionside,
    timeInForce='GTC',  # Can be changed - see link to API doc below
    type='LIMIT',
    #positionSide = positionside,
    price=Get_rounded_price(symbol, tp3),
    reduceOnly='true',
    quantity=quantity3)
