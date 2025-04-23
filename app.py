import streamlit as st
import pandas as pd

st.set_page_config(page_title="🔥 RMR Calculator from PNOE CSV", page_icon="🔥")

st.title("🔥 Resting Metabolic Rate (RMR) Calculator")
st.markdown("""
Upload your **PNOE RMR CSV file** and this app will:
- Use the `EE(kcal/day)` column (energy expenditure) as your RMR value
- Analyze a 60–90 second window
- Display the lowest and average RMR in that timeframe
""")

uploaded_file = st.file_uploader("📤 Upload your PNOE CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Load CSV with PNOE formatting (semicolon-separated)
        df = pd.read_csv(uploaded_file, sep=';')

        # Check for energy expenditure column
        if "EE(kcal/day)" not in df.columns:
            st.error("❌ Could not find column 'EE(kcal/day)' in your CSV.")
        else:
            st.success("✅ Found Energy Expenditure data!")

            st.subheader("📋 Preview of Energy Expenditure Data")
            st.dataframe(df[['T(sec)', 'PHASE', 'EE(kcal/day)']])

            # --- Range Analysis (60–90 sec) ---
            st.subheader("📊 RMR Analysis Between 60–90 Seconds")

            filtered_df = df[(df['T(sec)'] >= 60) & (df['T(sec)'] <= 90)]

            if not filtered_df.empty:
                lowest_rmr_row = filtered_df.loc[filtered_df['EE(kcal/day)'].idxmin()]
                average_rmr = filtered_df['EE(kcal/day)'].mean()

                st.markdown(f"""
                - 🔻 **Lowest RMR:** `{lowest_rmr_row['EE(kcal/day)']:.2f} kcal/day` at `T = {lowest_rmr_row['T(sec)']} sec`
                - 📈 **Average RMR:** `{average_rmr:.2f} kcal/day` between 60–90 seconds
                """)
            else:
                st.warning("⚠️ No data points found between 60 and 90 seconds.")

            # --- Downloadable output ---
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Full CSV with RMR",
                data=csv,
                file_name="rmr_energy_results.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
