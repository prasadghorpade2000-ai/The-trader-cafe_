import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. SESSION STATE (Database) ---
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Pizza": {"Golden Corn": 59, "Testy Tomato": 49, "Shiney Onion": 49, "Choppy Capcicum": 49, "Spicy Shezwan": 79, "Mighty Paneer pizza": 79, "Mixed Veges Spicy": 69},
        "Burger": {"Classic Burger": 39, "Cheese burger": 55, "Spicy salsa": 59, "Royal paneer Grill burger": 69},
        "Sandwich": {"Grill Sandwich": 39, "Vegs Cheese Sandwich": 49, "Schezwan Sandwich": 49, "Choklet sandwich": 59},
        "Combos": {"Forex Combo": 299, "Nifty Special": 239, "Back Benchers": 249, "Student Special": 189, "Hunger Killer": 169}
    }

if 'sales' not in st.session_state: st.session_state.sales = []
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
choice = st.sidebar.radio("Go to", ["Dashboard", "Sales Report", "Manage Menu Items", "Settings"])
if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()

# --- 4. DASHBOARD (BILLING & WHATSAPP) ---
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
            df_current = pd.DataFrame(st.session_state.tables[selected_tab])
            st.table(df_current)
            total = df_current['Price'].sum()
            st.write(f"### Total: ₹{total}")
            
            # --- CUSTOMER WHATSAPP FEATURE ---
            cust_mobile = st.text_input("Customer Mobile (with 91)", placeholder="9198XXXXXXXX")
            pay_mode = st.selectbox("Mode", ["Cash", "Online"])
            
            if st.button("Settle & Send WhatsApp"):
                st.session_state.sales.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Table": selected_tab, "Total": total, "Mode": pay_mode, "Status": "Success", "Reason": "-"
                })
                # WhatsApp link with mobile number
                insta = "https://www.instagram.com/the_trader_cafe?igsh=bHVzcm1pbWY4MXlq"
                wa_msg = f"Trader's Cafe Bill: ₹{total}. Payment: {pay_mode}. Follow us: {insta}"
                
                # Agar number nahi hai toh general link, warna direct chat link
                link = f"https://wa.me/{cust_mobile}?text={wa_msg}" if cust_mobile else f"https://wa.me/?text={wa_msg}"
                st.markdown(f"[📲 Open WhatsApp to Send Bill]({link})")
                st.session_state.tables[selected_tab] = []

            # --- CANCEL ORDER WITH REASON ---
            st.divider()
            cancel_reason = st.text_area("Reason for Cancellation")
            if st.button("Cancel Order"):
                if cancel_reason:
                    st.session_state.sales.append({
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Table": selected_tab, "Total": total, "Mode": "N/A", "Status": "Cancelled", "Reason": cancel_reason
                    })
                    st.session_state.tables[selected_tab] = []
                    st.warning("Order Cancelled and Recorded.")
                    st.rerun()
                else:
                    st.error("Please enter a reason to cancel!")

# --- 5. SALES REPORT ---
elif choice == "Sales Report":
    st.header("📊 Sales & Cancellation Report")
    if st.session_state.sales:
        df_sales = pd.DataFrame(st.session_state.sales)
        st.dataframe(df_sales)
        st.metric("Total Revenue", f"₹{df_sales[df_sales['Status']=='Success']['Total'].sum()}")
    else: st.info("No records yet.")

# --- 6. MANAGE MENU (EDIT NAME & RATE) ---
elif choice == "Manage Menu Items":
    st.header("📝 Edit Item Names & Rates")
    for category, items in st.session_state.menu.copy().items():
        st.subheader(f"Category: {category}")
        for old_name, price in items.items():
            col_a, col_b = st.columns(2)
            with col_a:
                new_name = st.text_input(f"Name of {old_name}", value=old_name, key=f"name_{old_name}")
            with col_b:
                new_price = st.number_input(f"Rate of {old_name}", value=price, key=f"price_{old_name}")
            
            # Logic to update name and price
            if new_name != old_name or new_price != price:
                st.session_state.menu[category][new_name] = st.session_state.menu[category].pop(old_name)
                st.session_state.menu[category][new_name] = new_price
                st.rerun()
