import pandas as pd
import streamlit as st
import plotly.express as px

st.title("CSV → Chart")

file = st.file_uploader("Upload CSV", type=["csv"])

if file:
    df = pd.read_csv(file)

    st.subheader("Preview:")
    st.dataframe(df.head())

    x = st.selectbox("X-axis", df.columns)
    y = st.selectbox("Y-axis", df.columns)

    chart_type = st.selectbox("Chart Type", ["Line", "Bar", "Scatter"])

    if st.button("Generate Chart"):
        if chart_type == "Line":
            fig = px.line(df, x=x, y=y)
        elif chart_type == "Bar":
            fig = px.bar(df, x=x, y=y)
        else:
            fig = px.scatter(df, x=x, y=y)

        st.plotly_chart(fig)


