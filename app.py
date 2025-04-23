import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="🔥 RMR Calculator from PNOE CSV", page_icon="🔥")

st.title("🔥 Resting Metabolic Rate (RMR) Calculator")
st.markdown("""
Upload your **PNOE RMR CSV file** and this app will:
- Use the `EE(kcal/day)` column as your RMR value
- Find the **lowest average RMR** across any 60–90 second span
- Display the **resting heart rate** (lowest HR > 25 bpm)
- Show **fat vs. carbohydrate utilization** with a pie chart
- Display **average breathing frequency** during the RMR window
""")

uploaded_file = st.file_uploader("📤 Upload your PNOE CSV file", type="csv")

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

            # --- Smart Rolling Window Analysis (60–90 second windows) ---
            st.subheader("🧠 Lowest Average RMR (60–90 Second Span)")

            def find_lowest_average_rmr(df, min_window=60, max_window=90):
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

                # Subset data for this time range
                rmr_range_df = df[(df['T(sec)'] >= start_time) & (df['T(sec)'] <= end_time)]

                # --- Average Breathing Frequency ---
                avg_bf = rmr_range_df['BF(bpm)'].mean()
                st.markdown(f"- 💨 **Average Breathing Frequency:** `{avg_bf:.2f} breaths/min`")

            else:
                st.warning("⚠️ No valid time range found between 60–90 seconds.")
                rmr_range_df = pd.DataFrame()

            # --- Resting Heart Rate (Filtered for HR > 25 bpm) ---
            valid_heart_rates = df[df['HR(bpm)'] > 25]['HR(bpm)']
            if not valid_heart_rates.empty:
                resting_hr = valid_heart_rates.min()
                st.subheader("💓 Resting Heart Rate")
                st.markdown(f"- 🔻 **Lowest Heart Rate (Resting HR):** `{resting_hr:.0f} bpm`")
            else:
                st.warning("⚠️ No valid heart rate values found above 25 bpm.")

            # --- Fat vs Carbohydrate Utilization Analysis ---
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

                    # Plotly pie chart
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=['Fat', 'Carbohydrates'],
                            values=[fat_percent, carb_percent],
                            marker=dict(colors=['yellow', 'dodgerblue']),
                            textinfo='label+percent',
                            hole=0.4
                        )
                    ])
                    fig.update_layout(
                        title='Fuel Utilization Breakdown (Pie Chart)',
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ No fuel data available in the RMR window.")

            # --- Downloadable output ---
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Full CSV with RMR",
                data=csv,
                file_name="rmr_energy_results.csv",
                mime="text/csv"
            )
