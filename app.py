import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="🔥 RMR Calculator from CSV", page_icon="🔥")

# --- Sidebar: Client Information ---
st.sidebar.header("🧍 Client Information")
first_name = st.sidebar.text_input("First Name")
last_name = st.sidebar.text_input("Last Name")
test_date = st.sidebar.date_input("Date of Test")
gender = st.sidebar.selectbox("Gender", ["", "Male", "Female", "Other"])
age = st.sidebar.number_input("Age", min_value=0, max_value=120, step=1)
height_in = st.sidebar.number_input("Height (inches)", min_value=0.0, step=0.1)
weight_lb = st.sidebar.number_input("Weight (lbs)", min_value=0.0, step=0.1)
target_weight = st.sidebar.number_input("Target Weight (lbs)", min_value=0.0, step=0.1)

st.title("🔥 Resting Metabolic Rate (RMR) Calculator")

# --- Display Client Info ---
if first_name or last_name:
    st.markdown(f"### Report for: **{first_name} {last_name}**")
    st.markdown(f"- 🗓️ **Date of Test:** {test_date}")
    st.markdown(f"- 👤 **Gender:** {gender}")
    st.markdown(f"- 🎂 **Age:** {age} years")
    st.markdown(f"- 📏 **Height:** {height_in:.1f} in")
    st.markdown(f"- ⚖️ **Weight:** {weight_lb:.1f} lbs")
    if target_weight > 0:
        st.markdown(f"- 🎯 **Target Weight:** {target_weight:.1f} lbs")

st.markdown("""
Upload your **RMR CSV file** and this app will:
- Use the `EE(kcal/day)` column as your RMR value
- Find the **lowest average RMR** across any 75–90 second span
- Display the **resting heart rate** (lowest HR > 25 bpm)
- Display **average breathing frequency** with hypoventilation/hyperventilation alerts
- Show **fat vs. carbohydrate utilization** with a pie chart
""")
