import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# Page config
st.set_page_config(page_title="Stunning Battery Dashboard", layout="wide", initial_sidebar_state="expanded")

# CSS styling for visuals
st.markdown("""
    <style>
    /* Header Banner */
    .header-container {
        padding: 1.5rem;
        background: linear-gradient(to right, #f9d423, #ff4e50);
        color: white;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.2);
    }
    .header-container h1 {
        font-size: 3rem;
        font-weight: bold;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.3);
    }

    /* Cell card effect */
    .cell-card {
        background: linear-gradient(145deg, #e3f2fd, #ffffff);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .cell-card:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
    }

    /* Summary metric styling */
    .summary-box {
        background: linear-gradient(to right, #00c6ff, #0072ff);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        color: #333;
        background: #e3f2fd;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(to right, #2196f3, #21cbf3);
        color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ---------- State ----------
if 'history' not in st.session_state:
    st.session_state.history = []
if 'autoupdate' not in st.session_state:
    st.session_state.autoupdate = False
if 'max_history' not in st.session_state:
    st.session_state.max_history = 100

# ---------- Header ----------
st.markdown("""
<div class="header-container">
    <h1>🔋  Battery Monitoring Dashboard</h1>
    <p style="margin-top: 5px; font-size: 1.2rem;">Live metrics, alerts & visual analytics for battery cells</p>
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.markdown("## ⚙️ Configuration")
num_cells = st.sidebar.slider("🔢 Number of Cells", 1, 20, 8)
temp_threshold = st.sidebar.number_input("🌡️ Temp Threshold", 0, 100, 40)
volt_threshold = st.sidebar.number_input("⚡ Voltage Threshold", 0.0, 5.0, 3.5)
autoupdate = st.sidebar.checkbox("🔄 Auto Refresh", value=st.session_state.autoupdate)
st.session_state.autoupdate = autoupdate
if autoupdate:
    st_autorefresh(interval=1000, limit=None, key="autorefresh")

voltages, currents, temperatures, capacities, modes = [], [], [], [], []
mode_options = ['Charging', 'Discharging', 'Idle']
for i in range(num_cells):
    with st.sidebar.expander(f"🔋 Cell {i+1}"):
        voltages.append(st.number_input("Voltage", value=3.7, step=0.01, key=f"v_{i}"))
        currents.append(st.number_input("Current", value=0.0, step=0.01, key=f"c_{i}"))
        temperatures.append(st.number_input("Temp", value=25.0, step=0.1, key=f"t_{i}"))
        capacities.append(st.number_input("Capacity (%)", 0, 100, 100, key=f"cap_{i}"))
        modes.append(st.selectbox("Mode", options=mode_options, index=2, key=f"m_{i}"))

if st.sidebar.button("🚀 Update Now") or autoupdate:
    st.session_state.history.append({
        'timestamp': datetime.now(),
        'voltages': voltages.copy(),
        'currents': currents.copy(),
        'temperatures': temperatures.copy(),
        'capacities': capacities.copy(),
        'modes': modes.copy()
    })
    if len(st.session_state.history) > st.session_state.max_history:
        st.session_state.history = st.session_state.history[-st.session_state.max_history:]

# ---------- Main Tabs ----------
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Graphs", "⚙️ Settings"])

# ---------- Tab 1: Dashboard ----------
with tab1:
    st.subheader("🔋 Cell Overview")

    # Alerts
    alert_msgs = []
    for i in range(num_cells):
        if temperatures[i] > temp_threshold:
            alert_msgs.append(f"🔥 <strong>Cell {i+1} Overheating</strong>: {temperatures[i]:.1f} °C")
        if voltages[i] < volt_threshold:
            alert_msgs.append(f"⚡ <strong>Low Voltage</strong> on Cell {i+1}: {voltages[i]:.2f} V")
    if alert_msgs:
        st.markdown(f"""
        <div style="background:#fff8e1; padding:1rem; border-left:5px solid #ff9800; border-radius:10px;">
            <b>⚠️ Alerts:</b><br>
            {"<br>".join(alert_msgs)}
        </div>
        """, unsafe_allow_html=True)

    # Cells Display
    cell_rows = [st.columns(4) for _ in range((num_cells + 3) // 4)]
    mode_colors = {'Charging': '#4caf50', 'Discharging': '#e53935', 'Idle': '#90a4ae'}
    for i in range(num_cells):
        with cell_rows[i // 4][i % 4]:
            st.markdown(f"""
                <div class="cell-card">
                    <h4 style="text-align:center;">🔋 Cell {i+1}</h4>
                    <ul style="list-style:none; font-size:15px; color:#333;">
                        <li>🔌 Voltage: <b>{voltages[i]:.2f} V</b></li>
                        <li>⚡ Current: <b>{currents[i]:.2f} A</b></li>
                        <li>🌡️ Temp: <b>{temperatures[i]:.1f} °C</b></li>
                        <li>🔋 Capacity: <b>{capacities[i]}%</b></li>
                        <li style="color:{mode_colors[modes[i]]}; text-align:center;"><b>{modes[i]}</b></li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

    # Summary Metrics
    st.markdown("### 📌 Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='summary-box'>🔋<br><b>Avg Voltage:</b><br>{sum(voltages)/num_cells:.2f} V</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='summary-box'>🌡️<br><b>Avg Temp:</b><br>{sum(temperatures)/num_cells:.1f} °C</div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='summary-box'>📈<br><b>Avg Capacity:</b><br>{sum(capacities)/num_cells:.1f} %</div>", unsafe_allow_html=True)

# ---------- Tab 2: Graphs ----------
with tab2:
    st.subheader("📈 Historical Graphs")
    df = pd.DataFrame(st.session_state.history)
    if not df.empty:
        ts = [e["timestamp"] for e in st.session_state.history]
        metrics = ["voltages", "currents", "temperatures", "capacities"]
        labels = ["Voltage (V)", "Current (A)", "Temperature (°C)", "Capacity (%)"]
        for metric, label in zip(metrics, labels):
            fig = go.Figure()
            for i in range(num_cells):
                series = [entry[metric][i] for entry in st.session_state.history]
                fig.add_trace(go.Scatter(x=ts, y=series, mode='lines+markers', name=f"Cell {i+1}"))
            fig.update_layout(title=label, xaxis_title="Time", yaxis_title=label, height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet.")

# ---------- Tab 3: Settings ----------
with tab3:
    st.subheader("⚙️ Configuration & Reset")
    st.number_input("Max History Length", 10, 1000, value=st.session_state.max_history, step=10, key="max_history")
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.success("History Cleared.")

# ---------- Footer ----------
st.markdown("""
<hr>
<p style="text-align:center; color:#999;">🚀 Made with ❤️ in Streamlit · 2025</p>
""", unsafe_allow_html=True)
