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
if 'cancelled_items' not in st.session_state: st.session_state.cancelled_items = []
if 'tables' not in st.session_state: st.session_state.tables = {f"Table {i}": [] for i in range(1, 16)}
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- 2. LOGIN SYSTEM ---
if not st.session_state.logged_in:
    st.title("🔐 Trader's Cafe Login")
    user = st.text_input("Username")
    passw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and passw == "trader77":
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("Galat Password!")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title("Trader's Cafe Panel")
choice = st.sidebar.radio("Go to", ["Dashboard", "Daily Sales Report", "Manage Menu Items", "Settings"])
if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()

# --- 4. DASHBOARD (ITEM-WISE CANCEL LOGIC) ---
if choice == "Dashboard":
    st.header("📍 Table Management")
    selected_tab = st.selectbox("Select Table", list(st.session_state.tables.keys()))
    
    c1, c2 = st.columns(2)
    with c1:
        cat = st.selectbox("Category", list(st.session_state.menu.keys()))
        item = st.selectbox("Item", list(st.session_state.menu[cat].keys()))
        if st.button("➕ Add to Bill"):
            price = st.session_state.menu[cat][item]
            # Unique ID for each order entry
            st.session_state.tables[selected_tab].append({
                "id": datetime.now().timestamp(), 
                "Item": item, 
                "Price": price,
                "Category": cat
            })
            st.rerun()

    with c2:
        st.subheader(f"Current Bill: {selected_tab}")
        items_in_table = st.session_state.tables[selected_tab]
        
        if items_in_table:
            total = sum(d['Price'] for d in items_in_table)
            
            # Displaying items with individual cancel option
            for idx, entry in enumerate(items_in_table):
                col_i, col_b = st.columns()
                col_i.write(f"**{entry['Item']}** - ₹{entry['Price']}")
                
                # Individual Cancel Button for each item
                if col_b.button("🗑️ Cancel", key=f"del_{entry['id']}"):
                    # Log to Cancelled Items list
                    st.session_state.cancelled_items.append({
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Table": selected_tab,
                        "Item": entry['Item'],
                        "Price": entry['Price'],
                        "Status": "Individual Cancel"
                    })
                    st.session_state.tables[selected_tab].pop(idx)
                    st.success(f"{entry['Item']} cancelled!")
                    st.rerun()
            
            st.divider()
            st.write(f"### Total: ₹{total}")
            
            # Settlement Section
            cash_amt = st.number_input("Cash Received", min_value=0, value=0)
            online_amt = st.number_input("Online Received", min_value=0, value=0)
            cust_phone = st.text_input("WhatsApp Number", placeholder="9876543210")
            
            if st.button("✅ Settle & Save Sale"):
                st.session_state.sales.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Date_Only": datetime.now().strftime("%Y-%m-%d"),
                    "Table": selected_tab, 
                    "Total": total, 
                    "Cash": cash_amt, 
                    "Online": online_amt, 
                    "Status": "Success"
                })
                # WhatsApp logic here (as per previous version)
                st.session_state.tables[selected_tab] = []
                st.success("Bill Settled Successfully!")
                st.rerun()

# --- 5. DAILY SALES REPORT (WITH CANCELLED LIST) ---
elif choice == "Daily Sales Report":
    st.header("📊 Daily Business Summary")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 5.1 SUCCESS SALES
    st.subheader("✅ Success Sales")
    if st.session_state.sales:
        df_sales = pd.DataFrame(st.session_state.sales)
        df_today = df_sales[(df_sales['Date_Only'] == today) & (df_sales['Status'] == 'Success')]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Cash Sale", f"₹{df_today['Cash'].sum()}")
        c2.metric("Online Sale", f"₹{df_today['Online'].sum()}")
        c3.metric("Total Business", f"₹{df_today['Total'].sum()}")
        st.dataframe(df_today)
    else: st.info("Aaj koi sale nahi hui.")

    st.divider()

    # 5.2 CANCELLED ITEMS LIST
    st.subheader("🚫 Cancelled Items Report")
    if st.session_state.cancelled_items:
        df_cancel = pd.DataFrame(st.session_state.cancelled_items)
        # Filter for today
        df_cancel_today = df_cancel[df_cancel['Date'].str.contains(today)]
        
        if not df_cancel_today.empty:
            st.warning(f"Total {len(df_cancel_today)} items were cancelled today.")
            st.table(df_cancel_today)
            st.write(f"**Lost Revenue (Cancelled): ₹{df_cancel_today['Price'].sum()}**")
        else: st.info("Aaj koi item cancel nahi hua.")
    else: st.info("No cancellation history.")

# --- 6. SETTINGS & MENU (Rest of the logic) ---
# ... (Previous Manage Menu & Settings logic remains same)
