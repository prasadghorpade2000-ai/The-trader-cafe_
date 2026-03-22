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
        else: st.error("Galat Password!")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title("Trader's Cafe Panel")
choice = st.sidebar.radio("Go to", ["Dashboard", "Pending Bills", "Daily Sales Report", "Manage Menu Items", "Settings"])
if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()

# --- 4. DASHBOARD (SETTLEMENT LOGIC) ---
if choice == "Dashboard":
    st.header("📍 Table Management")
    selected_tab = st.selectbox("Select Table", list(st.session_state.tables.keys()))
    
    c1, c2 = st.columns(2)
    with c1:
        cat = st.selectbox("Category", list(st.session_state.menu.keys()))
        item = st.selectbox("Item", list(st.session_state.menu[cat].keys()))
        if st.button("➕ Add to Bill"):
            price = st.session_state.menu[cat][item]
            st.session_state.tables[selected_tab].append({"id": datetime.now().timestamp(), "Item": item, "Price": price})
            st.rerun()

    with c2:
        st.subheader(f"Current Bill: {selected_tab}")
        items_in_table = st.session_state.tables[selected_tab]
        
        if items_in_table:
            total = sum(d['Price'] for d in items_in_table)
            for idx, entry in enumerate(items_in_table):
                col_i, col_b = st.columns()
                col_i.write(f"{entry['Item']} - ₹{entry['Price']}")
                if col_b.button("❌", key=f"del_{entry['id']}"):
                    st.session_state.tables[selected_tab].pop(idx)
                    st.rerun()
            
            st.write(f"### Total: ₹{total}")
            st.divider()
            
            # Detailed Settlement
            st.write("**Payment Breakup:**")
            cash_amt = st.number_input("Cash Amount Received", min_value=0.0, value=float(total), step=1.0)
            online_amt = st.number_input("Online Amount Received", min_value=0.0, value=0.0, step=1.0)
            
            remaining = total - (cash_amt + online_amt)
            if remaining > 0:
                st.warning(f"Pending Amount: ₹{remaining}")
            elif remaining < 0:
                st.success(f"Change to return: ₹{abs(remaining)}")

            cust_phone = st.text_input("WhatsApp Number", placeholder="9876543210")
            
            # Settlement Buttons
            col_acc, col_pend = st.columns(2)
            
            if col_acc.button("✅ Settle Full Bill"):
                st.session_state.sales.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Date_Only": datetime.now().strftime("%Y-%m-%d"),
                    "Table": selected_tab, "Total": total, "Cash": cash_amt, "Online": online_amt, "Status": "Success"
                })
                # WhatsApp Logic
                insta_url = "https://www.instagram.com/the_trader_cafe?igsh=bHVzcm1pbWY4MXlq"
                bill_msg = f"*--- THE TRADER'S CAFE ---*\nTotal: ₹{total}\nCash: ₹{cash_amt}\nOnline: ₹{online_amt}\n\nFollow us: {insta_url}"
                if cust_phone:
                    st.markdown(f"[📲 Send Bill](https://wa.me/91{cust_phone}?text={urllib.parse.quote(bill_msg)})")
                st.session_state.tables[selected_tab] = []
                st.success("Bill Settled!")

            if col_pend.button("⏳ Mark as Pending"):
                st.session_state.sales.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Date_Only": datetime.now().strftime("%Y-%m-%d"),
                    "Table": selected_tab, "Total": total, "Cash": cash_amt, "Online": online_amt, "Status": "Pending"
                })
                st.session_state.tables[selected_tab] = []
                st.info("Added to Pending Bills")

# --- 5. PENDING BILLS ---
elif choice == "Pending Bills":
    st.header("⏳ Pending/Unpaid Bills")
    if st.session_state.sales:
        df = pd.DataFrame(st.session_state.sales)
        pending_df = df[df['Status'] == 'Pending']
        if not pending_df.empty:
            st.dataframe(pending_df)
            st.write(f"**Total Outstanding: ₹{pending_df['Total'].sum() - (pending_df['Cash'].sum() + pending_df['Online'].sum())}**")
        else: st.success("No pending bills!")

# --- 6. DAILY SALES REPORT (CASH vs ONLINE) ---
elif choice == "Daily Sales Report":
    st.header("📊 Daily Business Summary")
    today = datetime.now().strftime("%Y-%m-%d")
    
    if st.session_state.sales:
        df = pd.DataFrame(st.session_state.sales)
        df_today = df[(df['Date_Only'] == today) & (df['Status'] == 'Success')]
        
        st.write(f"### Report for {today}")
        col_c, col_o, col_t = st.columns(3)
        
        cash_total = df_today['Cash'].sum()
        online_total = df_today['Online'].sum()
        grand_total = cash_total + online_total
        
        col_c.metric("Cash Sale", f"₹{cash_total}")
        col_o.metric("Online Sale", f"₹{online_total}")
        col_t.metric("Total Business", f"₹{grand_total}", delta=f"{len(df_today)} Orders")
        
        st.write("---")
        st.dataframe(df_today[["Date", "Table", "Total", "Cash", "Online"]])
    else: st.info("No sales data.")

# --- 7. SETTINGS & MENU (Purana Logic) ---
elif choice == "Settings":
    st.header("⚙️ Configuration")
    # Table/Category Add/Delete logic yahan rahega...
    if st.button("Add 1 Table"):
        new_id = f"Table {len(st.session_state.tables) + 1}"
        st.session_state.tables[new_id] = []
        st.rerun()
    
    del_tab = st.selectbox("Delete Table", ["Select"] + list(st.session_state.tables.keys()))
    if st.button("Delete Table") and del_tab != "Select":
        del st.session_state.tables[del_tab]
        st.rerun()

elif choice == "Manage Menu Items":
    st.header("📝 Menu Edit")
    for cat, items in st.session_state.menu.copy().items():
        with st.expander(cat):
            for old_n, pr in items.items():
                st.session_state.menu[cat][old_n] = st.number_input(f"Price: {old_n}", value=pr, key=f"p_{old_n}")
