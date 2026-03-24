import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import json
import os
import io  # Required for Excel download buffer

# --- 0. DATA PERSISTENCE LOGIC ---
DB_FILE = "cafe_data.json"

def save_data():
    """Saves all session state data to a JSON file."""
    data = {
        "menu": st.session_state.menu,
        "sales": st.session_state.sales,
        "inventory": st.session_state.inventory,
        "daily_archive": st.session_state.daily_archive,
        "tables": st.session_state.tables
    }
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    """Loads data from the JSON file if it exists."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return None

# Initial Load
saved_data = load_data()

# --- 1. DATABASE SETUP ---
if 'menu' not in st.session_state:
    st.session_state.menu = saved_data["menu"] if saved_data else {
        "Pizza": {"Golden Corn": 59, "Testy Tomato": 49, "Shiney Onion": 49, "Choppy Capcicum": 49, "Spicy Shezwan": 79, "Mighty Paneer pizza": 79, "Mixed Veges Spicy": 69},
        "Burger": {"Classic Burger": 39, "Cheese burger": 55, "Spicy salsa": 59, "Royal paneer Grill burger": 69},
        "Sandwich": {"Grill Sandwich": 39, "Vegs Cheese Sandwich": 49, "Schezwan Sandwich": 49, "Choklet sandwich": 59},
        "Combo Offers": {"Forex Combo": 299, "Nifty Special": 239, "Back Benchers": 249, "Student Special": 189, "Hunger Killer": 169}
    }

if 'sales' not in st.session_state: st.session_state.sales = saved_data["sales"] if saved_data else []
if 'tables' not in st.session_state: st.session_state.tables = saved_data["tables"] if saved_data else {f"Table {i}": [] for i in range(1, 16)}
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'inventory' not in st.session_state:
    st.session_state.inventory = saved_data["inventory"] if saved_data else {"Pizza Bun": {"added": 0, "sold": 0}, "Burger Bun": {"added": 0, "sold": 0}}
if 'daily_archive' not in st.session_state: st.session_state.daily_archive = saved_data["daily_archive"] if saved_data else []

CAFE_INSTA = "https://www.instagram.com/the_trader_cafe?igsh=bHVzcm1pbWY4MXlq"

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
st.sidebar.markdown(f"[📸 Follow us on Instagram]({CAFE_INSTA})")
st.sidebar.divider()

choice = st.sidebar.radio("Go to", ["Dashboard", "Sales Report", "Inventory", "Manage Menu Items", "Settings"])

st.sidebar.divider()
if st.sidebar.button("💾 Force Save Now"):
    save_data()
    st.sidebar.success("All data saved successfully!")

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
        if st.button("➕ Add to Bill"):
            price = st.session_state.menu[cat][item]
            st.session_state.tables[selected_tab].append({
                "id": datetime.now().timestamp(), "Item": item, "Price": price, "Category": cat
            })
            save_data()
            st.rerun()

    with c2:
        st.subheader(f"Current Bill: {selected_tab}")
        current_order = st.session_state.tables[selected_tab]
        if current_order:
            total = sum(d['Price'] for d in current_order)
            for idx, entry in enumerate(current_order):
                col_item, col_btn = st.columns([3, 1])
                col_item.write(f"• {entry['Item']} (₹{entry['Price']})")
                with col_btn.popover("🗑️"):
                    if st.button("Confirm Cancel", key=f"conf_{entry['id']}"):
                        st.session_state.tables[selected_tab].pop(idx)
                        save_data()
                        st.rerun()
            
            st.write(f"### Total: ₹{total}")
            cust_phone = st.text_input("WhatsApp Number", placeholder="9876543210")
            pay_mode = st.selectbox("Payment Mode", ["Cash", "Online", "UPI"])
            
            if st.button("✅ Settle & Send Bill"):
                for order_item in current_order:
                    if order_item['Category'] == "Pizza": st.session_state.inventory["Pizza Bun"]["sold"] += 1
                    elif order_item['Category'] == "Burger": st.session_state.inventory["Burger Bun"]["sold"] += 1

                st.session_state.sales.append({"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Table": selected_tab, "Total": total, "Mode": pay_mode, "Status": "Success"})
                
                if cust_phone and len(cust_phone) == 10:
                    bill_msg = f"*--- THE TRADER'S CAFE ---*\nTotal: ₹{total}\nPayment: {pay_mode}\nFollow: {CAFE_INSTA}"
                    wa_url = f"https://wa.me/91{cust_phone}?text={urllib.parse.quote(bill_msg)}"
                    st.markdown(f"### [📲 Send Bill]({wa_url})")

                st.session_state.tables[selected_tab] = []
                save_data()
                st.success("Sale Recorded & Saved!")

# --- 5. SALES REPORT ---
elif choice == "Sales Report":
    st.header("📊 Sales & Daily Reports")
    
    # --- EXCEL DOWNLOAD LOGIC ---
    if st.session_state.sales or st.session_state.daily_archive:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            if st.session_state.sales:
                pd.DataFrame(st.session_state.sales).to_excel(writer, sheet_name='Sales_Live', index=False)
            if st.session_state.daily_archive:
                pd.DataFrame(st.session_state.daily_archive).to_excel(writer, sheet_name='Daily_Archive', index=False)
            
            # Inventory Sheet
            inv_data = [{"Item": k, **v, "Remained": v['added']-v['sold']} for k, v in st.session_state.inventory.items()]
            pd.DataFrame(inv_data).to_excel(writer, sheet_name='Inventory_Status', index=False)
        
        st.download_button(
            label="📥 Download All Data as Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"Trader_Cafe_Report_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
            mime="application/vnd.ms-excel"
        )
        st.divider()

    tab1, tab2 = st.tabs(["Today's Live Sales", "📜 Archived Daily Reports"])
    
    with tab1:
        if st.session_state.sales:
            st.dataframe(pd.DataFrame(st.session_state.sales))
        else: st.info("No sales recorded yet.")

    with tab2:
        if st.sidebar.button("📦 Archive Today's Report"):
             today_date = datetime.now().strftime("%Y-%m-%d")
             success_sales = [s for s in st.session_state.sales if s['Status'] == 'Success']
             report_entry = {"Date": today_date, "Total Revenue": sum(s['Total'] for s in success_sales), "Orders": len(success_sales)}
             st.session_state.daily_archive.append(report_entry)
             save_data()
             st.success("Daily Report Archived!")
        
        if st.session_state.daily_archive:
            st.table(pd.DataFrame(st.session_state.daily_archive))

# --- 6. INVENTORY ---
elif choice == "Inventory":
    st.header("📦 Inventory Management")
    inv_item = st.selectbox("Select Bun Type", ["Pizza Bun", "Burger Bun"])
    add_qty = st.number_input(f"Add Quantity", min_value=0, step=1)
    if st.button("➕ Add Stock"):
        st.session_state.inventory[inv_item]["added"] += add_qty
        save_data()
        st.success("Stock updated and saved!")
    
    inv_data = []
    for item, stats in st.session_state.inventory.items():
        inv_data.append({"Item": item, "Added": stats["added"], "Sold": stats["sold"], "Remained": stats["added"] - stats["sold"]})
    st.table(pd.DataFrame(inv_data))

# --- 7. SETTINGS & MENU ---
elif choice == "Settings":
    if st.button("Add Table"):
        new_t = f"Table {len(st.session_state.tables) + 1}"
        st.session_state.tables[new_t] = []
        save_data()
        st.rerun()

elif choice == "Manage Menu Items":
    for cat, items in st.session_state.menu.copy().items():
        with st.expander(cat):
            for old_n, pr in items.items():
                old_p = st.session_state.menu[cat][old_n]
                new_p = st.number_input(f"Price: {old_n}", value=pr, key=f"p_{old_n}")
                if new_p != old_p:
                    st.session_state.menu[cat][old_n] = new_p
                    save_data()
