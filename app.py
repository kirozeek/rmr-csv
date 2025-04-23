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
                rmr_range_df = pd.DataFrame()

            valid_heart_rates = df[df['HR(bpm)'] > 25]['HR(bpm)']
            if not valid_heart_rates.empty:
                resting_hr = valid_heart_rates.min()
                st.subheader("💓 Resting Heart Rate")
                st.markdown("A lower resting heart rate generally indicates better cardiovascular fitness and more efficient heart function. It means your heart doesn't have to work as hard to maintain a steady beat, which is associated with a reduced risk of heart disease and improved longevity.")

                def rank_rhr(hr, age, gender):
                    if gender == "Male":
                        if hr < 56: return "Athlete", "green"
                        elif hr < 61: return "Excellent", "limegreen"
                        elif hr < 67: return "Good", "yellowgreen"
                        elif hr < 74: return "Above Average", "orange"
                        elif hr < 81: return "Average", "orangered"
                        else: return "Below Average", "red"
                    elif gender == "Female":
                        if hr < 60: return "Athlete", "green"
                        elif hr < 65: return "Excellent", "limegreen"
                        elif hr < 70: return "Good", "yellowgreen"
                        elif hr < 76: return "Above Average", "orange"
                        elif hr < 82: return "Average", "orangered"
                        else: return "Below Average", "red"
                    else:
                        return "Unranked", "gray"

                if gender in ["Male", "Female"] and age > 0:
                    rhr_rank, rhr_color = rank_rhr(resting_hr, age, gender)
                    st.markdown(f"- 🔻 **Resting HR:** <span style='color:{rhr_color}'>{resting_hr:.0f} bpm</span> ({rhr_rank})", unsafe_allow_html=True)
                else:
                    st.markdown(f"- 🔻 **Resting HR:** `{resting_hr:.0f} bpm` _(Ranking requires age and gender input)_")
            else:
                st.warning("⚠️ No valid heart rate values found above 25 bpm.")

            if not rmr_range_df.empty:
                st.subheader("🥑 Fuel Utilization Breakdown")
                avg_fat_kcal = rmr_range_df['FAT(kcal)'].mean()
                avg_carb_kcal = rmr_range_df['CARBS(kcal)'].mean()
                total_kcal = avg_fat_kcal + avg_carb_kcal
                if total_kcal > 0:
                    fat_percent = (avg_fat_kcal / total_kcal) * 100
                    carb_percent = (avg_carb_kcal / total_kcal) * 100
                    fat_grams = avg_fat_kcal / 9
                    carb_grams = avg_carb_kcal / 4
                    st.markdown(f"""
                    - 🥑 **Fat:** {avg_fat_kcal:.3f} kcal/min → **{fat_grams:.3f} g/min** (**{fat_percent:.2f}%**)
                    - 🍞 **Carbohydrates:** {avg_carb_kcal:.3f} kcal/min → **{carb_grams:.3f} g/min** (**{carb_percent:.2f}%**)
                    """)
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=['Fat', 'Carbohydrates'],
                            values=[fat_percent, carb_percent],
                            marker=dict(colors=['yellow', 'dodgerblue']),
                            textinfo='label+percent',
                            hole=0.4
                        )
                    ])
                    fig.update_layout(title='Fuel Utilization Breakdown (Pie Chart)', height=400)
                    st.plotly_chart(fig, use_container_width=True)

                    # Metabolic Flexibility Calculation
                    met_flex_percent = (avg_fat_kcal / total_kcal) * 100
                    if met_flex_percent > 70:
                        flex_label, flex_color = "Excellent", "green"
                    elif met_flex_percent > 50:
                        flex_label, flex_color = "Moderate", "orange"
                    else:
                        flex_label, flex_color = "Low", "red"

                    st.markdown(f"- 🔄 **Metabolic Flexibility:** <span style='color:{flex_color}'>{met_flex_percent:.1f}%</span> ({flex_label})", unsafe_allow_html=True)
                else:
                    st.warning("⚠️ No fuel data available in the RMR window.")

            if gender in ["Male", "Female"] and height_in > 0 and weight_lb > 0 and age > 0:
                if gender == "Male":
                    predicted_rmr = 66 + (6.23 * weight_lb) + (12.7 * height_in) - (6.8 * age)
                else:
                    predicted_rmr = 655 + (4.35 * weight_lb) + (4.7 * height_in) - (4.7 * age)
                st.subheader("📐 Predicted vs. Measured RMR")
                st.markdown(f"- 🧮 **Predicted RMR (Mifflin-St Jeor):** `{predicted_rmr:.2f} kcal/day`")
                bar_fig = go.Figure(data=[
                    go.Bar(name="Measured RMR", x=["RMR"], y=[lowest_avg_rmr], marker_color="green"),
                    go.Bar(name="Predicted RMR", x=["RMR"], y=[predicted_rmr], marker_color="blue")
                ])
                bar_fig.update_layout(title="Measured vs. Predicted RMR", barmode="group", yaxis_title="kcal/day")
                st.plotly_chart(bar_fig, use_container_width=True)
                line_fig = go.Figure()
                line_fig.add_trace(go.Scatter(x=["Measured", "Predicted"], y=[lowest_avg_rmr, predicted_rmr], mode="lines+markers", name="RMR Comparison"))
                line_fig.update_layout(title="RMR Comparison (Line Graph)", yaxis_title="kcal/day")
                st.plotly_chart(line_fig, use_container_width=True)

                st.subheader("🍽️ Macronutrient Breakdown")
                if gender in ["Male", "Female"] and target_weight > 0 and lowest_avg_rmr > 0:
                    if gender == "Male":
                        protein_grams = target_weight * 1.0
                    else:
                        protein_grams = target_weight * 0.9

                    protein_cals = protein_grams * 4
                    fat_cals = 0.25 * lowest_avg_rmr
                    carb_cals = lowest_avg_rmr - protein_cals - fat_cals

                    fat_grams = fat_cals / 9
                    carb_grams = carb_cals / 4

                    macro_df = pd.DataFrame({
                        "Macronutrient": ["Carbohydrates", "Protein", "Fats", "Total"],
                        "Grams": [round(carb_grams), round(protein_grams), round(fat_grams), ""],
                        "Calories": [int(round(carb_cals)), int(round(protein_cals)), int(round(fat_cals)), int(round(lowest_avg_rmr))],
                        "% of Total Calories": [
    f"{round(carb_cals / lowest_avg_rmr * 100)}%",
    f"{round(protein_cals / lowest_avg_rmr * 100)}%",
    f"{round(fat_cals / lowest_avg_rmr * 100)}%",
    "100%"
]
                    })

                    st.table(macro_df)

              
            csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
                label="📥 Download Full CSV with RMR",
                data=csv,
                file_name="rmr_energy_results.csv",
                mime="text/csv"
            )
