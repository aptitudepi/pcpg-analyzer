#!/usr/bin/env python3
# Devkumar Banerjee

# Load library imports
import streamlit as st
import umap
from sklearn.decomposition import PCA
from sklearn import cluster
import hdbscan
import pandas as pd
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from scipy.stats import median_abs_deviation
import plotly.express as px

st.set_page_config(layout="wide")

# Define (mostly cached) helper functions for better performance
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]

    return df

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
def UMAP_model():
        return umap.UMAP(n_components=2, init='spectral',metric="euclidean")

@st.cache_data
def UMAP(top_genes):
	# Replace transposed columns with axes labels
        return pd.DataFrame(UMAP_model().fit_transform(top_genes), columns=["UMAP1", "UMAP2"])

def Metadata():
	return filter_dataframe(pd.read_csv("data/metadata.csv"))

#def Label():
	#if (algo == "HDBScan"):
		#return hdbscan.HDBSCAN(min_cluster_size=3,gen_min_span_tree=True).fit_predict(coords.reset_index(drop=True))
	#else:
		#return cluster.KMeans(n_clusters=5).fit_predict(coords)


def Plot(coords, label):
	fig = px.scatter(data_frame=coords, x="UMAP1", y="UMAP2", title="UMAP", color=label, labels={'color': 'Genotype', 'Sample_type': 'Sample Type', 'Mut_Type': 'Mutation Type', 'Source_sample':'Source Sample'}, height=800, hover_name="Sample_ID", hover_data={"UMAP1": False, "UMAP2": False,'Sample_type': True, 'Mut_Type': True, "Experiment":True}, symbol = "Source_sample")
	fig.update_traces(marker=dict(size=10))
	return fig

# Streamlit GUI/main elements start here:
def main():
	# Desired number of genes
	num_genes = st.slider("Top n genes", 300, 9000, 1000)

	# Desired clustering algorithm
	# algo = st.radio("Algorithm",["HDBScan","K Means Clustering"])

	# Perform the Data Preprocessing
	top_genes = Preprocess("data/logcpm.csv", num_genes)

	# Set metadata here
	metadf = Metadata()

	# Apply UMAP,combine 2D embedding coordinates with metadata to allow access in the plotting function
	coords = pd.concat([UMAP(top_genes), metadf], axis=1)

	# Cluster data for plot colors
	# clusters = Metadata()["Genotype"]
	# Create the UMAP plot
	fig = Plot(coords,metadf["Genotype"])

	# Display the plot in Streamlit
	st.plotly_chart(fig, use_container_width=True)
	pass

if __name__ == "__main__":
	main()
