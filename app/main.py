import json
import logging
import uvicorn                      
from fastapi import FastAPI
from lib.FaucetRPC import *

app = FastAPI()

@app.get('/api/v1/summary')
async def summary():
    with open('data/summary.json') as f:
        summary = json.load(f)
    return summary


@app.get('/api/v1/ticker')
async def ticker():
    with open('data/ticker.json') as f:
        ticker = json.load(f)
    return ticker


@app.get('/api/v1/orderbook/{market_pair}')
async def orderbook(market_pair: str = "ALL"):
    with open('data/orderbook.json') as f:
        orderbook = json.load(f)
        try:
            return orderbook[market_pair]
        except KeyError:
            return {'error': 'no such pair'}


@app.get('/api/v1/trades/{market_pair}')
async def trades(market_pair: str = "ALL"):
    with open('data/trades.json') as f:
        trades = json.load(f)
        try:
            return trades[market_pair]
        except KeyError:
            return {'error': 'no such pair'}


# FAUCET ENDPOINTS
@app.get("/faucet/{coin}/{addr}")
async def drip(coin: str, addr: str):
    if coin not in ["RICK", "MORTY"]:
        return {
            "Result": "Error",
            "Response": {"Message": coin+" not recognised. Use RICK or MORTY."}
        }
    rpc = get_rpc(coin)
    return rpc.validate_drip(coin, addr)


@app.get("/faucet_db")
def show_db():
    return dump_db()


@app.get("/db_addr/{addr}")
def show_db_addr(addr: str):
    return select_addr_from_db(addr)


@app.get("/rm_faucet_balances")
def show_faucet_balances():
    return get_faucet_balances()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    uvicorn.run("main:app", host="0.0.0.0", port=8081, access_log=False, log_level='info', reload=True)