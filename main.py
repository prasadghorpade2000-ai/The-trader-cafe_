import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# --- 1. DATABASE SETUP ---
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Pizza": {"Golden Corn": 59, "Testy Tomato": 49, "Shiney Onion": 49, "Choppy Capcicum": 49, "Spicy Shezwan": 79, "Mighty Paneer pizza": 79, "Mixed Veges Spicy": 69},
        "Burger": {"Classic Burger": 39, "Cheese burger": 55, "Spicy salsa": 59, "Royal paneer Grill burger": 69},
        "Sandwich": {"Grill Sandwich": 39, "Vegs Cheese Sandwich": 49, "Schezwan Sandwich": 49, "Choklet sandwich": 59},
        "Combo Offers": {"Forex Combo": 299, "Nifty Special": 239, "Back Benchers": 249, "Student Special": 189, "Hunger Killer": 169}
    }

if 'sales' not in st.session_state: st.session_state.sales = []
if 'tables' not in st.session_state: st.session_state.tables = {f"Table {i}": [] for i in range(1, 16)}
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- 2. LOGIN ---
if not st.session_state.logged_in:
    st.title("🔐 Trader's Cafe Login")
    user = st.text_input("Username")
    passw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and passw == "trader77":
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("wrong Password!")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title("Trader's Cafe Panel")
choice = st.sidebar.radio("Go to", ["Dashboard", "Sales Report", "Manage Menu Items", "Settings"])
if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()

# --- 4. DASHBOARD (BILLING & INSTAGRAM DM) ---
if choice == "Dashboard":
    st.header("📍 Table Management")
    selected_tab = st.selectbox("Select Table", list(st.session_state.tables.keys()))
    
    c1, c2 = st.columns(2)
    with c1:
        cat = st.selectbox("Category", list(st.session_state.menu.keys()))
        item = st.selectbox("Item", list(st.session_state.menu[cat].keys()))
        if st.button("Add to Bill"):
            price = st.session_state.menu[cat][item]
            st.session_state.tables[selected_tab].append({"Item": item, "Price": price})
            st.rerun()

    with c2:
        st.subheader(f"Current Bill: {selected_tab}")
        if st.session_state.tables[selected_tab]:
            df_curr = pd.DataFrame(st.session_state.tables[selected_tab])
            st.table(df_curr)
            total = df_curr['Price'].sum()
            st.write(f"### Total: ₹{total}")
            
            # --- INSTAGRAM DIRECT BILLING ---
            insta_user = st.text_input("Customer Insta Username", placeholder="example_user")
            pay_mode = st.selectbox("Payment Mode", ["Cash", "Online"])
            
            if st.button("Settle & Send Bill to Insta"):
                # Bill details formatting
                items_list = "\n".join([f"- {d['Item']}: ₹{d['Price']}" for d in st.session_state.tables[selected_tab]])
                cafe_insta = "https://www.instagram.com/the_trader_cafe"
                
                full_bill = f"--- THE TRADER'S CAFE ---\nItems Order Kiye:\n{items_list}\n\nTOTAL BILL: ₹{total}\nPayment: {pay_mode}\n\nFollow Us: {cafe_insta}"
                
                # Copy to Clipboard message for user
                st.info("Bill Copy Karein aur niche button dabayein:")
                st.code(full_bill)
                
                # Direct Link to Customer's DM (Agar username diya hai)
                if insta_user:
                    dm_url = f"https://www.instagram.com/direct/t/{insta_user}/"
                    st.markdown(f"[📩 Open Customer's Insta DM]({dm_url})")
                else:
                    st.warning("Username nahi dala, manually search karein.")

                # Save Sale
                st.session_state.sales.append({"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Table": selected_tab, "Total": total, "Mode": pay_mode, "Status": "Success"})
                st.session_state.tables[selected_tab] = []

            # --- CANCEL ORDER ---
            st.divider()
            reason = st.text_input("Cancellation Reason")
            if st.button("Cancel Order"):
                if reason:
                    st.session_state.sales.append({"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Table": selected_tab, "Total": total, "Status": "Cancelled", "Reason": reason})
                    st.session_state.tables[selected_tab] = []
                    st.rerun()
                else: st.error("Reason likhna zaroori hai!")

# --- 5. SETTINGS (NEW ITEM LAUNCH) ---
elif choice == "Settings":
    st.header("⚙️ Settings & New Launch")
    
    with st.expander("🚀 Launch New Item"):
        launch_cat = st.selectbox("Category", list(st.session_state.menu.keys()))
        launch_name = st.text_input("New Item Name")
        launch_price = st.number_input("Launch Price", min_value=0)
        if st.button("Launch Now"):
            if launch_name:
                st.session_state.menu[launch_cat][launch_name] = launch_price
                st.success(f"{launch_name} launched in {launch_cat}!")
            else: st.error("Item ka naam likhein.")

    if st.button("Add 1 New Table"):
        new_t = f"Table {len(st.session_state.tables) + 1}"
        st.session_state.tables[new_t] = []
        st.success(f"{new_t} added!")

# --- 6. MANAGE MENU ---
elif choice == "Manage Menu Items":
    st.header("📝 Edit Item Names & Rates")
    # Same as before for editing names and prices
    for cat, items in st.session_state.menu.copy().items():
        with st.expander(cat):
            for old_n, pr in items.items():
                new_n = st.text_input(f"Name", value=old_n, key=f"n_{old_n}")
                new_p = st.number_input(f"Rate", value=pr, key=f"p_{old_n}")
                if new_n != old_n or new_p != pr:
                    st.session_state.menu[cat][new_n] = st.session_state.menu[cat].pop(old_n)
                    st.session_state.menu[cat][new_n] = new_p
                    st.rerun()
