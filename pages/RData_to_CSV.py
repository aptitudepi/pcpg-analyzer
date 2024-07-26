#!/usr/bin/env python3
# Devkumar Banerjee

import pandas as pd
import streamlit as st
import pyreadr
import io

st.set_page_config(layout="wide")

@st.cache_data
def read_rdata(upfile):
    # Create a temporary file to store the uploaded content
    with open("/tmp/temp.RData", "wb") as f:
        f.write(upfile.getvalue())
    # Read the temporary file using pyreadr
    return pyreadr.read_r("/tmp/temp.RData")

@st.cache_data
def dataframe_to_csv(df):
	df.insert(0, "GENE", df.index)
	return df.to_csv(index=False).encode("utf-8")

st.title("RData to CSV Converter")

uploaded_file = st.file_uploader("Upload your RData file here!", type=["RData", "rdata"])

if uploaded_file is not None:
    try:
        read_file = read_rdata(uploaded_file)
        option = st.selectbox(
            "Which dataframe would you like to download?",
            list(read_file.keys()),
            index=None,
            placeholder="Select dataframe.",
        )
        if option:
            selected_df = pd.DataFrame(read_file[option])
            csv_data = dataframe_to_csv(selected_df)
            st.download_button(
                label="Download your dataframe as CSV",
                data=csv_data,
                file_name=f"{option}.csv",
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    st.info("Please upload an RData file to begin.")
