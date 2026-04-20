import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os
from streamlit_geolocation import streamlit_geolocation

# -----------------------------------------------------------------------------
# 1. Configuration & Mock Database
# -----------------------------------------------------------------------------
DB_FILE = "employee_attendance.csv"
LOCAL_TZ = pytz.timezone("Asia/Jerusalem")

# Mock User Database (In a real app, use a real database and hash passwords!)
USERS = {
    "employee1": {"name": "John Doe", "password": "123", "role": "employee"},
    "employee2": {"name": "Jane Smith", "password": "123", "role": "employee"},
    "admin": {"name": "Boss", "password": "admin", "role": "admin"}
}

# Create CSV if it doesn't exist
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["Employee_Name", "Action", "Timestamp", "Latitude", "Longitude"])
    df.to_csv(DB_FILE, index=False)

# -----------------------------------------------------------------------------
# 2. Session State Initialization
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "name" not in st.session_state:
    st.session_state.name = ""

# -----------------------------------------------------------------------------
# 3. App Pages (Login, Employee, Admin)
# -----------------------------------------------------------------------------

def login_page():
    st.title("🔐 Login")
    st.write("Please log in to continue.")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Log In", type="primary"):
        if username in USERS and USERS[username]["password"] == password:
            # Set session state variables
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = USERS[username]["role"]
            st.session_state.name = USERS[username]["name"]
            
            st.success("Logged in successfully!")
            st.rerun()  # Refresh the page to load the correct view
        else:
            st.error("❌ Invalid Username or Password")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.name = ""
    st.rerun()

def employee_page():
    st.title(f"👋 Welcome, {st.session_state.name}")
    st.write("📍 **Log your working hours and current location.**")
    
    st.write("**Step 1: Click below to fetch your GPS location.**")
    location = streamlit_geolocation()

    # Verify that the GPS location has been successfully fetched
    if location and location.get('latitude'):
        lat = location['latitude']
        lon = location['longitude']
        
        st.success("✅ Location acquired successfully!")
        st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
        
        st.write("**Step 2: Record your attendance.**")
        col1, col2 = st.columns(2)
        
        # 🟢 Clock In
        with col1:
            if st.button("🟢 Clock In", use_container_width=True):
                current_time = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")
                new_entry = pd.DataFrame([{
                    "Employee_Name": st.session_state.name,
                    "Action": "Clock In",
                    "Timestamp": current_time,
                    "Latitude": lat,
                    "Longitude": lon
                }])
                new_entry.to_csv(DB_FILE, mode='a', header=False, index=False)
                st.success(f"Clocked IN at {current_time}")
                
        # 🔴 Clock Out
        with col2:
            if st.button("🔴 Clock Out", use_container_width=True):
                current_time = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")
                new_entry = pd.DataFrame([{
                    "Employee_Name": st.session_state.name,
                    "Action": "Clock Out",
                    "Timestamp": current_time,
                    "Latitude": lat,
                    "Longitude": lon
                }])
                new_entry.to_csv(DB_FILE, mode='a', header=False, index=False)
                st.success(f"Clocked OUT at {current_time}")
    else:
        st.warning("⚠️ Please allow location permissions in your browser and click the 'Get Location' button.")

def admin_page():
    st.title("🛡️ Admin Dashboard")
    st.write(f"Welcome to the management panel, {st.session_state.name}.")
    
    st.subheader("Employee Attendance Logs")
    if os.path.exists(DB_FILE):
        logs = pd.read_csv(DB_FILE)
        if not logs.empty:
            # Display logs sorted by newest first
            st.dataframe(logs.sort_values(by="Timestamp", ascending=False), use_container_width=True)
            
            # Create a download button for the CSV
            csv = logs.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv,
                file_name='employee_attendance_logs.csv',
                mime='text/csv',
            )
        else:
            st.info("No records found yet.")

# -----------------------------------------------------------------------------
# 4. Main App Routing
# -----------------------------------------------------------------------------

# If user is NOT logged in, show the login page
if not st.session_state.logged_in:
    login_page()

# If user IS logged in, route them based on their role
else:
    # Setup Sidebar for Logout
    with st.sidebar:
        st.write(f"Logged in as: **{st.session_state.name}**")
        st.write(f"Role: **{st.session_state.role.capitalize()}**")
        if st.button("Log Out"):
            logout()
            
    # Route to correct page based on role
    if st.session_state.role == "employee":
        employee_page()
    elif st.session_state.role == "admin":
        admin_page()