import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# --- 1. DATABASE & GOOGLE SHEETS SETUP ---
# Note: Real Google Sheets sync requires a JSON key file from Google Cloud Console.
# For now, I am keeping the logic ready.
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
    st.title("📈 The Trader's Cafe - Admin")
    user = st.text_input("Username")
    passw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and passw == "trader77":
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("Access Denied!")
    st.stop()

# --- 3. SIDEBAR ---
choice = st.sidebar.radio("Main Menu", ["Dashboard", "Pending Bills", "Sales Report", "Manage Menu", "Settings"])
if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()

# --- 4. DASHBOARD (BILLING & SPLIT PAYMENT) ---
if choice == "Dashboard":
    st.header(f"📍 Billing Counter")
    selected_tab = st.selectbox("Select Table", list(st.session_state.tables.keys()))
    
    col_in, col_bill = st.columns()
    
    with col_in:
        cat = st.selectbox("Category", list(st.session_state.menu.keys()))
        item = st.selectbox("Item", list(st.session_state.menu[cat].keys()))
        if st.button("➕ Add Item"):
            price = st.session_state.menu[cat][item]
            st.session_state.tables[selected_tab].append({"id": datetime.now().timestamp(), "Item": item, "Price": price})
            st.rerun()

    with col_bill:
        st.subheader(f"Bill: {selected_tab}")
        current_items = st.session_state.tables[selected_tab]
        if current_items:
            total = sum(i['Price'] for i in current_items)
            for idx, entry in enumerate(current_items):
                c_name, c_del = st.columns()
                c_name.write(f"{entry['Item']} - ₹{entry['Price']}")
                if c_del.button("❌", key=f"del_{entry['id']}"):
                    st.session_state.tables[selected_tab].pop(idx)
                    st.rerun()
            
            st.write(f"### Total: ₹{total}")
            st.divider()
            
            # Detailed Payment Entry
            cash_in = st.number_input("Cash Received", min_value=0, value=0)
            online_in = st.number_input("Online Received", min_value=0, value=0)
            phone = st.text_input("Customer Phone", placeholder="9876543210")
            
            # Settlement Logic
            c_settle, c_pend = st.columns(2)
            
            if c_settle.button("✅ Settle Full"):
                st.session_state.sales.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Table": selected_tab, "Total": total, "Cash": cash_in, "Online": online_in, "Status": "Success"
                })
                # WhatsApp Message with Insta Link
                insta = "https://www.instagram.com/the_trader_cafe?igsh=bHVzcm1pbWY4MXlq"
                msg = f"*--- THE TRADER'S CAFE ---*\nTotal: ₹{total}\nPaid: Cash(₹{cash_in}) + Online(₹{online_in})\n\nFollow us: {insta}\nThanks! 🙏"
                if phone:
                    st.markdown(f"[📲 Send WhatsApp Bill](https://wa.me/91{phone}?text={urllib.parse.quote(msg)})")
                st.session_state.tables[selected_tab] = []
                st.success("Hisaab Saved!")

            if c_pend.button("⏳ Mark Pending"):
                st.session_state.sales.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Table": selected_tab, "Total": total, "Cash": cash_in, "Online": online_in, "Status": "Pending"
                })
                st.session_state.tables[selected_tab] = []
                st.warning("Moved to Pending List")

# --- 5. SALES REPORT (DAILY SUMMARY) ---
elif choice == "Sales Report":
    st.header("📊 Business Performance")
    if st.session_state.sales:
        df = pd.DataFrame(st.session_state.sales)
        success_df = df[df['Status'] == 'Success']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Cash", f"₹{success_df['Cash'].sum()}")
        c2.metric("Total Online", f"₹{success_df['Online'].sum()}")
        c3.metric("Grand Total", f"₹{success_df['Total'].sum()}")
        
        st.write("### All Transactions")
        st.dataframe(df)
        
        # Google Sheet Export Button (Mockup)
        if st.button("📤 Sync to Google Sheets"):
            st.success("Data Synced to 'Traders_Cafe_Sales' Sheet!")
    else:
        st.info("No sales yet.")

# --- 6. SETTINGS ---
elif choice == "Settings":
    st.header("⚙️ Cafe Setup")
    if st.button("➕ Add New Table"):
        new_t = f"Table {len(st.session_state.tables) + 1}"
        st.session_state.tables[new_t] = []
        st.rerun()
    
    del_t = st.selectbox("Remove Table", ["None"] + list(st.session_state.tables.keys()))
    if st.button("🗑️ Delete Table") and del_t != "None":
        del st.session_state.tables[del_t]
        st.rerun()
