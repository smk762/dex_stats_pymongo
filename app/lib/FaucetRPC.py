#!/usr/bin/env python3
import os
import random
from slickrpc import Proxy
from dotenv import load_dotenv
from .lib_sqlite import *
load_dotenv()

node_list = [i for i in os.environ.get("NODELIST").split(" ")] 
rpcuser = os.environ.get("RPCUSER")
rpcpass = os.environ.get("RPCPASS")
rpc_ports = {
    "RICK":os.environ.get("RICKPORT"),
    "MORTY":os.environ.get("MORTYPORT")
}


class FaucetRPC():
    def __init__(self, node, rpcport):
        self.rpc = (Proxy(f"http://{rpcuser}:{rpcpass}@{node}:{rpcport}"))
        self.node = node

    def get_addr_bal(self, addr):
        try:
            resp = self.rpc.getaddressbalance({"addresses": [addr]})
            balance = resp["balance"]/100000000
            return balance
        except:
            return 0

    def get_addr_received(self, addr):
        try:
            resp = self.rpc.getaddressbalance({"addresses": [addr]})
            received = resp["received"]/100000000
            return received
        except:
            return 0

    def is_addr_valid(self, addr):
        try:
            if 'ismine' not in self.rpc.validateaddress(addr):
                return False
            else:
                return True
        except:
            return True

    def validate_drip(self, coin, addr):
        resp = {
            "Response":{
                "Coin": coin,
                "Address": addr
            }                
        }
        if not self.is_addr_valid(addr):
            resp.update({"Result": "Error"})
            resp["Response"].update({"Message": addr+" is not a valid "+coin+" address."})
            return resp
        try:
            bal = self.get_addr_bal(addr)
            resp["Response"].update({"Balance": bal})
        except Exception as e:
            print(e)
            bal = 0
            resp.update({"Result": "Error"})
            resp["Response"].update({"Message": f"{self.node} RPC unresposive. Please try again later"})
            return resp


        # Is address in queue, or been replenished in the last 4 hours?
        if is_in_queue(coin, addr):
            result = "Denied"
            msg = "Thankyou for request, a tranasction to "+addr+" is already in the queue and should arrive in less than 5 min."

        elif is_recently_filled(coin, addr):
            result = "Denied"
            msg = "Thankyou for request, your address has been filled recently. Please try again later."

        elif is_dry(coin):
            result = "Denied"
            msg = "Thankyou for request, the faucet has exceeded 4hr allocation limit. Please try again later."

        # is balance low?
        elif bal < 1:
            queue_drop(coin, addr)
            result = "Success"
            msg = "Thankyou for request, funds should arrive in "+addr+" within 5 min."

        else:
            result = "Denied"
            msg = "Thankyou for request, your address balance is above the faucet limit. Please try again later."

        resp.update({"Result": result})
        resp["Response"].update({"Message": msg})
        return resp

def get_faucet_balances():
    balances = {}
    for node in node_list:
        balances.update({
            node:{}
        })
        for coin in ["RICK", "MORTY"]:
            try:
                node_rpc = FaucetRPC(node, rpc_ports[coin])
                balances[node].update({
                    coin:node_rpc.rpc.getbalance()
                })
            except:
                balances[node].update({
                    coin:"RPC Error. Is daemon running?"
                })
    return balances

def get_rpc(coin):
    node = random.choice(node_list)
    port = rpc_ports[coin]
    return FaucetRPC(node, port)