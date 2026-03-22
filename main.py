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
choice = st.sidebar.radio("Go to", ["Dashboard", "Daily Sales Report", "Manage Menu Items", "Settings"])
if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()

# --- 4. DASHBOARD (ITEM-WISE CANCELLATION) ---
if choice == "Dashboard":
    st.header("📍 Table Management")
    selected_tab = st.selectbox("Select Table", list(st.session_state.tables.keys()))
    
    c1, c2 = st.columns(2)
    with c1:
        cat = st.selectbox("Category", list(st.session_state.menu.keys()))
        item = st.selectbox("Item", list(st.session_state.menu[cat].keys()))
        if st.button("➕ Add to Bill"):
            price = st.session_state.menu[cat][item]
            # Unique ID for each item to allow specific deletion
            st.session_state.tables[selected_tab].append({"id": datetime.now().timestamp(), "Item": item, "Price": price})
            st.rerun()

    with c2:
        st.subheader(f"Current Bill: {selected_tab}")
        items_in_table = st.session_state.tables[selected_tab]
        
        if items_in_table:
            total = 0
            for idx, entry in enumerate(items_in_table):
                col_item, col_btn = st.columns()
                col_item.write(f"{entry['Item']} - ₹{entry['Price']}")
                if col_btn.button("❌", key=f"del_{entry['id']}"):
                    # Record the item cancellation in sales report
                    st.session_state.sales.append({
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Table": selected_tab, "Total": entry['Price'], "Status": "Item Cancelled", "Item": entry['Item']
                    })
                    st.session_state.tables[selected_tab].pop(idx)
                    st.rerun()
                total += entry['Price']
            
            st.write(f"### Total: ₹{total}")
            
            st.divider()
            cust_phone = st.text_input("WhatsApp Number", placeholder="9876543210")
            pay_mode = st.selectbox("Payment Mode", ["Cash", "Online", "UPI"])
            
            # Format Bill with Insta Link
            items_text = "\n".join([f"• {d['Item']}: ₹{d['Price']}" for d in items_in_table])
            insta_url = "https://www.instagram.com/the_trader_cafe?igsh=bHVzcm1pbWY4MXlq"
            bill_msg = f"*--- THE TRADER'S CAFE ---*\n\n*Order Details:*\n{items_text}\n\n*TOTAL: ₹{total}*\nPayment: {pay_mode}\n\nFollow us on Instagram: {insta_url}\n\nThank you! 🙏"
            
            if st.button("✅ Settle & WhatsApp Bill"):
                st.session_state.sales.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Table": selected_tab, 
                    "Total": total, "Mode": pay_mode, "Status": "Success"
                })
                if cust_phone:
                    encoded_msg = urllib.parse.quote(bill_msg)
                    st.markdown(f"[📲 Click to Send WhatsApp Bill](https://wa.me/91{cust_phone}?text={encoded_msg})")
                st.success("Sale Recorded!")

            if st.button("🧹 Clear Table"):
                st.session_state.tables[selected_tab] = []
                st.rerun()

# --- 5. DAILY SALES REPORT ---
elif choice == "Daily Sales Report":
    st.header("📊 Daily Sales Report")
    today = datetime.now().strftime("%Y-%m-%d")
    
    if st.session_state.sales:
        df = pd.DataFrame(st.session_state.sales)
        # Filter for today only
        df_today = df[df['Date'].str.contains(today)]
        
        st.write(f"### Sales for {today}")
        st.dataframe(df_today)
        
        success_total = df_today[df_today['Status'] == 'Success']['Total'].sum()
        st.metric("Total Success Sale (Today)", f"₹{success_total}")
    else: st.info("No sales recorded yet.")

# --- 6. SETTINGS (ADD/DELETE TABLE & CATEGORY) ---
elif choice == "Settings":
    st.header("⚙️ Cafe Configuration")
    
    # Category Management
    st.subheader("Manage Categories")
    new_cat = st.text_input("New Category Name")
    if st.button("Add Category"):
        if new_cat and new_cat not in st.session_state.menu:
            st.session_state.menu[new_cat] = {}
            st.rerun()
            
    cat_to_del = st.selectbox("Delete Category", ["Select"] + list(st.session_state.menu.keys()))
    if st.button("🗑️ Delete Category"):
        if cat_to_del != "Select":
            del st.session_state.menu[cat_to_del]
            st.rerun()

    st.divider()
    # Table Management
    st.subheader("Manage Tables")
    if st.button("➕ Add 1 More Table"):
        new_id = f"Table {len(st.session_state.tables) + 1}"
        st.session_state.tables[new_id] = []
        st.rerun()
        
    table_to_del = st.selectbox("Delete Table", ["Select"] + list(st.session_state.tables.keys()))
    if st.button("🗑️ Delete Selected Table"):
        if table_to_del != "Select":
            del st.session_state.tables[table_to_del]
            st.rerun()

# --- 7. MANAGE MENU ---
elif choice == "Manage Menu Items":
    st.header("📝 Menu Management")
    with st.expander("🚀 Launch New Item"):
        l_cat = st.selectbox("Category", list(st.session_state.menu.keys()))
        l_name = st.text_input("Item Name")
        l_price = st.number_input("Price", min_value=0)
        if st.button("Add Item"):
            st.session_state.menu[l_cat][l_name] = l_price
            st.rerun()
