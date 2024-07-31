#!/usr/bin/env python3
# Devkumar Banerjee

import pandas as pd
import altair as alt
import streamlit as st
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.set_page_config(layout="wide")

@st.cache_data
def showTable(filepath):
    return pd.read_csv(filepath)[["Sample_ID", "Sample_type", "Genotype", "Source", "Mut_Type", "Experiment"]]

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

def main():

	# Load data
	df = filter_dataframe(showTable("data/metadata.csv"))

	# Display filtered data
	st.dataframe(df, use_container_width=True)

	# Visualization
	st.header("Data Visualizations")

	# Bar Chart: Count of Genotypes
	st.subheader("Count of Genotypes")
	genotype_counts = df["Genotype"].value_counts()
	st.bar_chart(genotype_counts)

	# Bar Chart: Count of Sample Types
	st.subheader("Count of Sample Types")
	sample_type_counts = df["Sample_type"].value_counts()
	st.bar_chart(sample_type_counts)

	# Line Chart: Count of Genotypes over Sample Types
	st.subheader("Count of Genotypes over Sample Types")
	genotype_sample_counts = df.groupby("Sample_type")["Genotype"].count().reset_index()
	line_chart = alt.Chart(genotype_sample_counts).mark_line(point=True).encode(x=alt.X('Sample_type:N', title='Sample Type'),y=alt.Y('Genotype:Q', title='Count of Genotype'),tooltip=['Sample_type:N', 'Genotype:Q']).interactive()
	st.altair_chart(line_chart, use_container_width=True)

	# Scatter Plot: Sample Types vs. Mut_Type
	st.subheader("Sample Types vs. Mut_Type")
	st.write("Scatter plot to visualize the relationship between Sample Types and Mutation Types")
	st.scatter_chart(df, x="Sample_type", y="Mut_Type", size="Sample_ID", color="Genotype")

	# Pie Chart: Proportion of Mutation Types
	st.subheader("Proportion of Mutation Types")
	mut_type_counts = df["Mut_Type"].value_counts().reset_index()
	mut_type_counts.columns = ['Mut_Type', 'Count']
	pie_chart = alt.Chart(mut_type_counts).mark_arc().encode(theta=alt.Theta(field="Count", type="quantitative"),color=alt.Color(field="Mut_Type", type="nominal"),tooltip=['Mut_Type', 'Count']).interactive()
	st.altair_chart(pie_chart, use_container_width=True)

	# Heatmap: Correlation between Sample Types and Mutation Types
	st.subheader("Correlation between Sample Types and Mutation Types")
	heatmap = alt.Chart(df).mark_rect().encode(x='Sample_type',y='Mut_Type',color='count()',tooltip=['count()']).interactive()
	st.altair_chart(heatmap, use_container_width=True)

	pass

if __name__ == "__main__":
        main()
