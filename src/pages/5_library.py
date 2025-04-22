import sqlite3
import pandas as pd
import streamlit as st

# Funktion til at hente opdateret data fra databasen
def fetch_updated_data():
    # Connect to the SQLite database
    db_path = '/Users/noahfabricius/Desktop/adbis/src/samples.db'
    conn = sqlite3.connect(db_path)

    # SQL query to join the two tables on request_name
    query = """
    SELECT 
        samples.id,
        samples.initialer,
        samples.sample_name,
        samples.eln_number,
        samples.project_name,
        samples.concentration,
        samples.method,
        samples.comment,
        samples.request_name,
        new_table.ELN_M,
        new_table.component,
        new_table.area,
        new_table.date,
        new_table.initialer_m
    FROM 
        samples
    LEFT JOIN 
        new_table
    ON 
        samples.request_name = new_table.request_name
    """

    # Execute the query and load the result into a pandas DataFrame
    df = pd.read_sql_query(query, conn)

    # Remove duplicate rows based on the 'id' column
    df = df.drop_duplicates(subset='id')

    # Close the database connection
    conn.close()

    return df

# Streamlit app
st.title("Library View")

# Hent opdateret data hver gang appen genindlæses
df = fetch_updated_data()

# Create a dropdown menu with unique request_name values
request_names = df['request_name'].dropna().unique()
selected_request_name = st.selectbox("Vælg request_name:", request_names)

# Filter the DataFrame based on the selected request_name
filtered_df = df[df['request_name'] == selected_request_name]

# Display the filtered data
st.dataframe(filtered_df)