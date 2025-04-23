import streamlit as st
import pandas as pd

st.set_page_config(page_title="🔥 RMR Calculator from PNOE CSV", page_icon="🔥")

st.title("🔥 Resting Metabolic Rate (RMR) Calculator")
st.markdown("Upload your **PNOE RMR CSV file** and we’ll calculate RMR using `VO2(ml/min) × 1.44`.")

uploaded_file = st.file_uploader("📤 Upload your PNOE CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Load CSV with PNOE formatting (semicolon-separated)
        df = pd.read_csv(uploaded_file, sep=';')

        if "VO2(ml/min)" not in df.columns:
            st.error("Could not find column 'VO2(ml/min)' in your CSV.")
        else:
            # Calculate RMR
            df['RMR (kcal/day)'] = df['VO2(ml/min)'] * 1.44

            st.success("✅ RMR calculated successfully!")
            st.subheader("📋 Preview of Data with RMR")
            st.dataframe(df[['T(sec)', 'PHASE', 'VO2(ml/min)', 'RMR (kcal/day)']])

            # --- Range Analysis (60–90 sec) ---
            st.subheader("📊 Analysis: 60–90 Second Window")

            filtered_df = df[(df['T(sec)'] >= 60) & (df['T(sec)'] <= 90)]

            if not filtered_df.empty:
                lowest_rmr_row = filtered_df.loc[filtered_df['RMR (kcal/day)'].idxmin()]
                average_rmr = filtered_df['RMR (kcal/day)'].mean()

                st.markdown(f"""
                - 🔻 **Lowest RMR:** `{lowest_rmr_row['RMR (kcal/day)']:.2f} kcal/day` at `T = {lowest_rmr_row['T(sec)']} sec`
                - 📈 **Average RMR:** `{average_rmr:.2f} kcal/day` between 60–90 seconds
                """)
            else:
                st.warning("No data points found between 60 and 90 seconds.")

            # --- Downloadable output ---
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV with RMR",
                data=csv,
                file_name="rmr_results.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
