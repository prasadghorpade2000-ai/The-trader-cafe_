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
        if st.button("➕ Add to Bill"):
            price = st.session_state.menu[cat][item]
            st.session_state.tables[selected_tab].append({
                "id": datetime.now().timestamp(), 
                "Item": item, 
                "Price": price
            })
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
                    item_reason = st.text_input("Why cancel?", key=f"re_{entry['id']}", placeholder="e.g. Mistake")
                    if st.button("Confirm Cancel", key=f"conf_{entry['id']}"):
                        st.session_state.sales.append({
                            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Table": selected_tab, "Total": entry['Price'], 
                            "Item": entry['Item'], "Status": "Item Cancelled", 
                            "Reason": item_reason if item_reason else "No reason provided"
                        })
                        st.session_state.tables[selected_tab].pop(idx)
                        st.rerun()
            
            st.write(f"### Total: ₹{total}")
            st.divider()
            
            # --- WHATSAPP BILLING SECTION ---
            st.subheader("Send WhatsApp Bill")
            cust_phone = st.text_input("WhatsApp Number (10 Digits)", placeholder="9876543210")
            pay_mode = st.selectbox("Payment Mode", ["Cash", "Online", "UPI"])
            
            if st.button("✅ Settle & Generate WhatsApp Bill"):
                # Format the Text Message
                items_list = "\n".join([f"• {d['Item']}: ₹{d['Price']}" for d in current_order])
                bill_msg = (
                    f"*--- THE TRADER'S CAFE ---*\n"
                    f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n"
                    f"Table: {selected_tab}\n"
                    f"---------------------------\n"
                    f"{items_list}\n"
                    f"---------------------------\n"
                    f"*TOTAL BILL: ₹{total}*\n"
                    f"Payment: {pay_mode}\n\n"
                    f"Thank you! Visit again. 🙏"
                )

                # Save Sale
                st.session_state.sales.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Table": selected_tab, "Total": total, "Mode": pay_mode, "Status": "Success", "Reason": "N/A"
                })
                
                # WhatsApp URL (Hardcoded +91 for India)
                if cust_phone and len(cust_phone) == 10:
                    encoded_msg = urllib.parse.quote(bill_msg)
                    wa_url = f"https://wa.me/91{cust_phone}?text={encoded_msg}"
                    st.success("Sale Recorded!")
                    st.markdown(f"### [📲 Click to Send WhatsApp Bill]({wa_url})")
                else:
                    st.warning("Sale saved, but WhatsApp number was missing/invalid.")

                # Clear Table
                st.session_state.tables[selected_tab] = []

            # --- FULL ORDER CANCEL ---
            st.divider()
            with st.expander("🚫 Cancel Full Order"):
                full_reason = st.selectbox("Reason for Full Cancellation", 
                                          ["Customer changed mind", "Order delayed", "Kitchen busy", "Wrong Table", "Other"])
                other_text = st.text_input("If other, please specify:")
                
                if st.button("⚠️ Confirm Full Cancel"):
                    final_reason = other_text if full_reason == "Other" else full_reason
                    st.session_state.sales.append({
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                        "Table": selected_tab, "Total": total, "Status": "Full Cancelled", 
                        "Reason": final_reason
                    })
                    st.session_state.tables[selected_tab] = []
                    st.rerun()

# --- 5. SALES REPORT ---
elif choice == "Sales Report":
    st.header("📊 Sales & Cancellation Report")
    if st.session_state.sales:
        df = pd.DataFrame(st.session_state.sales)
        t1, t2 = st.tabs(["💰 Successful Sales", "❌ Cancellation Logs"])
        
        with t1:
            success_df = df[df['Status'] == 'Success']
            if not success_df.empty:
                st.dataframe(success_df[["Date", "Table", "Total", "Mode"]])
                st.metric("Total Collection", f"₹{success_df['Total'].sum()}")
            else: st.info("No successful sales yet.")

        with t2:
            cancel_df = df[df['Status'].str.contains("Cancelled")]
            if not cancel_df.empty:
                st.table(cancel_df[["Date", "Table", "Status", "Reason", "Total"]])
                st.error(f"Total Revenue Lost: ₹{cancel_df['Total'].sum()}")
            else: st.success("Great! No cancellations today.")
    else: st.info("No data available.")

# --- 6. SETTINGS ---
elif choice == "Settings":
    st.header("⚙️ Settings")
    if st.button("Add 1 New Table"):
        new_t = f"Table {len(st.session_state.tables) + 1}"
        st.session_state.tables[new_t] = []
        st.rerun()

elif choice == "Manage Menu Items":
    st.header("📝 Menu Management")
    for cat, items in st.session_state.menu.copy().items():
        with st.expander(cat):
            for old_n, pr in items.items():
                new_p = st.number_input(f"Price: {old_n}", value=pr, key=f"p_{old_n}")
                if new_p != pr:
                    st.session_state.menu[cat][old_n] = new_p
                    st.rerun()
