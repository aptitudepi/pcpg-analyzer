import streamlit as st
import umap
import pandas as pd
from scipy.stats import median_abs_deviation
import plotly.express as px
import umap.plot

df = pd.read_csv("data/logcpm.csv")

df

df["MAD"] = df.iloc[: , 1:].apply(lambda row: median_abs_deviation(row, scale=1), axis=1)

# Select top genes based on MAD
num_genes = st.slider("Top n genes", 300, 3000, 1000)  # Replace with your desired number of genes
top_genes = df.sort_values(by=["MAD"]).head(num_genes)
top_genes.drop(['MAD'], axis=1, inplace=True)

# Transpose our dataframe such that the samples become rows, and the genes, columns
top_genes = top_genes.set_index("GENE").T

# Apply UMAP
reducer = umap.UMAP(n_components=3, init='random', random_state=0)
coords = reducer.fit_transform(top_genes)
coords = pd.DataFrame(coords, columns=["UMAP1", "UMAP2", "UMAP3"])
# umap_result now contains the 2D embedding coordinates

# Create the UMAP plot
fig = px.scatter_3d(
    coords, x="UMAP1", y="UMAP2", z="UMAP3", color=top_genes.index, labels={'color':'Sample'}
)

# Display the plot in Streamlit
st.plotly_chart(fig)
