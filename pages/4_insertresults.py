import sqlite3
import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

st.set_page_config(layout="wide")

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


# Connect to the database
db_path = os.path.join(os.path.dirname(__file__), '../samples.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the new_table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS new_table (
    request_name TEXT,
    ELN_M TEXT,
    component TEXT,
    area REAL,
    date TEXT,
    initialer_m TEXT
)
""")
conn.commit()

# Streamlit app
st.title("Insert Results")

# Fetch distinct request names for the dropdown
cursor.execute("SELECT DISTINCT request_name FROM samples")
request_names = [row[0] for row in cursor.fetchall()]

# Dropdown for selecting a request_name
selected_request_name = st.selectbox("Select a Request Name", request_names)

# Input field for entering the recipient's email
recipient_email = st.text_input("Enter the recipient's email for updates")

def send_email_notification(request_name, initialer_m, recipient_email):
    sender_email = "testinglabmb@gmail.com"  # Din e-mailadresse
    sender_password = "rezrgeiaglpkcnoz"    # Din e-mailadgangskode
    subject = f"Update for Request: {request_name}"
    body = f"Hello, {initialer_m} has updated {request_name} with results from the LC-MS machine.\n\nBest regards,"

    # Opret e-mailen
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send e-mailen
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Brug Gmail SMTP-server
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"E-mail sendt til {recipient_email}")
    except Exception as e:
        print(f"Fejl ved afsendelse af e-mail: {e}")


# Display the filtered results
if selected_request_name:
    query = "SELECT * FROM samples WHERE request_name = ?"
    cursor.execute(query, (selected_request_name,))
    rows = cursor.fetchall()

    # Fetch column names from the database
    column_names = [description[0] for description in cursor.description]

    if rows:
        st.write(f"Results for Request Name: {selected_request_name}")
        # Use pandas to create a DataFrame with column names
        df = pd.DataFrame(data=rows, columns=column_names)

        # Drop the 'id' column if it exists
        if 'id' in df.columns:
            df = df.drop(columns=['id'])

        st.dataframe(df)
        # Add input fields for each row dynamically based on the number of rows
        st.write("Add New Rows")
        new_rows = []

        for i in range(len(rows)):
            st.write(f"Row {i}")
            cols = st.columns(5)  # Create 5 columns for horizontal layout
            with cols[0]:
                new_eln_m = st.text_input(f"ELN_M for Row {i}", key=f"eln_m_{i}")
            with cols[1]:
                new_component = st.text_input(f"Component for Row {i}", key=f"component_{i}")
            with cols[2]:
                new_area = st.text_input(f"Area (%) for Row {i}", key=f"area_{i}")
            with cols[3]:
                new_date = st.date_input(f"Date for Row {i}", key=f"date_{i}")
            with cols[4]:
                new_initialer_m = st.text_input(f"Initialer_M for Row {i}", key=f"initialer_m_{i}")
            new_rows.append((new_eln_m, new_component, new_area, new_date, new_initialer_m))

        if st.button("Insert Rows"):
            # Først slet gamle entries med samme request_name
            delete_query = "DELETE FROM new_table WHERE request_name = ?"
            cursor.execute(delete_query, (selected_request_name,))
    
    # Indsæt de nye rækker
            for eln_m, component, area, date, initialer_m in new_rows:
                if eln_m and component and area and date and initialer_m:  # Sørg for, at alle felter er udfyldt
                    insert_query = """
                    INSERT INTO new_table (request_name, ELN_M, component, area, date, initialer_m)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(insert_query, (selected_request_name, eln_m, component, area, date, initialer_m))
            conn.commit()
            st.success("Rows inserted successfully!")

    # Send e-mail notification
            if recipient_email:
                send_email_notification(selected_request_name, initialer_m, recipient_email)
                st.info(f"E-mail sent to {recipient_email}")
            else:
                st.warning("No recipient email provided. E-mail not sent.")
# Close the connection when the app stops
conn.close()

if __name__ == "__main__":
    main()

