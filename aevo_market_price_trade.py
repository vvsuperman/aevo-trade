# 策略2 ：
#     - 查看买一卖一价差有多大，如果小于0.1%， 直接下市价单。
#     - 下单后，查询是否有未平仓位，如果有，市价平仓。
#     - 交易次数达到上限后，程序退出。


import asyncio
import json
from aevo import AevoClient
from dotenv import load_dotenv
import os
from constant import keysList

# 加载.env文件
load_dotenv()


async def foo(quantity, max_trade_number):


    # ==================== 交易配置 ====================
    tradeAsset = 'ETH' # 设置交易币种
    # quantity = 0.01  # 设置每次交易数量(单位：币)
    # max_trade_number =  1 # 设置刷交易的次数，开平仓为一次
    # ===============================================
    
    aevo_sub = AevoClient(
        signing_key=os.getenv("SIGNING"), # 钱包私钥
        wallet_address=os.getenv("WALLETADDRESS"), # 钱包地址
        api_key=os.getenv("APIKEY"), # API key
        api_secret=os.getenv("APISECRET"), # API secret
        # signing_key=signing_key,
        # wallet_address=wallet_address,
        # api_key=api_key,
        # api_secret=api_secret,
        env="mainnet",
    )


    if not aevo_sub.signing_key:
        raise Exception(
            "Signing key is not set. Please set the signing key in the AevoClient constructor."
        )
    
    markets = aevo_sub.get_markets(tradeAsset)
    await aevo_sub.open_connection()
    await aevo_sub.subscribe_ticker(f"ticker:{tradeAsset}:PERPETUAL")
    
    #async for msg in init_aevo.read_messages():
    for info in keysList:
        number = 0
        async for msg in aevo_sub.read_messages():
            maxTaskNum = len(keysList)
            taskNum =0
               

            print(info["name"]+" began----------------------")
            #await foo(info["key"], info["address"],info["api_key"],info["api_secret"],0.01, 1)
            aevo = AevoClient(
                signing_key=info["key"], # 钱包私钥
                wallet_address=info["address"], # 钱包地址
                api_key=info["api_key"], # API key
                api_secret=info["api_secret"], # API secret
                # signing_key=signing_key,
                # wallet_address=wallet_address,
                # api_key=api_key,
                # api_secret=api_secret,
                env="mainnet",
            )


            if not aevo.signing_key:
                raise Exception(
                    "Signing key is not set. Please set the signing key in the AevoClient constructor."
                )
            data = json.loads(msg)["data"]
            # 如果数据里包含ticker，就执行交易
            if "tickers" in data:
                print('开始执行第{}次交易'.format(number + 1))
                instrument_id = markets[0]['instrument_id']
                bid_price = float(data["tickers"][0]['bid']['price'])
                ask_price = float(data["tickers"][0]['ask']['price'])
                price_step = float(markets[0]['price_step'])
                price_decimals = len(str(price_step).split('.')[1])
                # 计算价差比例
                spread = (ask_price - bid_price) / bid_price
                print(f'买一价：{bid_price}, 卖一价：{ask_price}, 价差比例：{spread}')
                if spread < 0.0005:
                    print('价差比例小于0.05%，直接下市价单')
                    # 下市价卖单
                    response = aevo.rest_create_order(instrument_id=instrument_id, is_buy=False, limit_price=0, quantity=quantity, post_only=False)
                    print(response)
                    # 下市价买单
                    buy_order_price = round( ask_price * 1.02, price_decimals)
                    response = aevo.rest_create_order(instrument_id=instrument_id, is_buy=True, limit_price=buy_order_price, quantity=quantity, post_only=False)
                    print(response)
                    print(info["name"]+'第{}次交易结束'.format(number),'开始查询是否有未平仓位。')
                    account_info = aevo.rest_get_account()
                    positions = account_info['positions']
                    if len(positions) > 0:
                        # 找出instrument_name等于交易资产的position
                        for position in positions:
                            if position['instrument_name'] == f'{tradeAsset}-PERP':
                                # 市价平仓
                                instrument_id, cpquantity, side = position['instrument_id'], float(position['amount']), position['side']
                                is_buy = True if side == 'sell' else False
                                limit_price = round( ask_price * 1.1, price_decimals) if is_buy else 0
                                print(f'存在未平仓位，开始平仓,并取消所有挂单。instrument_id: {instrument_id}, quantity: {cpquantity}, is_buy: {is_buy}, limit_price: {limit_price}')
                                response = aevo.rest_create_order(instrument_id=instrument_id, is_buy=is_buy, limit_price=limit_price, quantity=cpquantity, post_only=False)
                                print(response)
                                aevo.rest_cancel_all_orders()
                    # 暂停5秒
                    number += 1
                    await asyncio.sleep(5)
                
                if number >= max_trade_number:
                    print( info["name"]+'交易次数已达到上限，程序退出')
                    break
                    # aevo.close_connection()
                    # taskNum += 1
                    # print(f'执行任务数:{taskNum},任务上限:{maxTaskNum}')
                    # if taskNum >= maxTaskNum:
                    #     print("所有任务均结束，程序退出")
                    #     return
                    # continue
            

if __name__ == "__main__":
    asyncio.run(foo())
