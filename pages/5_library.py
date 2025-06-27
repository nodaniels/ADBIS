import sqlite3
import pandas as pd
import streamlit as st
import os
import xlsxwriter
import io

def main():
    with st.sidebar:
        # Always show the Guide link at the top
        st.page_link('main.py', label='🏠 Guide')
        
        # Check location from session state
        if 'location' in st.session_state:
            if st.session_state.location == "Bagsværd 🔵":
                st.page_link('pages/1_createsample.py', label='🔵 Create Sample')
                st.page_link('pages/2_generateqr.py', label='🔵 Generate QR Code')
                st.page_link('pages/3_shippingstatus.py', label='🚐 Shipping Status')
                st.page_link('pages/5_library.py', label='📚 Library')
            
            elif st.session_state.location == "Måløv 🔴":
                st.page_link('pages/3_shippingstatus.py', label='🚐 Shipping Status')
                st.page_link('pages/4_insertresults.py', label='🔴 Insert Results')
                st.page_link('pages/5_library.py', label='📚 Library')
        else:
            st.warning("Please select your location on the main page")
            st.page_link('main.py', label='Go to main page')




# Funktion til at hente opdateret data fra databasen
def fetch_updated_data():
    # Connect to the SQLite database
    db_path = os.path.join(os.path.dirname(__file__), '../samples.db')
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

# Add a button to download the filtered data as an Excel file
# Opret en BytesIO buffer til Excel-filen
excel_buffer = io.BytesIO()

# Brug Pandas ExcelWriter med xlsxwriter som engine
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    filtered_df.to_excel(writer, index=False, sheet_name='Data')
    # writer.save() is not needed as the context manager automatically saves the file

# Sæt bufferens position tilbage til start
excel_buffer.seek(0)

# Dynamisk filnavn baseret på valgt request_name
excel_file_name = f"data_{selected_request_name}.xlsx"

# Tilføj download-knap
st.download_button(
    label="Download som Excel-fil",
    data=excel_buffer,
    file_name=excel_file_name,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

if __name__ == "__main__":
    main()