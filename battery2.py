import streamlit as st
import random
import time
import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO
import datetime


# ------------------ Streamlit UI Config ------------------
st.set_page_config(page_title="🔋 Battery Simulator", layout="wide")
st.markdown("""
    <style>
        body {
            background-color: #fdfdfd;
            font-size: 1.1rem;
            color: #111;
        }
        .gradient-box {
            background: linear-gradient(90deg, #5eaaa8, #a3d2ca);
            padding: 2rem;
            border-radius: 16px;
            color: white;
            font-size: 3rem;
            text-align: center;
            font-weight: 800;
            margin-bottom: 2rem;
        }
        .metric-box {
            background-color: #f4f4f4;
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        }
        .sidebar-nav h1, .sidebar-nav h2, .sidebar-nav h3, .sidebar-nav h4 {
            color: #333;
        }
        .sidebar-nav a {
            color: #5eaaa8;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="gradient-box">🔋 Interactive Battery Simulation Dashboard</div>', unsafe_allow_html=True)

# ------------------ Sidebar Navigation ------------------
st.sidebar.title("🔧 Navigation")
nav_option = st.sidebar.radio("Select Page", ["Dashboard", "Simulation"])

if nav_option == "Dashboard":
    with st.sidebar.expander("🔋 Cell Configuration", expanded=True):
        number_of_cells = st.number_input("Enter number of cells", min_value=1, max_value=10, value=3)
        cell_types = []
        for i in range(number_of_cells):
            cell_type = st.selectbox(f"Select type for Cell {i+1}", ["lfp", "nmc"], key=f"cell_{i}")
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

    # ------------------ Dashboard Display ------------------
    st.markdown('<div class="gradient-box">📊 Battery Dashboard</div>', unsafe_allow_html=True)
    cols = st.columns(number_of_cells)
    selected_cell = None
    for idx, (key, data) in enumerate(cells_data.items()):
        with cols[idx]:
            if st.button(f"{key}", key=f"btn_{idx}"):
                selected_cell = key
            charge_percent = (data["voltage"] - data["min_voltage"]) / (data["max_voltage"] - data["min_voltage"]) * 100
            st.progress(charge_percent / 100, f"{charge_percent:.1f}%")

    # ------------------ Cell Detail Sidebar ------------------
    if selected_cell:
        st.sidebar.subheader(f"🔍 Details of {selected_cell}")
        details = cells_data[selected_cell]
        for k, v in details.items():
            st.sidebar.write(f"{k}: {v}")

elif nav_option == "Simulation":
    st.markdown('<div class="gradient-box">🛠 Simulation & Export</div>', unsafe_allow_html=True)
    add_vertical_space(1)

    task_types = ["CC_CV", "IDLE", "CC_CD"]
    num_tasks = st.number_input("Enter number of tasks", min_value=1, max_value=5, value=2)

    simulation_data = []
    task_list = []
    for i in range(num_tasks):
        st.markdown(f"#### Task {i+1}")
        task_type = st.selectbox(f"Select task type for Task {i+1}", task_types, key=f"task_type_{i}")
        task = {"task_type": task_type}

        if task_type == "CC_CV":
            task["cc_cp"] = st.text_input(f"CC/CP value for Task {i+1} (e.g. '5A')", key=f"cccv_{i}")
            task["cv_voltage"] = st.number_input("CV Voltage (V)", key=f"cv_{i}")
            task["current"] = st.number_input("Current (A)", key=f"cur_{i}")
            task["capacity"] = st.number_input("Capacity", key=f"cap_{i}")
            task["time_seconds"] = st.slider("Duration (s)", 5, 60, 10, key=f"time_{i}")

        elif task_type == "IDLE":
            task["time_seconds"] = st.slider("Duration (s)", 5, 60, 10, key=f"idle_time_{i}")

        elif task_type == "CC_CD":
            task["cc_cp"] = st.text_input(f"CC/CP value for Task {i+1} (e.g. '5A')", key=f"cccd_{i}")
            task["voltage"] = st.number_input("Voltage (V)", key=f"volt_{i}")
            task["capacity"] = st.number_input("Capacity", key=f"cap_cd_{i}")
            task["time_seconds"] = st.slider("Duration (s)", 5, 60, 10, key=f"cd_time_{i}")

        task_list.append(task)

    if st.button("▶️ Run Simulation"):
        st.success("Simulation running...")
        for i, task in enumerate(task_list):
            row = {"Task": f"Task {i+1}", "Type": task["task_type"], "Start": datetime.datetime.now().strftime("%H:%M:%S")}
            time.sleep(1)
            row["End"] = datetime.datetime.now().strftime("%H:%M:%S")
            simulation_data.append(row)
        st.success("✅ Simulation complete!")

        df = pd.DataFrame(simulation_data)
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results", data=csv, file_name="simulation_results.csv", mime="text/csv")

