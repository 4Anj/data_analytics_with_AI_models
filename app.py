# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import re
from calendar import month_name

st.set_page_config(page_title="SmartViz: Ask Your Data", layout="wide")
st.title("📊 SmartViz: Ask Your Data")

# 📁 Upload CSV
st.sidebar.header("Upload your CSV")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Data loaded successfully!")

    # 🧠 Select Columns
    st.sidebar.header("Select Key Columns")
    date_col = st.sidebar.selectbox("📅 Date Column", df.columns, index=0)
    numeric_col = st.sidebar.selectbox("🔢 Numeric Column", df.select_dtypes("number").columns)

    # Preprocess Date & Time
    try:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df["Year"] = df[date_col].dt.year
        df["Quarter"] = df[date_col].dt.quarter
        df["Month"] = df[date_col].dt.month_name()
        df["Month_Num"] = df[date_col].dt.month
        df["Day"] = df[date_col].dt.day
    except Exception as e:
        st.error(f"❌ Date parsing error: {e}")

    st.subheader("📋 Dataset Preview")
    st.dataframe(df.head())

    # 📊 KPIs
    st.subheader("📊 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", f"{df[numeric_col].sum():,.2f}")
    col2.metric("Average", f"{df[numeric_col].mean():,.2f}")
    col3.metric("Max", f"{df[numeric_col].max():,.2f}")
    col4.metric("Min", f"{df[numeric_col].min():,.2f}")

    # 📈 Monthly Chart
    df["Month_Period"] = df[date_col].dt.to_period("M").astype(str)
    monthly_data = df.groupby("Month_Period")[numeric_col].sum().reset_index()
    st.subheader("📅 Monthly Trend")
    fig = px.line(monthly_data, x="Month_Period", y=numeric_col, markers=True)
    st.plotly_chart(fig, use_container_width=True)

    # 🧠 Custom Logic Q&A
    st.subheader("🤖 Ask Time-Based Questions About Your Data")

    # Mapping
    month_map = {m.lower(): m for m in month_name if m}
    quarters = {
        "q1": [1, 2, 3],
        "q2": [4, 5, 6],
        "q3": [7, 8, 9],
        "q4": [10, 11, 12]
    }

    def logic_answer(q):
        q = q.lower()
        try:
            year_match = re.search(r"(20\d{2})", q)
            year = int(year_match.group()) if year_match else None

            # Check for month name
            month = next((m for m in month_map if m in q), None)
            quarter = next((qtr for qtr in quarters if qtr in q), None)

            filtered_df = df.copy()
            if year:
                filtered_df = filtered_df[filtered_df["Year"] == year]
            if month:
                filtered_df = filtered_df[filtered_df["Month"].str.lower() == month]
            if quarter:
                filtered_df = filtered_df[filtered_df["Month_Num"].isin(quarters[quarter])]
                filtered_df = filtered_df[filtered_df["Month"].str.lower() == month]
            if quarter:
                filtered_df = filtered_df[filtered_df["Month_Num"].isin(quarters[quarter])]

            if filtered_df.empty:
                return "⚠️ No data found for that time period."

            if "total" in q or ("sum" in q and "average" not in q):
                return f"🧾 Total {numeric_col} in selected period: {filtered_df[numeric_col].sum():,.2f}"
            if "average" in q or "mean" in q:
                return f"📊 Average {numeric_col}: {filtered_df[numeric_col].mean():,.2f}"
            if "max" in q or "highest" in q:
                return f"📈 Max {numeric_col}: {filtered_df[numeric_col].sum():,.2f}"
            if "min" in q or "lowest" in q:
                return f"📉 Min {numeric_col}: {filtered_df[numeric_col].sum():,.2f}"
            if "daily" in q:
                daily = filtered_df.groupby(filtered_df[date_col].dt.date)[numeric_col].sum()
                return daily.to_string()

            return "⚠️ I only answer time-based questions like totals or averages for months, quarters, or years."
        except Exception as e:
            return f"❌ Error answering question: {str(e)}"

# ✅ Text input to ask question
question = st.text_input("Ask your question (e.g., total in April 2022, average in Q1, etc.):")
if question:
    response = logic_answer(question)
    st.success(response)
