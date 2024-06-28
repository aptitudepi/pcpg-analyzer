#!/usr/bin/env python3
# Devkumar Banerjee

# Load library imports
import streamlit as st
import umap
import pandas as pd
from scipy.stats import median_abs_deviation
import plotly.express as px

# Load the Input Data
df = pd.read_csv("data/logcpm.csv")

# Select top genes based on Median Absolute Deviation (MAD)
df["MAD"] = df.iloc[: , 1:].apply(lambda row: median_abs_deviation(row, scale=1), axis=1)
num_genes = st.slider("Top n genes", 300, 9000, 1000)  # Replace with your desired number of genes
top_genes = df.sort_values(by=["MAD"]).head(num_genes)

# Drop the final MAD column since it is not needed anymore
# It will also prepare the DataFrame to make transposition more simple
top_genes.drop(['MAD'], axis=1, inplace=True)

# Transpose our dataframe such that the samples become rows, and the genes become columns
top_genes = top_genes.set_index("GENE").T

# Apply UMAP
reducer = umap.UMAP(n_components=2, init='random')
coords = reducer.fit_transform(top_genes)

# Replace transposed columns with axes labels
coords = pd.DataFrame(coords, columns=["UMAP1", "UMAP2"])
# umap_result now contains the 2D embedding coordinates

# Create the UMAP plot
fig = px.scatter(
    coords, x="UMAP1", y="UMAP2", color=top_genes.index, labels={'color': 'Sample'}
)
fig.update_traces(marker=dict(size=7))

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)
