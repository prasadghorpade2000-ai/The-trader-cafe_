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
# Naya record cancelled items ke liye
if 'cancelled_log' not in st.session_state: st.session_state.cancelled_log = []
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
        else: st.error("Galat Password!")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title("Trader's Cafe Panel")
choice = st.sidebar.radio("Go to", ["Dashboard", "Sales Report", "Manage Menu Items", "Settings"])
if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()

# --- 4. DASHBOARD ---
if choice == "Dashboard":
    st.header("📍 Table Management")
    selected_tab = st.selectbox("Select Table", list(st.session_state.tables.keys()))
    
    c1, c2 = st.columns(2)
    with c1:
        cat = st.selectbox("Category", list(st.session_state.menu.keys()))
        item = st.selectbox("Item", list(st.session_state.menu[cat].keys()))
        if st.button("Add to Bill"):
            price = st.session_state.menu[cat][item]
            # Unique ID taaki sahi item delete ho
            st.session_state.tables[selected_tab].append({
                "id": datetime.now().timestamp(), 
                "Item": item, 
                "Price": price
            })
            st.rerun()

    with c2:
        st.subheader(f"Current Bill: {selected_tab}")
        items = st.session_state.tables[selected_tab]
        if items:
            total = 0
            # --- ITEM WISE LIST WITH CANCEL OPTION ---
            for idx, row in enumerate(items):
                col_name, col_btn = st.columns()
                col_name.write(f"{row['Item']} - ₹{row['Price']}")
                if col_btn.button("🗑️", key=f"del_{row['id']}"):
                    # Cancelled item ko log mein save karo
                    st.session_state.cancelled_log.append({
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Table": selected_tab, "Item": row['Item'], "Price": row['Price']
                    })
                    st.session_state.tables[selected_tab].pop(idx)
                    st.rerun()
                total += row['Price']
            
            st.write(f"### Total: ₹{total}")
            st.divider()
            
            # Settlement Section
            cust_phone = st.text_input("WhatsApp Number", placeholder="9876543210")
            pay_mode = st.selectbox("Payment Mode", ["Cash", "Online", "UPI"])
            
            if st.button("✅ Settle & WhatsApp"):
                # Save to Sales
                st.session_state.sales.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Date_Only": datetime.now().strftime("%Y-%m-%d"),
                    "Table": selected_tab, "Total": total, "Mode": pay_mode, "Status": "Success"
                })
                # WhatsApp URL
                items_text = "\n".join([f"• {d['Item']}: ₹{d['Price']}" for d in items])
                bill_msg = f"*--- THE TRADER'S CAFE ---*\n\n{items_text}\n\n*TOTAL: ₹{total}*\nMode: {pay_mode}\n\nThanks! 🙏"
                if cust_phone:
                    st.markdown(f"[📲 Send Bill](https://wa.me/91{cust_phone}?text={urllib.parse.quote(bill_msg)})")
                
                st.session_state.tables[selected_tab] = []
                st.success("Sale Recorded!")

            if st.button("🧹 Clear Table"):
                st.session_state.tables[selected_tab] = []
                st.rerun()

# --- 5. SALES REPORT (SUCCESS + CANCELLED) ---
elif choice == "Sales Report":
    st.header("📊 Business Report")
    today = datetime.now().strftime("%Y-%m-%d")
    
    tab1, tab2 = st.tabs(["✅ Success Sales", "🚫 Cancelled Items"])
    
    with tab1:
        if st.session_state.sales:
            df = pd.DataFrame(st.session_state.sales)
            df_today = df[df['Date'].str.contains(today)]
            st.write(f"### Today's Total: ₹{df_today[df_today['Status']=='Success']['Total'].sum()}")
            st.dataframe(df_today)
        else: st.info("No sales yet.")

    with tab2:
        if st.session_state.cancelled_log:
            df_can = pd.DataFrame(st.session_state.cancelled_log)
            df_can_today = df_can[df_can['Date'].str.contains(today)]
            st.write(f"### Items Cancelled Today: {len(df_can_today)}")
            st.table(df_can_today)
        else: st.info("No items cancelled today.")

# --- 6. SETTINGS & MENU (Purana Logic) ---
elif choice == "Settings":
    st.header("⚙️ Settings")
    if st.button("Add 1 Table"):
        new_t = f"Table {len(st.session_state.tables) + 1}"
        st.session_state.tables[new_t] = []
        st.rerun()

elif choice == "Manage Menu Items":
    st.header("📝 Menu Edit")
    for cat, items in st.session_state.menu.copy().items():
        with st.expander(cat):
            for old_n, pr in items.items():
                new_p = st.number_input(f"Rate: {old_n}", value=pr, key=f"p_{old_n}")
                if new_p != pr:
                    st.session_state.menu[cat][old_n] = new_p
                    st.rerun()
