import streamlit as st
import umap
import pandas as pd
from scipy.stats import median_abs_deviation
import plotly.express as px

df = pd.read_csv("data/logcpm.csv")

df["MAD"] = df.iloc[: , 1:].apply(lambda row: median_abs_deviation(row, scale=1), axis=1)

df
df.columns
# Select top genes based on MAD
num_genes = st.slider('x')  # Replace with your desired number of genes
top_genes = df.iloc[df["MAD"].argsort()[::-1][:num_genes]]
top_genes
# Apply UMAP
reducer = umap.UMAP()
result = reducer.fit_transform(df.iloc[: , 1:])

# umap_result now contains the 2D embedding coordinates

# Create the UMAP plot
fig = px.scatter(
    x=result[:, 0],
    y=result[:, 1],
    labels={'x': 'UMAP1', 'y': 'UMAP2'},
    title='UMAP Projection of Gene Expression Data'
)

# Display the plot in Streamlit
st.plotly_chart(fig)
