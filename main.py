import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="The Trader's Cafe", layout="wide")

# --- DATABASE INITIALIZATION (Session State) ---
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Pizza": {"Golden Corn": 59, "Testy Tomato": 49, "Shiney Onion": 49, "Choppy Capcicum": 49, "Spicy Shezwan": 79, "Mighty Paneer pizza": 79, "Mixed Veges Spicy": 69},
        "Burger": {"Classic Burger": 39, "Cheese burger": 55, "Spicy salsa": 59, "Royal paneer Grill burger": 69},
        "Sandwich": {"Grill Sandwich": 39, "Vegs Cheese Sandwich": 49, "Schezwan Sandwich": 49, "Choklet sandwich": 59},
        "Special Offers": {
            "1 Classic Burger + 1 Cold Drink + Brownie": 59,
            "1 Pizza (Basic) + Cold Drink + Brownie": 89,
            "Premium: Corn Pizza + Cheese SW + Drink": 99,
            "Premium: Shezwan Pizza + Cheese Burger + Drink": 119,
            "Student Special: 2 Pizza + 1 Choc SW + Drink": 189,
            "Hunger Killer: 2 Cheese Burger + 1 Mix Veg Pizza": 169,
            "Back Benchers: 2CB + 2VP + 2SW + 3 Drink": 249
        },
        "Trader's Special": {
            "Forex Combo: 2 Paneer + 2 Salsa + 1 Choc SW": 299,
            "Nifty Special: 1 Paneer + 1 Shezwan + 1CB + 1SW": 239
        }
    }

if 'sales_data' not in st.session_state:
    st.session_state.sales_data = []
if 'tables' not in st.session_state:
    # Starting with 15 tables as requested
    st.session_state.tables = {f"Table {i}": [] for i in range(1, 16)}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN SYSTEM ---
if not st.session_state.logged_in:
    st.title("📈 The Trader's Cafe - Admin Login")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pw == "trader@2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong Username or Password")
    st.stop()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Trader's Cafe Panel")
page = st.sidebar.radio("Menu", ["📊 Dashboard (15 Tables)", "🧾 Sales Report", "🍔 Edit Menu/Rates", "⚙️ Settings"])
if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()

# --- PAGE 1: DASHBOARD (TABLE MANAGEMENT) ---
if page == "📊 Dashboard (15 Tables)":
    st.header("Live Table Management")
    cols = st.columns(3)
    
    for i, table_name in enumerate(st.session_state.tables.keys()):
        with cols[i % 3]:
            with st.expander(f"📍 {table_name}", expanded=False):
                current_order = st.session_state.tables[table_name]
                
                # Select Item to add
                cat = st.selectbox("Category", list(st.session_state.menu.keys()), key=f"cat_{table_name}")
                item = st.selectbox("Item", list(st.session_state.menu[cat].keys()), key=f"item_{table_name}")
                
                if st.button(f"Add Item to {table_name}", key=f"btn_{table_name}"):
                    price = st.session_state.menu[cat][item]
                    st.session_state.tables[table_name].append({"item": item, "price": price})
                    st.rerun()
                
                # Show items in table
                if current_order:
                    st.write("---")
                    df_temp = pd.DataFrame(current_order)
                    st.table(df_temp)
                    total = df_temp['price'].sum()
                    st.write(f"**Total: ₹{total}**")
                    
                    method = st.radio("Payment Mode", ["Cash", "Online"], key=f"pay_{table_name}")
                    
                    if st.button("Settle Bill & Notify", key=f"settle_{table_name}"):
                        # Save to report
                        st.session_state.sales_data.append({
                            "Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Table": table_name,
                            "Total": total,
                            "Mode": method,
                            "Status": "Success"
                        })
                        
                        # WhatsApp Link Generation
                        insta_link = "https://www.instagram.com/the_trader_cafe?igsh=bHVzcm1pbWY4MXlq"
                        msg = f"Thanks for visiting The Trader's Cafe! %0A*Total Bill: ₹{total}* %0APayment: {method} %0AFollow us for updates: {insta_link}"
                        st.success("Bill Settled!")
                        st.markdown(f"[Click here to send WhatsApp Bill](https://wa.me/?text={msg})")
                        
                        st.session_state.tables[table_name] = [] # Reset Table

                    if st.button("Cancel Order", key=f"cancel_{table_name}"):
                        st.session_state.sales_data.append({
                            "Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Table": table_name,
                            "Total": total,
                            "Mode": "N/A",
                            "Status": "Cancelled"
                        })
                        st.session_state.tables[table_name] = []
                        st.rerun()

# --- PAGE 2: SALES REPORT ---
elif page == "🧾 Sales Report":
    st.header("Daily & Monthly Sales Report")
    if st.session_state.sales_data:
        df = pd.DataFrame(st.session_state.sales_data)
        
        # Summary Cards
        success_df = df[df['Status'] == "Success"]
        cancelled_df = df[df['Status'] == "Cancelled"]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Sale", f"₹{success_df['Total'].sum()}")
        c2.metric("Orders", len(success_df))
        c3.metric("Cancelled", len(cancelled_df))
        
        st.write("### All Transactions")
        st.dataframe(df)
        
        # Simple Chart
        st.bar_chart(success_df.groupby("Mode")["Total"].sum())
    else:
        st.info("No sales yet for today.")

# --- PAGE 3: MENU MANAGEMENT ---
elif page == "🍔 Edit Menu/Rates":
    st.header("Manage Menu Items & Prices")
    
    # Add New Item
    with st.expander("➕ Add New Item"):
        new_cat = st.selectbox("Select Category", list(st.session_state.menu.keys()))
        new_item = st.text_input("Item Name")
        new_price = st.number_input("Price", min_value=0)
        if st.button("Save New Item"):
            st.session_state.menu[new_cat][new_item] = new_price
            st.success("Item Added!")

    # Edit Rates
    st.subheader("Edit Existing Rates")
    for category, items in st.session_state.menu.items():
        st.write(f"**{category}**")
        for item, price in items.items():
            new_p = st.number_input(f"Rate for {item}", value=price, key=f"rate_{item}")
            st.session_state.menu[category][item] = new_p

# --- PAGE 4: SETTINGS ---
elif page == "⚙️ Settings":
    st.header("Cafe Configuration")
    if st.button("Add New Table"):
        new_t_num = len(st.session_state.tables) + 1
        st.session_state.tables[f"Table {new_t_num}"] = []
        st.success(f"Table {new_t_num} added successfully!")
