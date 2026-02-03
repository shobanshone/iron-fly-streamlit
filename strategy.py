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
    # Weekly expiries (YYMDD)
    "10 Feb 2026": "26210",
    "17 Feb 2026": "26217",
    "24 Feb 2026": "26FEB",
    "02 Mar 2026": "26302",

    # Month-end expiries (YYMMM)
    "30 Mar 2026": "26MAR",
    "28 Apr 2026": "26APR",
    "30 Jun 2026": "26JUN",
    "29 Sep 2026": "26SEP",
    "29 Dec 2026": "26DEC",

    "29 Jun 2027": "27JUN",
    "28 Dec 2027": "27DEC",

    "27 Jun 2028": "28JUN",
    "26 Dec 2028": "28DEC",

    "26 Jun 2029": "29JUN",
    "24 Dec 2029": "29DEC",

    "25 Jun 2030": "30JUN",
    "31 Dec 2030": "30DEC"

},
    "SENSEX": {
   
    "05 Feb 2026": "26205",
    "12 Feb 2026": "26212",
    "19 Feb 2026": "26219",
    "26 Feb 2026": "26FEB",

    "05 Mar 2026": "26305",
    "12 Mar 2026": "26312",
    "19 Mar 2026": "26319",
    "25 Mar 2026": "26MAR",
    "30 Apr 2026": "26APR",

    "25 Jun 2026": "26JUN",
    "24 Sep 2026": "26SEP",

    "24 Jun 2027": "27JUN",
    "30 Dec 2027": "27DEC",

    "29 Jun 2028": "28JUN",
    "28 Dec 2028": "28DEC",


    # Month-end expiries → YYMMM
    "31 Dec 2026": "26DEC"
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


def get_kite_user_name():
    try:
        profile = kite.profile()
        return profile.get("user_name") or profile.get("user_id")
    except Exception:
        return None

def execute_iron_fly(
    index_name,
    atm,
    hedge_distance,
    expiry_key,
    lots,
    order_type,
    dry_run=False
):
    config = INDEX_CONFIG[index_name]
    lot_size = config["lot_size"]
    exchange = config["exchange"]

    qty = lot_size * lots
    expiry = EXPIRIES[index_name][expiry_key]

    ce_buy = atm + hedge_distance
    pe_buy = atm - hedge_distance

    orders = []

    def place(tradingsymbol, transaction):
        if dry_run:
            return {
                "variety" : kite.VARIETY_REGULAR,
                "exchange" : exchange,
                "symbol": tradingsymbol,
                "transaction": transaction,
                "qty": qty,
                "product" : kite.PRODUCT_NRML,  
                "order_type": order_type
            }
        else:
            order_id = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=exchange,
                tradingsymbol=tradingsymbol,
                transaction_type=transaction,
                quantity=qty,
                product=kite.PRODUCT_NRML,
                order_type=order_type
            )
            return order_id

    # BUY hedges
    orders.append(place(f"{index_name}{expiry}{ce_buy}CE", "BUY"))
    orders.append(place(f"{index_name}{expiry}{pe_buy}PE", "BUY"))

    # SELL ATM
    orders.append(place(f"{index_name}{expiry}{atm}PE", "SELL"))
    orders.append(place(f"{index_name}{expiry}{atm}CE", "SELL"))

    return orders
