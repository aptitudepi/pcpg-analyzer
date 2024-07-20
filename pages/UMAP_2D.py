#!/usr/bin/env python3
# Devkumar Banerjee

# Load library imports
import streamlit as st
import umap
from sklearn.decomposition import PCA
from sklearn import cluster
import hdbscan
import pandas as pd
from scipy.stats import median_abs_deviation
import plotly.express as px

st.set_page_config(layout="wide")

# Define (cached) helper functions for better performance
@st.cache_data
def Preprocess(filepath, num_genes):
	df = pd.read_csv("data/logcpm.csv")
	# Select top genes based on Median Absolute Deviation (MAD)
	df["MAD"] = df.iloc[: , 1:].apply(lambda row: median_abs_deviation(row, scale=1), axis=1)
	top_genes = df.sort_values(by=["MAD"],ascending=False).head(num_genes)
	# Drop the final MAD column since it is not needed anymore
	# It will also prepare the DataFrame to make transposition more simple
	top_genes.drop(['MAD'], axis=1, inplace=True)
	# Transpose our dataframe such that the samples become rows, and the genes become columns
	top_genes = top_genes.set_index("GENE").T
	# st.write(top_genes)
	return top_genes

@st.cache_resource
def UMAP_model(num_neighbors,min_distance):
        return umap.UMAP(n_components=2, init='spectral',n_neighbors=num_neighbors,min_dist=min_distance,metric="euclidean")

@st.cache_data
def UMAP(top_genes,num_neighbors,min_distance):
	# Replace transposed columns with axes labels
        return pd.DataFrame(UMAP_model(num_neighbors,min_distance).fit_transform(top_genes), columns=["UMAP1", "UMAP2"])

@st.cache_data
def Metadata():
	return pd.read_csv("data/Metadata_allsamples.csv")

@st.cache_data
def Label(coloring):
	if (coloring == "Discriminating"):
		return Metadata()["Genotype_color"]
	else:
		return Metadata()["Genotype"]

#def Label():
	#if (algo == "HDBScan"):
		#return hdbscan.HDBSCAN(min_cluster_size=3,gen_min_span_tree=True).fit_predict(coords.reset_index(drop=True))
	#else:
		#return cluster.KMeans(n_clusters=5).fit_predict(coords)


def Plot(coords, label):
	fig = px.scatter(data_frame=coords, x="UMAP1", y="UMAP2", title="UMAP", color=label, labels={'color': 'Genotype'}, height=800, hover_name="Sample_ID", hover_data=["Sample_type", "Genotype", "Source", "Mut_Type", "Experiment", "Genotype_color", "Source_sample"])
	fig.update_traces(marker=dict(size=7))
	return fig

# Streamlit GUI/main elements start here:
def main():
	# Desired number of genes
	num_genes = st.slider("Top n genes", 300, 9000, 1000)

	# Desired number of neighbors
	num_neighbors = st.slider("Number of Neighbors (UMAP Hyperparameter)", 1, 1000, 15)

	# Desired number of genes
	min_distance = st.slider("Minimum Distance (UMAP Hyperparameter)", 0.0, 1.0, 0.1)

	# Desired clustering algorithm
	# algo = st.radio("Algorithm",["HDBScan","K Means Clustering"])

	# Desired Coloring Type
	coloring = st.radio("Coloring Type", ["Discriminating", "Nondiscriminating"])

	# Perform the Data Preprocessing
	top_genes = Preprocess("data/logcpm.csv", num_genes)

	# Apply UMAP,combine 2D embedding coordinates with metadata to allow access in the plotting function
	coords = pd.concat([UMAP(top_genes,num_neighbors,min_distance), Metadata()], axis=1)

	# Cluster data for plot colors
	# clusters = Label(algo, coords)
	clusters = Label(coloring)

	# Create the UMAP plot
	fig = Plot(coords,clusters)

	# Display the plot in Streamlit
	st.plotly_chart(fig, use_container_width=True)
	pass

if __name__ == "__main__":
	main()
