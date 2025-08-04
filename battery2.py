import streamlit as st
import random
import time
import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO
import datetime
import plotly.graph_objs as go

# ------------------ Streamlit UI Config ------------------
st.set_page_config(page_title="Battery Simulator", layout="wide")
st.markdown("""
    <style>
        html, body {
            background-color: #fefefe;
            font-family: 'Segoe UI', sans-serif;
        }
        .stButton>button {
            background-color: #0d6efd;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: bold;
            transition: 0.3s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #0b5ed7;
        }
        .stProgress > div > div > div > div {
            background-color: #20c997;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#333'><span style='color:#0d6efd'>Interactive Battery Simulation Dashboard</span></h1>", unsafe_allow_html=True)

# ------------------ Sidebar Configuration ------------------
st.sidebar.markdown("<h2 style='color:#0d6efd'>Configuration</h2>", unsafe_allow_html=True)

dark_mode = st.sidebar.toggle("Dark Mode")

number_of_cells = st.sidebar.slider("Number of Cells", min_value=1, max_value=10, value=3)
cell_types = []
for i in range(number_of_cells):
    cell_type = st.sidebar.selectbox(f"Type for Cell {i+1}", ["lfp", "nmc"], key=f"cell_{i}")
    cell_types.append(cell_type)

# ------------------ Generate Cells Data ------------------
cells_data = {}
for idx, cell_type in enumerate(cell_types, start=1):
    cell_key = f"Cell {idx} ({cell_type})"
    voltage = 3.2 if cell_type == "lfp" else 3.6
    min_voltage = 2.8 if cell_type == "lfp" else 3.2
    max_voltage = 3.6 if cell_type == "lfp" else 4.0
    current = round(random.uniform(0.5, 2.0), 2)
    temp = round(random.uniform(25, 40), 1)
    capacity = round(voltage * current, 2)
    cells_data[cell_key] = {
        "voltage": voltage,
        "current": current,
        "temp": temp,
        "capacity": capacity,
        "min_voltage": min_voltage,
        "max_voltage": max_voltage
    }

# ------------------ Battery Dashboard ------------------
st.markdown("<h2 style='color:#20c997'>Battery Dashboard</h2>", unsafe_allow_html=True)
cols = st.columns(number_of_cells)
selected_cell = None

for idx, (key, data) in enumerate(cells_data.items()):
    with cols[idx]:
        if st.button(f"{key}", key=f"btn_{idx}"):
            selected_cell = key
        charge_percent = (data["voltage"] - data["min_voltage"]) / (data["max_voltage"] - data["min_voltage"]) * 100
        st.progress(charge_percent / 100, f"{charge_percent:.1f}%")

# ------------------ Cell Details ------------------
if selected_cell:
    st.sidebar.markdown(f"<h3 style='color:#20c997'>Details of {selected_cell}</h3>", unsafe_allow_html=True)
    for k, v in cells_data[selected_cell].items():
        st.sidebar.write(f"{k.capitalize()}: {v}")

# ------------------ Task Simulation ------------------
st.markdown("<h2 style='color:#6f42c1'>Task Simulation</h2>", unsafe_allow_html=True)
task_types = ["CC_CV", "IDLE", "CC_CD"]
num_tasks = st.slider("Number of tasks", 1, 5, 2)
task_list = []

for i in range(num_tasks):
    st.markdown(f"<h4 style='color:#6f42c1'>Task {i+1}</h4>", unsafe_allow_html=True)
    task_type = st.selectbox(f"Task type {i+1}", task_types, key=f"task_type_{i}")
    task = {"task_type": task_type}

    if task_type == "CC_CV":
        task["cc_cp"] = st.text_input(f"CC/CP (e.g., '5A')", key=f"cccv_{i}")
        task["cv_voltage"] = st.number_input("CV Voltage (V)", key=f"cv_{i}")
        task["current"] = st.number_input("Current (A)", key=f"cur_{i}")
        task["capacity"] = st.number_input("Capacity", key=f"cap_{i}")
        task["time_seconds"] = st.slider("Duration (s)", 5, 60, 10, key=f"time_{i}")

    elif task_type == "IDLE":
        task["time_seconds"] = st.slider("Duration (s)", 5, 60, 10, key=f"idle_time_{i}")

    elif task_type == "CC_CD":
        task["cc_cp"] = st.text_input(f"CC/CP (e.g., '5A')", key=f"cccd_{i}")
        task["voltage"] = st.number_input("Voltage (V)", key=f"volt_{i}")
        task["capacity"] = st.number_input("Capacity", key=f"cap_cd_{i}")
        task["time_seconds"] = st.slider("Duration (s)", 5, 60, 10, key=f"cd_time_{i}")

    task_list.append(task)

# ------------------ Simulation Button ------------------
if st.button("Start Simulation"):
    st.success("Running simulation...")
    voltages, currents, temps, times = [], [], [], []
    progress_bar = st.progress(0)
    graph_placeholder = st.empty()
    start_time = datetime.datetime.now()

    for t in range(100):
        voltage = round(random.uniform(3.0, 4.2), 2)
        current = round(random.uniform(0.5, 5.0), 2)
        temp = round(random.uniform(25, 45), 1)

        voltages.append(voltage)
        currents.append(current)
        temps.append(temp)
        times.append(t)

        progress_bar.progress((t + 1) / 100)
        time.sleep(0.05)

        with graph_placeholder.container():
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=times, y=voltages, mode='lines+markers', name='Voltage (V)', line=dict(color='green')))
            fig.add_trace(go.Scatter(x=times, y=currents, mode='lines+markers', name='Current (A)', yaxis='y2', line=dict(color='blue')))

            fig.update_layout(
                title="Real-Time Voltage and Current vs Time",
                xaxis=dict(title='Time (s)'),
                yaxis=dict(title='Voltage (V)', titlefont=dict(color='green'), tickfont=dict(color='green')),
                yaxis2=dict(title='Current (A)', overlaying='y', side='right', titlefont=dict(color='blue'), tickfont=dict(color='blue')),
                legend=dict(x=0.01, y=0.99),
                template='plotly_dark' if dark_mode else 'plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)

    st.success("Simulation Complete!")

    df = pd.DataFrame({
        "Time (s)": times,
        "Voltage (V)": voltages,
        "Current (A)": currents,
        "Temperature (°C)": temps
    })

    st.markdown("<h3 style='color:#0d6efd'>Export Graph Data</h3>", unsafe_allow_html=True)
    st.dataframe(df.head())
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button("Download Simple CSV", csv_buffer.getvalue(), "battery_simulation_data.csv", "text/csv")
