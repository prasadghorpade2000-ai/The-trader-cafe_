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
        else: st.error("Wrong Password!")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title("Trader's Cafe Panel")
choice = st.sidebar.radio("Go to", ["Dashboard", "Sales Report", "Manage Menu Items", "Settings"])
if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()

# --- 4. DASHBOARD (BILLING, WHATSAPP & INSTAGRAM) ---
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
            
            st.divider()
            st.subheader("Send Digital Bill")
            
            # Input Fields
            cust_phone = st.text_input("WhatsApp Number (10 Digits)", placeholder="9876543210")
            insta_user = st.text_input("Customer Insta Username", placeholder="username_here")
            pay_mode = st.selectbox("Payment Mode", ["Cash", "Online", "UPI"])
            
            # Format the Bill Text
            items_text = "\n".join([f"• {d['Item']}: ₹{d['Price']}" for d in st.session_state.tables[selected_tab]])
            bill_msg = f"*--- THE TRADER'S CAFE ---*\n\n*Order Details:*\n{items_text}\n\n*TOTAL AMOUNT: ₹{total}*\nPayment Method: {pay_mode}\n\nThank you! Visit again. 🙏"
            
            if st.button("✅ Settle & Generate Links"):
                # 1. WHATSAPP LOGIC
                if cust_phone and len(cust_phone) == 10:
                    encoded_msg = urllib.parse.quote(bill_msg)
                    wa_url = f"https://wa.me/91{cust_phone}?text={encoded_msg}"
                    st.success("WhatsApp Link Ready!")
                    st.markdown(f"[📲 Send Bill via WhatsApp]({wa_url})")
                else:
                    st.error("Please enter a valid 10-digit mobile number.")

                # 2. INSTAGRAM LOGIC
                st.info("Instagram par message manually paste karein:")
                st.code(bill_msg) # Easy to copy
                if insta_user:
                    insta_url = f"https://www.instagram.com/direct/t/{insta_user}/"
                    st.markdown(f"[📸 Open Instagram DM]({insta_url})")

                # Save to Sales Record
                st.session_state.sales.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                    "Table": selected_tab, 
                    "Total": total, 
                    "Mode": pay_mode, 
                    "Status": "Success"
                })
                # Clear Table
                # st.session_state.tables[selected_tab] = [] 
                # Note: I commented the clear line so you can click links before it vanishes. 
                # Add a "Clear Table" button separately if preferred.

            if st.button("🧹 Clear Table"):
                st.session_state.tables[selected_tab] = []
                st.rerun()


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
