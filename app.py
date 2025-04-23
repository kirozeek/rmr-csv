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

st.title("🔥 Resting Metabolic Rate (RMR) Calculator")

# --- Display Client Info ---
if first_name or last_name:
    st.markdown(f"### Report for: **{first_name} {last_name}**")
    st.markdown(f"- 🗓️ **Date of Test:** {test_date}")
    st.markdown(f"- 👤 **Gender:** {gender}")
    st.markdown(f"- 🎂 **Age:** {age} years")
    st.markdown(f"- 📏 **Height:** {height_in:.1f} in")
    st.markdown(f"- ⚖️ **Weight:** {weight_lb:.1f} lbs")

st.markdown("""
Upload your **RMR CSV file** and this app will:
- Use the `EE(kcal/day)` column as your RMR value
- Find the **lowest average RMR** across any 75–90 second span
- Display the **resting heart rate** (lowest HR > 25 bpm)
- Display **average breathing frequency** with hypoventilation/hyperventilation alerts
- Show **fat vs. carbohydrate utilization** with a pie chart
""")

uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=';')
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
    else:
        required_cols = ["EE(kcal/day)", "T(sec)", "HR(bpm)", "FAT(kcal)", "CARBS(kcal)", "BF(bpm)"]
        missing = [col for col in required_cols if col not in df.columns]

        if missing:
            st.error(f"❌ Missing required columns: {', '.join(missing)}")
        else:
            st.success("✅ File loaded successfully.")

            st.subheader("🧠 Lowest Average RMR (75–90 Second Span)")
            st.markdown("Knowing your Resting Metabolic Rate (RMR) helps determine the minimum number of calories your body needs to function at rest. This baseline is essential for designing effective weight management plans, setting accurate calorie targets, and understanding how your metabolism supports overall energy balance.")

            def find_lowest_average_rmr(df, min_window=75, max_window=90):
                best_avg = float('inf')
                best_start_time = None
                best_end_time = None

                time_points = df['T(sec)'].tolist()
                for i in range(len(time_points)):
                    for j in range(i + 1, len(time_points)):
                        start_time = time_points[i]
                        end_time = time_points[j]
                        duration = end_time - start_time

                        if min_window <= duration <= max_window:
                            sub_df = df[(df['T(sec)'] >= start_time) & (df['T(sec)'] <= end_time)]
                            avg_rmr = sub_df['EE(kcal/day)'].mean()

                            if avg_rmr < best_avg:
                                best_avg = avg_rmr
                                best_start_time = start_time
                                best_end_time = end_time

                return best_avg, best_start_time, best_end_time

            lowest_avg_rmr, start_time, end_time = find_lowest_average_rmr(df)

            if start_time is not None and end_time is not None:
                st.markdown(f"""
                - 🟢 **Lowest Rolling Average RMR:** `{lowest_avg_rmr:.2f} kcal/day`
                - ⏱️ **Time Range:** `{start_time} sec to {end_time} sec` (`{end_time - start_time:.0f} seconds`)
                """)

                rmr_range_df = df[(df['T(sec)'] >= start_time) & (df['T(sec)'] <= end_time)]

                avg_bf = rmr_range_df['BF(bpm)'].mean()

                if avg_bf < 6:
                    st.markdown(f"- 💨 **Average Breathing Frequency:** <span style='color:red'>{avg_bf:.2f} breaths/min</span> ⚠️ _Hypoventilation_", unsafe_allow_html=True)
                elif avg_bf > 18:
                    st.markdown(f"- 💨 **Average Breathing Frequency:** <span style='color:red'>{avg_bf:.2f} breaths/min</span> ⚠️ _Hyperventilation_", unsafe_allow_html=True)
                else:
                    st.markdown(f"- 💨 **Average Breathing Frequency:** `{avg_bf:.2f} breaths/min`")
            else:
                st.warning("⚠️ No valid time range found between 75–90 seconds.")
