#!/usr/bin/env python3
# Devkumar Banerjee

import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

@st.cache_data
def showTable(filepath):
	return pd.read_csv(filepath)

st.write(showTable("data/metadata.csv"), use_container_width=True)
