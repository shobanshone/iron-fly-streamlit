import os
from datetime import datetime, date, timedelta, timezone
from math import ceil
from kiteconnect import KiteConnect


kite = KiteConnect(api_key=os.environ["KITE_API_KEY"])
kite.set_access_token(os.environ["KITE_ACCESS_TOKEN"])
# --------------------------------
# 🔧 USER SETTINGS
# --------------------------------
# with open("access_token.txt", "r") as f:
#     kite.set_access_token(f.read().strip())


EXPIRIES = {
    "NIFTY": {
    "03 Feb 2026": "03FEB",
    "10 Feb 2026": "10FEB",
    "17 Feb 2026": "17FEB",
    "24 Feb 2026": "24FEB",
    "02 Mar 2026": "02MAR",
    "30 Mar 2026": "30MAR",
    "28 Apr 2026": "28APR",
    "30 Jun 2026": "30JUN",
    "29 Sep 2026": "29SEP",
    "29 Dec 2026": "29DEC",
    "29 Jun 2027": "29JUN",
    "28 Dec 2027": "28DEC",
    "27 Jun 2028": "27JUN",
    "26 Dec 2028": "26DEC",
    "26 Jun 2029": "26JUN",
    "24 Dec 2029": "24DEC",
    "25 Jun 2030": "25JUN",
    "31 Dec 2030": "31DEC"
},
    "SENSEX": {
    "05 Feb 2026": "05FEB",
    "12 Feb 2026": "12FEB",
    "19 Feb 2026": "19FEB",
    "26 Feb 2026": "26FEB",
    "05 Mar 2026": "05MAR",
    "12 Mar 2026": "12MAR",
    "19 Mar 2026": "19MAR",
    "25 Mar 2026": "25MAR",
    "30 Apr 2026": "30APR",
    "25 Jun 2026": "25JUN",
    "24 Sep 2026": "24SEP",
    "31 Dec 2026": "31DEC",
    "24 Jun 2027": "24JUN",
    "30 Dec 2027": "30DEC",
    "29 Jun 2028": "29JUN",
    "28 Dec 2028": "28DEC",
    "28 Jun 2029": "28JUN",
    "27 Dec 2029": "27DEC",
    "27 Jun 2030": "27JUN",
    "26 Dec 2030": "26DEC"
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
        
        kite.place_order(
             variety=kite.VARIETY_REGULAR,
             exchange=exchange,
             tradingsymbol=tradingsymbol,
             transaction_type=transaction,
             quantity=qty,
             product=kite.PRODUCT_NRML,
             order_type=order_type
         )

    place(f"{index_name}{expiry}{ce_buy}CE", "BUY")
    place(f"{index_name}{expiry}{pe_buy}PE", "BUY")
    place(f"{index_name}{expiry}{atm}PE", "SELL")
    place(f"{index_name}{expiry}{atm}CE", "SELL")


