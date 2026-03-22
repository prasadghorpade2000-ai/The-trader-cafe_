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

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("Trader's Cafe Panel")
choice = st.sidebar.radio("Go to", ["Dashboard", "Pending Bills", "Daily Sales Report", "Manage Menu Items", "Settings"])
if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()

# --- 4. DASHBOARD (BILLING & PRINT) ---
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
            
            # Settlement & Print Options
            cash_amt = st.number_input("Cash Amount", min_value=0.0, value=float(total))
            online_amt = st.number_input("Online Amount", min_value=0.0, value=0.0)
            cust_phone = st.text_input("WhatsApp Number", placeholder="9876543210")
            
            # Print Layout Generator
            receipt_text = f"--- THE TRADER'S CAFE ---\nDate: {datetime.now().strftime('%d/%m/%Y %H:%M')}\nTable: {selected_tab}\n----------------------\n"
            for d in items_in_table:
                receipt_text += f"{d['Item'][:15]:<15} ₹{d['Price']:>4}\n"
            receipt_text += f"----------------------\nTOTAL: ₹{total}\nCash: ₹{cash_amt} | Online: ₹{online_amt}\n----------------------\nVisit Again! @the_trader_cafe"

            col_s, col_p = st.columns(2)
            if col_s.button("✅ Settle & WhatsApp"):
                st.session_state.sales.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Date_Only": datetime.now().strftime("%Y-%m-%d"),
                    "Table": selected_tab, "Total": total, "Cash": cash_amt, "Online": online_amt, "Status": "Success"
                })
                insta_url = "https://www.instagram.com/the_trader_cafe?igsh=bHVzcm1pbWY4MXlq"
                bill_msg = f"*--- THE TRADER'S CAFE ---*\nTotal: ₹{total}\nCash: ₹{cash_amt}\nOnline: ₹{online_amt}\n\nFollow: {insta_url}"
                if cust_phone:
                    st.markdown(f"[📲 Send WhatsApp Bill](https://wa.me/91{cust_phone}?text={urllib.parse.quote(bill_msg)})")
                st.session_state.tables[selected_tab] = []
                st.success("Bill Settled!")

            if col_p.button("🖨️ Print Receipt"):
                st.text_area("Receipt Preview (Copy to Print)", receipt_text, height=200)
                st.info("Bluetooth Printer se connect karke Print karein.")

            if st.button("⏳ Mark as Pending"):
                st.session_state.sales.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Date_Only": datetime.now().strftime("%Y-%m-%d"),
                    "Table": selected_tab, "Total": total, "Cash": cash_amt, "Online": online_amt, "Status": "Pending"
                })
                st.session_state.tables[selected_tab] = []
                st.info("Added to Pending")

# --- 5. DAILY SALES REPORT (HISAAB) ---
elif choice == "Daily Sales Report":
    st.header("📊 Daily Business Report")
    today = datetime.now().strftime("%Y-%m-%d")
    
    if st.session_state.sales:
        df = pd.DataFrame(st.session_state.sales)
        df_today = df[(df['Date_Only'] == today) & (df['Status'] == 'Success')]
        
        c_sale = df_today['Cash'].sum()
        o_sale = df_today['Online'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Cash In Hand", f"₹{c_sale}")
        col2.metric("Online Collection", f"₹{o_sale}")
        col3.metric("Grand Total Today", f"₹{c_sale + o_sale}")
        
        st.write("### Today's Orders")
        st.dataframe(df_today[["Date", "Table", "Total", "Cash", "Online"]])
        
        # Download Option
        csv = df_today.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Daily Report (CSV)", csv, f"Report_{today}.csv", "text/csv")
    else: st.info("No data for today.")

# --- 6. SETTINGS (ADD/DELETE) ---
elif choice == "Settings":
    st.header("⚙️ Settings")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("➕ Add Table"):
            st.session_state.tables[f"Table {len(st.session_state.tables)+1}"] = []
            st.rerun()
    with col_b:
        t_del = st.selectbox("Delete Table", ["Select"] + list(st.session_state.tables.keys()))
        if st.button("🗑️ Delete") and t_del != "Select":
            del st.session_state.tables[t_del]
            st.rerun()

    st.divider()
    # New Category
    new_cat = st.text_input("New Category Name")
    if st.button("Add Category") and new_cat:
        st.session_state.menu[new_cat] = {}
        st.rerun()
