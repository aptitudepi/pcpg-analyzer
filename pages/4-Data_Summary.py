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
    df = pd.read_csv(filepath)[["Sample_ID", "Sample_type", "Genotype_color", "Source", "Mut_Type", "Experiment"]]
    m = {"Primary Tumor": ["Additional - New Primary", "Frozen Tumor","Primary Solid Tumor","Metastatic"],"Dissociated Tumor": ["Dissociated Tumor"], "Organoid": ["Organoid"]}
    inverse_m = {v: k for k, values in m.items() for v in (values if isinstance(values, list) else [values])}
    df['Sample_type'] = df['Sample_type'].replace(inverse_m)
    return df

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """

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

def plotter(df, colname, dispname, isStacked):
	col1, col2 = st.columns(2)
	with col1:

		col1.subheader("Proportion of " + dispname)

		if (isStacked):
			percentages = df[colname].value_counts(normalize=True).mul(100).round(1).reset_index()
			percentages.columns = [colname, 'Percentage']
			# Sort percentages in descending order
			percentages = percentages.sort_values('Percentage', ascending=False)
			# Calculate cumulative percentages for stacking
			percentages['cumulative'] = percentages['Percentage'].cumsum()
			percentages['cumulative_prev'] = percentages['cumulative'].shift(1, fill_value=0)
			# Create the stacked bar chart
			chart = alt.Chart(percentages).mark_bar().encode(y=alt.Y('cumulative_prev:Q', title='Percentage'),y2=alt.Y2('cumulative:Q'),x=alt.X('dummy:N', title='', axis=None),color=alt.Color(colname + ':N', sort=None),tooltip=[colname, 'Percentage']).transform_calculate(dummy="''")
			# Combine chart and text
			final_chart = (chart).properties()
			col1.altair_chart(final_chart, use_container_width=True)
		else:
			percentages = df[colname].value_counts(normalize=True).mul(100).round(1).reset_index()
			percentages.columns = [colname, 'Percentage']
			col1.altair_chart(alt.Chart(percentages).mark_bar(color="#FF0000").encode(x=alt.X(colname+':N', title=dispname, sort=alt.EncodingSortField(field=colname, op="count", order='descending')), y=alt.Y('Percentage:Q', title='Proportion of ' + dispname), tooltip=[colname, 'Percentage']), use_container_width=True)

	with col2:

		col2.subheader("Proportion of " + dispname)
		percentages = df[colname].value_counts(normalize=True).sort_values(ascending=False).mul(100).reset_index()
		percentages.columns = [colname, 'Percentage']
		chart = alt.Chart(percentages).mark_arc().encode(theta=alt.Theta(field='Percentage', type='quantitative', sort='descending'),color=alt.Color(field=colname, scale = alt.Scale(range=["#696969", "#d3d3d3", "#556b2f", "#228b22", "#7f0000", "#483d8b", "#008b8b", "#4682b4", "#d2691e", "#00008b", "#32cd32", "#8fbc8f", "#8b008b", "#b03060", "#ff4500", "#ffa500", "#ffff00", "#00ff00", "#00fa9a", "#8a2be2", "#dc143c", "#00ffff", "#0000ff", "#f08080", "#adff2f", "#ff00ff", "#1e90ff", "#f0e68c", "#dda0dd", "#ff1493"])),order=alt.Order(field="Value",type="quantitative",sort="descending"),tooltip=[colname, 'Percentage']).interactive()
		col2.altair_chart(chart, use_container_width=True)


def main():

	# Load data
	df = filter_dataframe(showTable("data/metadata.csv").drop("Sample_ID", axis=1))
	# Visualization
	st.header("Data Visualizations")
	dispnames = ["Sample Types", "Genotypes", "Source", "Mutation Types", "Sequencing Types"]

	for i in range(5):
		if i == 1:
			filter = df[df.columns[i]].str.contains("Unknown")
			plotter(df[~filter], df.columns[i], dispnames[i], False)
			continue
		plotter(df, df.columns[i], dispnames[i], True)


	pass



if __name__ == "__main__":
        main()
