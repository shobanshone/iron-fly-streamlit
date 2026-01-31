


"""
Full-featured Kite Connect Iron Condor runner (simulation + live-ready)

Features:
 - Wait until 09:29:59 IST -> compute ATM (nearest 50) & wings (±300)
 - Find NFO option instruments for nearest expiry
 - Place entry as: BUY wings first, SELL ATM legs
 - Robust order handling: LIMIT (recommended) with dynamic price or MARKET fallback
 - Poll order status until complete; handle partial fills and attempt to fill remainder
 - Monitor spot: immediate square-off if |spot - ATM| >= 150, else square-off at 15:20 IST
 - Logging to CSV (events), email & webhook alerts on entry and exit
 - DRY_RUN mode: simulates orders & fills for full tests (default True)
"""
import os
import json
import csv
import time
import tempfile
import traceback
import requests
import smtplib
import re
import statistics
from datetime import datetime, date, timedelta, timezone
from math import ceil
from kiteconnect import KiteConnect



EXPIRIES = {
    "NIFTY": {
        "24 JAN 2026": "26JAN",
        "31 JAN 2026": "31JAN",
        "07 FEB 2026": "07FEB"
    },
    "SENSEX": {
        "24 JAN 2026": "26JAN",
        "31 JAN 2026": "31JAN"
    }
}

INDEX_CONFIG = {
    "NIFTY": {
        "lot_size": 65,
        "exchange": "NFO"
    },
    "SENSEX": {
        "lot_size": 20,
        "exchange": "BFO"
    }
}


def execute_iron_fly(
    index_name,
    atm,
    hedge_distance,
    expiry_key,
    lots,
    order_type
):
    config = INDEX_CONFIG[index_name]
    lot_size = config["lot_size"]
    exchange = config["exchange"]

    qty = lot_size * lots
    expiry = EXPIRIES[index_name][expiry_key]

    ce_buy = atm + hedge_distance
    pe_buy = atm - hedge_distance

    def place(tradingsymbol, transaction):
        print("dddd")
        # kite.place_order(
        #     variety=kite.VARIETY_REGULAR,
        #     exchange=exchange,
        #     tradingsymbol=tradingsymbol,
        #     transaction_type=transaction,
        #     quantity=qty,
        #     product=kite.PRODUCT_NRML,
        #     order_type=order_type
        # )

    place(f"{index_name}{expiry}{ce_buy}CE", "BUY")
    place(f"{index_name}{expiry}{pe_buy}PE", "BUY")
    place(f"{index_name}{expiry}{atm}PE", "SELL")
    place(f"{index_name}{expiry}{atm}CE", "SELL")


