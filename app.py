import streamlit as st
import os
from strategy import execute_iron_fly, EXPIRIES, get_kite_user_name

# ---------- SIMPLE AUTH ----------
APP_PIN = os.environ["APP_PIN"]   # change this

pin = st.text_input("🔐 Enter PIN", type="password")

#user_name = get_kite_user_name()
if pin != APP_PIN:
    st.warning("Unauthorized access")
    st.stop()
# -------------------------------------------------
# Page config (mobile-friendly)
# -------------------------------------------------
st.set_page_config(
    page_title="Iron Fly Trader",
    layout="wide"
)

st.title("📱 Iron Fly Trader")


if user_name:
    st.success(f"👤 Connected Kite Account: **{user_name}**")
else:
    st.error("❌ Kite account not connected (invalid/expired token)")
    st.stop()

# -------------------------------------------------
# SIDEBAR — All inputs (best for mobile)
# -------------------------------------------------
with st.sidebar:
    st.header("⚙️ Strategy Inputs")

    index_name = st.selectbox("Index", ["NIFTY", "SENSEX"])

    # Dynamic defaults based on index
    if index_name == "NIFTY":
        atm_default = 25000
        hedge_min = 50
        hedge_step = 50
    else:
        atm_default = 82000
        hedge_min = 200
        hedge_step = 100

    expiry_key = st.selectbox(
        "Expiry",
        list(EXPIRIES[index_name].keys())
    )

    atm = st.number_input(
        "ATM Strike",
        value=atm_default,
        step=hedge_step
    )

    hedge_distance = st.number_input(
        "Hedge Distance",
        min_value=hedge_min,
        value=hedge_min,
        step=hedge_step
    )

    lots = st.number_input(
        "Lots",
        min_value=1,
        step=1
    )

    order_type = st.selectbox(
        "Order Type",
        ["MARKET", "LIMIT"]
    )

# -------------------------------------------------
# CALCULATE LEGS (for summary)
# -------------------------------------------------
ce_sell = atm
pe_sell = atm
ce_buy = atm + hedge_distance
pe_buy = atm - hedge_distance

# -------------------------------------------------
# MAIN SCREEN — Strategy summary (NO SCROLL)
# -------------------------------------------------
st.markdown("### 📋 Strategy Summary")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Instrument Details**")
    st.write(f"""
    **Index:** {index_name}  

    **Expiry:** {expiry_key}  

    **ATM Strike:** {atm}  

    **Lots:** {lots}  
    
    **Order Type:** {order_type}
    """)

with col2:
    st.markdown("**Iron Fly Legs**")
    st.write(f"""
    🟢 **BUY PE**  → {pe_buy}       
    🔴 **SELL PE** → {pe_sell}  

    🔴 **SELL CE** → {ce_sell}  
    🟢 **BUY CE**  → {ce_buy}  

    """)

st.markdown("---")
dry_run = st.toggle("🧪 Dry Run (No real orders)", value=False)

# -------------------------------------------------
# CONFIRMATION + EXECUTION (SAFE)
# -------------------------------------------------
confirm = st.checkbox("I confirm to place this trade")

if "executed" not in st.session_state:
    st.session_state.executed = False

if st.button("🚀 EXECUTE IRON FLY"):
    if not confirm:
        st.error("❌ Please confirm before executing the trade")
    elif st.session_state.executed:
        st.warning("⚠️ Trade already executed. Refresh the page to trade again.")
    else:
        orders = execute_iron_fly(
            index_name=index_name,
            atm=atm,
            hedge_distance=hedge_distance,
            expiry_key=expiry_key,
            lots=lots,
            order_type=order_type,
            dry_run=dry_run
        )
        st.session_state.executed = True
        if dry_run:
            st.info("🧪 DRY RUN — No real orders placed")
            st.json(orders)
        else:
            st.success("✅ Orders sent to Kite")
            st.write("Order IDs:")
            st.write(orders)
        st.success("✅ Iron Fly executed successfully")

if st.session_state.executed:
    st.info("🔒 Execution locked. Refresh page for next trade.")
