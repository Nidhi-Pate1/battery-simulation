import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh  # pip install streamlit-autorefresh

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

if 'autoupdate' not in st.session_state:
    st.session_state.autoupdate = False

if 'max_history' not in st.session_state:
    st.session_state.max_history = 100

st.set_page_config(page_title="Battery Monitoring Dashboard", layout="wide")

# Header
st.markdown("""
    <h1 style='text-align: center; color: #00c6ff;'>🔋 Battery Monitoring Dashboard</h1>
    <p style='text-align: center; color: #4f4f4f;'>Track real-time metrics of your battery cells with interactive visuals and alerts</p>
    <hr style='border-top: 3px solid #00c6ff;'>
""", unsafe_allow_html=True)

# Sidebar for configuration
st.sidebar.markdown("## ⚙️ Configuration Panel")
num_cells = st.sidebar.slider("Select Number of Cells", min_value=1, max_value=20, value=8)

# Alert thresholds
temp_threshold = st.sidebar.number_input("🔥 Temperature Alert Threshold (°C)", min_value=0, max_value=100, value=40)
volt_threshold = st.sidebar.number_input("⚡ Voltage Alert Threshold (V)", min_value=0.0, max_value=5.0, value=3.5)

autoupdate = st.sidebar.checkbox("🔄 Enable Auto Refresh", value=st.session_state.autoupdate)
st.session_state.autoupdate = autoupdate

# Auto refresh using st_autorefresh
if autoupdate:
    count = st_autorefresh(interval=1000, limit=None, key="autorefresh")

# Input cells data with sensible defaults
voltages, currents, temperatures, capacities, modes = [], [], [], [], []
mode_options = ['Charging', 'Discharging', 'Idle']

for i in range(num_cells):
    st.sidebar.markdown(f"### 🔋 Cell {i+1} Input")
    voltages.append(st.sidebar.number_input(f"Voltage (V) - Cell {i+1}", value=3.7, step=0.01, key=f"voltage_{i}"))
    currents.append(st.sidebar.number_input(f"Current (A) - Cell {i+1}", value=0.0, step=0.01, key=f"current_{i}"))
    temperatures.append(st.sidebar.number_input(f"Temperature (°C) - Cell {i+1}", value=25.0, step=0.1, key=f"temp_{i}"))
    capacities.append(st.sidebar.number_input(f"Capacity (%) - Cell {i+1}", min_value=0, max_value=100, value=100, key=f"cap_{i}"))
    modes.append(st.sidebar.selectbox(f"Mode - Cell {i+1}", options=mode_options, index=2, key=f"mode_{i}"))  # Default Idle

if st.sidebar.button("🚀 Update Dashboard") or autoupdate:
    timestamp = datetime.now()
    st.session_state.history.append({
        'timestamp': timestamp,
        'voltages': voltages.copy(),
        'currents': currents.copy(),
        'temperatures': temperatures.copy(),
        'capacities': capacities.copy(),
        'modes': modes.copy()
    })
    # Keep only latest max_history records
    if len(st.session_state.history) > st.session_state.max_history:
        st.session_state.history = st.session_state.history[-st.session_state.max_history:]

# Alerts Section
alert_msgs = []
for i in range(num_cells):
    if temperatures[i] > temp_threshold:
        alert_msgs.append(f"🔥 Cell {i+1} Overheating! Temp: {temperatures[i]:.1f} °C")
    if voltages[i] < volt_threshold:
        alert_msgs.append(f"⚡ Low Voltage on Cell {i+1}: {voltages[i]:.2f} V")

if alert_msgs:
    st.warning("\n".join(alert_msgs))

# Display cell cards with selected mode and color
st.markdown("### 📊 Cell Status Overview")
cell_rows = [st.columns(4) for _ in range((num_cells + 3) // 4)]
mode_colors = {
    'Charging': '#28a745',      # Green
    'Discharging': '#dc3545',   # Red
    'Idle': '#6c757d'           # Gray
}

for i in range(num_cells):
    with cell_rows[i // 4][i % 4]:
        status_color = mode_colors.get(modes[i], '#6c757d')
        st.markdown(f"""
        <div style='border-radius: 15px; padding: 20px; background: linear-gradient(135deg, #d0f0fd, #ffffff); box-shadow: 0 4px 8px rgba(0,0,0,0.15); margin-bottom: 20px; transition: all 0.3s ease;'>
            <h4 style='color:#006fa6; text-align:center;'>🔋 Cell {i+1}</h4>
            <ul style='list-style:none; padding-left:0; font-size: 15px;'>
                <li>🔌 Voltage: <strong>{voltages[i]:.2f} V</strong></li>
                <li>⚡ Current: <strong>{currents[i]:.2f} A</strong></li>
                <li>🌡️ Temperature: <strong>{temperatures[i]:.1f} °C</strong></li>
                <li>📈 Capacity: <strong>{capacities[i]} %</strong></li>
                <li style='color:{status_color}; font-weight:bold;'>{modes[i]}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Prepare DataFrames for plotting
df = pd.DataFrame(st.session_state.history)
if not df.empty:
    df_expanded = pd.DataFrame({
        'timestamp': [t for t in df['timestamp'] for _ in range(num_cells)],
        'cell': [f'Cell {i+1}' for t in df['timestamp'] for i in range(num_cells)],
        'voltage': [v[i] for v in df['voltages'] for i in range(num_cells)],
        'current': [c[i] for c in df['currents'] for i in range(num_cells)],
        'temperature': [temp[i] for temp in df['temperatures'] for i in range(num_cells)],
        'capacity': [cap[i] for cap in df['capacities'] for i in range(num_cells)],
        'mode': [m[i] for m in df['modes'] for i in range(num_cells)],
    })

    # Voltage graph
    st.markdown("### 📈 Voltage Tracking Over Time")
    fig_v = go.Figure()
    for i in range(num_cells):
        volt_series = [entry['voltages'][i] for entry in st.session_state.history]
        time_series = [entry['timestamp'] for entry in st.session_state.history]
        fig_v.add_trace(go.Scatter(x=time_series, y=volt_series, mode='lines+markers', name=f'Cell {i+1}'))
    fig_v.update_layout(xaxis_title='Time', yaxis_title='Voltage (V)', legend_title='Cells', template='plotly_white', height=350)
    st.plotly_chart(fig_v, use_container_width=True)

    # Current graph
    st.markdown("### ⚡ Current Tracking Over Time")
    fig_c = go.Figure()
    for i in range(num_cells):
        curr_series = [entry['currents'][i] for entry in st.session_state.history]
        time_series = [entry['timestamp'] for entry in st.session_state.history]
        fig_c.add_trace(go.Scatter(x=time_series, y=curr_series, mode='lines+markers', name=f'Cell {i+1}'))
    fig_c.update_layout(xaxis_title='Time', yaxis_title='Current (A)', legend_title='Cells', template='plotly_white', height=350)
    st.plotly_chart(fig_c, use_container_width=True)

    # Temperature graph
    st.markdown("### 🌡️ Temperature Tracking Over Time")
    fig_t = go.Figure()
    for i in range(num_cells):
        temp_series = [entry['temperatures'][i] for entry in st.session_state.history]
        time_series = [entry['timestamp'] for entry in st.session_state.history]
        fig_t.add_trace(go.Scatter(x=time_series, y=temp_series, mode='lines+markers', name=f'Cell {i+1}'))
    fig_t.update_layout(xaxis_title='Time', yaxis_title='Temperature (°C)', legend_title='Cells', template='plotly_white', height=350)
    st.plotly_chart(fig_t, use_container_width=True)

    # Capacity graph
    st.markdown("### 📈 Capacity Tracking Over Time")
    fig_cap = go.Figure()
    for i in range(num_cells):
        cap_series = [entry['capacities'][i] for entry in st.session_state.history]
        time_series = [entry['timestamp'] for entry in st.session_state.history]
        fig_cap.add_trace(go.Scatter(x=time_series, y=cap_series, mode='lines+markers', name=f'Cell {i+1}'))
    fig_cap.update_layout(xaxis_title='Time', yaxis_title='Capacity (%)', legend_title='Cells', template='plotly_white', height=350)
    st.plotly_chart(fig_cap, use_container_width=True)

else:
    st.info("No data to display yet. Please enter values and update the dashboard.")

# Footer
st.markdown("""
---
<p style='text-align: center;'>Made with ❤️ using Streamlit · 2025</p>
""", unsafe_allow_html=True)