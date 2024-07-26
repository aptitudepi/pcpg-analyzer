#!/usr/bin/env python3
# Devkumar Banerjee

import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

@st.cache_data
def showTable(filepath):
	return pd.read_csv(filepath)[["Sample_ID","Sample_type","Genotype","Source","Mut_Type","Experiment"]]

st.write(showTable("data/metadata.csv"), container_width=True, width=5000)
