import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# --- 1. INITIALIZATION ---
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Pizza": {"Golden Corn": 59, "Testy Tomato": 49, "Shiney Onion": 49, "Choppy Capcicum": 49, "Spicy Shezwan": 79, "Mighty Paneer pizza": 79, "Mixed Veges Spicy": 69},
        "Burger": {"Classic Burger": 39, "Cheese burger": 55, "Spicy salsa": 59, "Royal paneer Grill burger": 69},
        "Sandwich": {"Grill Sandwich": 39, "Vegs Cheese Sandwich": 49, "Schezwan Sandwich": 49, "Choklet sandwich": 59},
        "Combo Offer": {
            "Forex Combo": 299, "Nifty Special": 239, "Back Benchers": 249, 
            "Student Special": 189, "Hunger Killer": 169, "Cafe Special 59": 59
        }
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
st.sidebar.header("The Trader's Cafe")
choice = st.sidebar.radio("Menu", ["Dashboard", "Sales Report", "Manage Menu", "Settings"])
if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()

# --- 4. DASHBOARD (BILLING & WHATSAPP) ---
if choice == "Dashboard":
    st.header("📊 Billing Dashboard")
    selected_tab = st.selectbox("Select Table", list(st.session_state.tables.keys()))
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.subheader("Add Items")
        cat = st.selectbox("Category", list(st.session_state.menu.keys()))
        item = st.selectbox("Item", list(st.session_state.menu[cat].keys()))
        qty = st.number_input("Qty", min_value=1, value=1)
        if st.button("Add to Bill"):
            price = st.session_state.menu[cat][item]
            st.session_state.tables[selected_tab].append({"Item": item, "Price": price, "Qty": qty, "Subtotal": price * qty})
            st.rerun()

    with col2:
        st.subheader(f"Receipt: {selected_tab}")
        if st.session_state.tables[selected_tab]:
            df_current = pd.DataFrame(st.session_state.tables[selected_tab])
            st.table(df_current[['Item', 'Qty', 'Subtotal']])
            total = df_current['Subtotal'].sum()
            st.write(f"### Total Amount: ₹{total}")
            
            cust_num = st.text_input("Customer WhatsApp (e.g. 919876543210)")
            pay_mode = st.selectbox("Payment Mode", ["Cash", "Online"])
            
            if st.button("Generate & Send Bill"):
                # Prepare Bill Text for WhatsApp
                bill_details = ""
                for index, row in df_current.iterrows():
                    bill_details += f"• {row['Item']} (x{row['Qty']}) - ₹{row['Subtotal']}\n"
                
                insta_link = "https://www.instagram.com/the_trader_cafe?igsh=bHVzcm1pbWY4MXlq"
                
                full_msg = (
                    f"✨ *The Trader's Cafe* ✨\n"
                    f"---------------------------\n"
                    f"Table: {selected_tab}\n"
                    f"Date: {datetime.now().strftime('%d-%m-%Y')}\n\n"
                    f"*Order Details:*\n{bill_details}\n"
                    f"---------------------------\n"
                    f"*Grand Total: ₹{total}*\n"
                    f"Payment: {pay_mode}\n\n"
                    f"Follow us for updates:\n{insta_link}\n"
                    f"Thank you! Visit again. 🙏"
                )
                
                # Encoding message for URL
                encoded_msg = urllib.parse.quote(full_msg)
                wa_url = f"https://wa.me/{cust_num}?text={encoded_msg}" if cust_num else f"https://wa.me/?text={encoded_msg}"
                
                # Save to Sales
                st.session_state.sales.append({"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Table": selected_tab, "Total": total, "Status": "Success", "Mode": pay_mode})
                
                st.markdown(f'### [📲 Click Here to Send Bill on WhatsApp]({wa_url})', unsafe_markdown=True)
                st.session_state.tables[selected_tab] = []

            # Cancel Order
            with st.expander("Cancel Order"):
                reason = st.text_input("Reason for Cancellation")
                if st.button("Confirm Cancel"):
                    if reason:
                        st.session_state.sales.append({"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Table": selected_tab, "Total": total, "Status": "Cancelled", "Mode": "N/A", "Reason": reason})
                        st.session_state.tables[selected_tab] = []
                        st.rerun()
                    else: st.error("Reason likhna zaroori hai!")

# --- 5. MANAGE MENU (NAME & RATE EDIT) ---
elif choice == "Manage Menu":
    st.header("📝 Edit Item Names & Rates")
    for category, items in st.session_state.menu.copy().items():
        with st.expander(f"Category: {category}"):
            for old_name, price in list(items.items()):
                c1, c2 = st.columns(2)
                new_n = c1.text_input("Name", value=old_name, key=f"n_{old_name}_{category}")
                new_p = c2.number_input("Rate", value=int(price), key=f"p_{old_name}_{category}")
                
                if new_n != old_name or new_p != price:
                    st.session_state.menu[category][new_n] = st.session_state.menu[category].pop(old_name)
                    st.session_state.menu[category][new_n] = new_p
                    st.rerun()

# --- 6. SETTINGS (NEW ITEM ADD) ---
elif choice == "Settings":
    st.header("⚙️ Cafe Settings")
    
    with st.container(border=True):
        st.subheader("🚀 Launch New Item")
        new_cat = st.selectbox("Select Category", list(st.session_state.menu.keys()))
        new_item_name = st.text_input("New Item Name")
        new_item_price = st.number_input("Set Price", min_value=0)
        if st.button("Add to Menu Now"):
            if new_item_name:
                st.session_state.menu[new_cat][new_item_name] = new_item_price
                st.success(f"{new_item_name} launched successfully in {new_cat}!")
            else: st.error("Naam toh likho!")

    st.divider()
    if st.button("Add 1 New Table"):
        new_id = len(st.session_state.tables) + 1
        st.session_state.tables[f"Table {new_id}"] = []
        st.success(f"Table {new_id} Active!")
