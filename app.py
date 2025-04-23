import streamlit as st
import pandas as pd

st.set_page_config(page_title="🔥 RMR Calculator from PNOE CSV", page_icon="🔥")

st.title("🔥 Resting Metabolic Rate (RMR) Calculator")
st.markdown("""
Upload your **PNOE RMR CSV file** and this app will:
- Use the `EE(kcal/day)` column (energy expenditure) as your RMR value
- Find the **lowest average RMR** across *any* 60–90 second span
- Display the **lowest heart rate** (Resting Heart Rate), filtering out values ≤ 25 bpm
""")

uploaded_file = st.file_uploader("📤 Upload your PNOE CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=';')
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
    else:
        if "EE(kcal/day)" not in df.columns or "T(sec)" not in df.columns or "HR(bpm)" not in df.columns:
            st.error("❌ Required columns 'EE(kcal/day)', 'T(sec)', or 'HR(bpm)' not found in your CSV.")
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
            else:
                st.warning("⚠️ No valid time range found between 60–90 seconds.")

            # --- Resting Heart Rate (Filtered for HR > 25 bpm) ---
            valid_heart_rates = df[df['HR(bpm)'] > 25]['HR(bpm)']
            if not valid_heart_rates.empty:
                resting_hr = valid_heart_rates.min()
                st.subheader("💓 Resting Heart Rate")
                st.markdown(f"- 🔻 **Lowest Heart Rate (Resting HR):** `{resting_hr:.0f} bpm`")
            else:
                st.warning("⚠️ No valid heart rate values found above 25 bpm.")

            # --- Downloadable output ---
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Full CSV with RMR",
                data=csv,
                file_name="rmr_energy_results.csv",
                mime="text/csv"
            )
