from constant import keysList
from aevo_market_price_trade import foo
import asyncio
from aevo import AevoClient
from dotenv import load_dotenv
import os



# quantity = 0.01  # 设置每次交易数量(单位：币)
# max_trade_number =  1 # 设置刷交易的次数，开平仓为一次

async def aveoTrading():

    # 加载.env文件
    await foo(0.01, 10)

if __name__ == "__main__":
    asyncio.run(aveoTrading())
