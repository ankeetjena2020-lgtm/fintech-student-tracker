import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import hashlib
from datetime import datetime
import database as db

# Database initialize
db.init_db()

st.set_page_config(page_title="Student FinTech Tracker", page_icon="📈", layout="wide")

def trigger_refresh():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def fetch_live_price(ticker_symbol):
    try:
        ticker_data = yf.Ticker(ticker_symbol)
        hist = ticker_data.history(period="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
        info = ticker_data.fast_info
        if info and 'last_price' in info:
            return float(info['last_price'])
        return None
    except Exception:
        return None

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "username" not in st.session_state:
    st.session_state["username"] = ""

# ================= AUTHENTICATION GATE =================
if not st.session_state["logged_in"]:
    st.title("🔒 Student FinTech Portal Secure Access")
    st.markdown("---")
    auth_mode = st.radio("Choose Action", ["Login to Account", "Create New Account"], horizontal=True)
    
    with st.form("auth_form"):
        username_input = st.text_input("Username / Roll No").strip()
        password_input = st.text_input("Security PIN / Password", type="password")
        submit_auth = st.form_submit_button("Proceed")
        
        if submit_auth and username_input and password_input:
            hashed_p = hash_password(password_input)
            if auth_mode == "Create New Account":
                if db.register_user(username_input, hashed_p):
                    st.success("Account created! Please switch to Login mode.")
                else:
                    st.error("Username already taken!")
            elif auth_mode == "Login to Account":
                uid = db.login_user(username_input, hashed_p)
                if uid:
                    st.session_state["logged_in"] = True
                    st.session_state["user_id"] = uid
                    st.session_state["username"] = username_input
                    trigger_refresh()
                else:
                    st.error("Invalid credentials!")
    st.stop()

# ================= DASHBOARD APP =================
st.sidebar.markdown(f"### 👤 User: **{st.session_state['username']}**")
if st.sidebar.button("Logout 🏃"):
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = ""
    trigger_refresh()

st.title("📈 Student FinTech Dashboard & Analytics")
st.markdown("---")

menu = ["Dashboard (Analytics)", "Manage Savings Goals", "Track Expenses", "📈 Live Stock Portfolio", "👥 P2P Bill Splitter"]
choice = st.sidebar.selectbox("Navigation", menu)
current_uid = st.session_state["user_id"]

# --- DASHBOARD ---
if choice == "Dashboard (Analytics)":
    st.subheader("📊 Financial Insights & Data Visualizations")
    goals = db.get_goals(current_uid)
    expenses = db.get_expenses(current_uid)
    
    df_goals = pd.DataFrame(goals, columns=["ID", "Goal Name", "Target (₹)", "Date", "Saved (₹)"]) if goals else pd.DataFrame()
    df_exp = pd.DataFrame(expenses, columns=["ID", "Category", "Amount (₹)", "Date"]) if expenses else pd.DataFrame()
    
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Total Expenses Logged", f"₹{df_exp['Amount (₹)'].sum() if not df_exp.empty else 0:,.2f}")
    with m2: st.metric("Total Money Saved in Goals", f"₹{df_goals['Saved (₹)'].sum() if not df_goals.empty else 0:,.2f}")
    with m3: st.metric("Active Savings Goals", f"{len(df_goals)} Targets")
        
    st.markdown("---")
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        if not df_exp.empty:
            fig_pie = px.pie(df_exp.groupby("Category")["Amount (₹)"].sum().reset_index(), values="Amount (₹)", names="Category", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pie, use_container_width=True)
        else: st.info("No expense data available.")
    with col_chart2:
        if not df_goals.empty:
            df_melted = df_goals.melt(id_vars=["Goal Name"], value_vars=["Target (₹)", "Saved (₹)"], var_name="Type", value_name="Amount (₹)")
            fig_bar = px.bar(df_melted, x="Goal Name", y="Amount (₹)", color="Type", barmode="group")
            st.plotly_chart(fig_bar, use_container_width=True)
        else: st.info("No goals setup yet.")

# --- MANAGE SAVINGS GOALS ---
elif choice == "Manage Savings Goals":
    st.subheader("🎯 Savings Goals Management")
    with st.expander("➕ Add New Goal"):
        with st.form("new_goal_form"):
            g_name = st.text_input("Goal Name")
            g_target = st.number_input("Target Amount (₹)", min_value=100.0)
            g_date = st.date_input("Target Date")
            if st.form_submit_button("Create Goal") and g_name:
                db.add_goal(current_uid, g_name, g_target, str(g_date))
                trigger_refresh()
    
    goals = db.get_goals(current_uid)
    for goal in goals:
        g_id, name, target, date_str, saved = goal
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"**🎯 {name}** (Target: ₹{target} | Date: {date_str})")
                st.progress(min(float(saved/target), 1.0) if target > 0 else 0.0)
            with c2:
                if st.button("✏️ Edit", key=f"edit_{g_id}"): st.session_state[f"active_edit_{g_id}"] = True
            with c3:
                if st.button("🗑️ Delete", key=f"del_{g_id}"):
                    db.delete_goal(g_id)
                    trigger_refresh()
            if st.session_state.get(f"active_edit_{g_id}", False):
                with st.form(f"f_edit_{g_id}"):
                    u_name = st.text_input("Edit Name", value=name)
                    u_target = st.number_input("Edit Target", value=float(target))
                    u_date = st.date_input("Edit Date", value=datetime.strptime(date_str, "%Y-%m-%d").date())
                    u_saved = st.number_input("Update Savings", value=float(saved))
                    if st.form_submit_button("Save"):
                        db.update_goal(g_id, u_name, u_target, str(u_date), u_saved)
                        st.session_state[f"active_edit_{g_id}"] = False
                        trigger_refresh()

# --- TRACK EXPENSES ---
elif choice == "Track Expenses":
    st.subheader("💸 Expense Management")
    col1, col2 = st.columns([2, 3])
    with col1:
        with st.form("exp_form"):
            cat = st.selectbox("Category", ["Food", "Travel", "Books/Stationery", "Subscribed Apps", "Others"])
            amt = st.number_input("Amount (₹)", min_value=1.0)
            d = st.date_input("Date")
            if st.form_submit_button("Log Entry"):
                db.add_expense(current_uid, cat, amt, str(d))
                trigger_refresh()
    with col2:
        expenses = db.get_expenses(current_uid)
        for exp in expenses:
            e_id, category, amount, date_str = exp
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1: st.write(f"**{category}**")
            with c2: st.write(f"₹{amount} ({date_str})")
            with c3:
                if st.button("🗑️", key=f"del_exp_{e_id}"):
                    db.delete_expense(e_id)
                    trigger_refresh()

# --- LIVE STOCK PORTFOLIO ---
elif choice == "📈 Live Stock Portfolio":
    st.subheader("📈 Mock Stock Portfolio Engine")
    col1, col2 = st.columns([2, 4])
    with col1:
        with st.form("stock_form"):
            ticker = st.text_input("Ticker Symbol (e.g. TCS.NS, AAPL)").strip()
            sh = st.number_input("Shares", min_value=0.01, value=1.0)
            pr = st.number_input("Buy Price (₹)", min_value=1.0)
            dt = st.date_input("Date")
            if st.form_submit_button("Add Asset") and ticker:
                if fetch_live_price(ticker) is not None:
                    db.add_investment(current_uid, ticker, str(sh), str(pr), str(dt))
                    trigger_refresh()
                else: st.error("Invalid Ticker!")
    with col2:
        investments = db.get_investments(current_uid)
        if investments:
            p_data = []
            for inv in investments:
                i_id, tck, q, bp, d = inv
                lp = fetch_live_price(tck) or float(bp)
                ic, cv = float(q)*float(bp), float(q)*lp
                p_data.append({"ID": i_id, "Asset": tck.upper(), "Qty": float(q), "Avg": float(bp), "Live": lp, "Cost": ic, "Value": cv, "PnL": cv-ic})
            df = pd.DataFrame(p_data)
            st.columns(3)[0].metric("Portfolio Value", f"₹{df['Value'].sum():,.2f}", delta=f"₹{df['PnL'].sum():,.2f}")
            for idx, r in df.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 4, 1])
                    c1.write(f"**{r['Asset']}** | Shares: {r['Qty']:.2f}")
                    c2.write(f"Cost: ₹{r['Cost']:,.2f} ➔ Value: ₹{r['Value']:,.2f} ({r['PnL']:+.2f})")
                    if c3.button("🗑️", key=f"del_inv_{r['ID']}"):
                        db.delete_investment(int(r['ID']))
                        trigger_refresh()

# ================= PHASE 7: P2P BILL SPLITTER INTERFACE =================
elif choice == "👥 P2P Bill Splitter":
    st.subheader("👥 Peer-to-Peer Bill Splitter (Roommate Utility)")
    
    col_add, col_calc = st.columns([2, 3])
    
    with col_add:
        st.markdown("### Log Group Expense")
        with st.form("bill_form"):
            desc = st.text_input("Description (e.g., Room Rent, Dinner Party)", placeholder="e.g., Dominoes Pizza")
            amount = st.number_input("Total Bill Amount (₹)", min_value=1.0, step=50.0)
            paid_by = st.text_input("Who paid this bill?", value=st.session_state["username"])
            friends_input = st.text_area("Friends involved (Comma separated names)", placeholder="Aman, Rahul, Vicky")
            b_date = st.date_input("Bill Date")
            
            if st.form_submit_button("Split & Save Bill"):
                if desc and friends_input:
                    # Formatting text properly
                    clean_friends = ", ".join([f.strip() for f in friends_input.split(",") if f.strip()])
                    db.add_bill(current_uid, desc, amount, paid_by.strip(), clean_friends, str(b_date))
                    st.success("Group expense logged successfully!")
                    trigger_refresh()
                else:
                    st.warning("Please fill description and add friends.")
                    
    with col_calc:
        st.markdown("### Balance Ledger (Who Owes Whom)")
        bills = db.get_bills(current_uid)
        
        if not bills:
            st.info("No group expenses recorded yet.")
        else:
            balances = {} # Core Matrix dictionary to map balances
            
            for b in bills:
                b_id, description, total, payer, friends_str, d_str = b
                all_members = [m.strip() for m in friends_str.split(",") if m.strip()]
                if payer not in all_members:
                    all_members.append(payer)
                
                num_people = len(all_members)
                share = total / num_people
                
                # Calculating net balances matrix
                for person in all_members:
                    if person not in balances:
                        balances[person] = 0.0
                    if person == payer:
                        balances[person] += (total - share)
                    else:
                        balances[person] -= share
            
            # Rendering P2P calculation updates
            st.markdown("#### Net Balances Summary")
            for person, balance in balances.items():
                if person == st.session_state["username"]:
                    if balance >= 0:
                        st.success(f"**You get back:** ₹{balance:,.2f} in total")
                    else:
                        st.error(f"**You owe:** ₹{abs(balance):,.2f} in total")
                else:
                    if balance >= 0:
                        st.markdown(f"🟢 **{person}** gets back ₹{balance:,.2f}")
                    else:
                        st.markdown(f"🔴 **{person}** owes ₹{abs(balance):,.2f}")
                        
            st.markdown("---")
            st.markdown("#### Bill History Logs")
            for b in bills:
                b_id, description, total, payer, friends_str, d_str = b
                with st.container(border=True):
                    c_txt, c_del = st.columns([5, 1])
                    c_txt.write(f"**{description}** | Total: ₹{total:,.2f} | Paid by: *{payer}* | Members: {friends_str}")
                    if c_del.button("🗑️", key=f"del_bill_{b_id}"):
                        db.delete_bill(b_id)
                        trigger_refresh()